"""Picks a clean narration take for every beat: no laughing, gasping or whispering, and no chopped words.

Usage (from the WanGP folder, in the WanGP Python environment, after rendering the voices):
    python stories/tools/review_voices.py stories/debt_hunter/ep01_account_opened.md
    python stories/tools/review_voices.py stories/debt_hunter/ep01_account_opened.md --rounds 3 --takes 4
    python stories/tools/review_voices.py stories/debt_hunter/ep01_account_opened.md --beats 4,21,63
    python stories/tools/review_voices.py stories/debt_hunter/ep01_account_opened.md --test   # the 3-beat test render
Needs ffmpeg on PATH (WanGP's ffmpeg_bins folder). It runs wgp.py itself to re-record bad takes.

Every narration take of every beat in output/<ep> is checked:
  * an AudioSet sound classifier (AST) listens for laughter, snickering, gasps and whispering,
  * Whisper (medium.en) checks that the whole script is spoken, with confident (not garbled) words.
The take is only trimmed before the first and after the last word, at real silence, never inside the speech,
so no words are chopped. Beats without a clean take are re-recorded with new seeds and checked again.
The chosen take is saved as <ep>_vo_NN_pick.wav with its trimmed <ep>_vo_NN_pick_clean.wav, which the
assembler then uses. Beats that never got a clean take keep their best one and are listed at the end.
"""
import argparse
import difflib
import glob
import json
import os
import re
import shutil
import subprocess
import sys

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from build_episode import duration_cap, parse_beats, voice_task
from clean_voices import RATE, load, save

LAUGH = ("Laughter", "Giggle", "Chuckle, chortle", "Snicker", "Belly laugh", "Baby laughter")
LAUGH_MAX = 0.12          # any laughter class above this anywhere in the trimmed take fails it
GASP_MAX = 0.42           # gasps and whispering above this fail it (normal breaths score about 0.2)
LOW_WORD = 0.3            # a script word heard with less confidence than this counts as garbled
MAX_LOW = 1               # unclear words allowed per take (names are often heard with low confidence)
MAX_EXTRA = 1             # words that are not in the script allowed per take (a misheard name)
MIN_COVER = 0.9           # share of the script that must be heard
LEAD, TAIL = 0.12, 0.35   # silence kept before the first and after the last word
SEED_BASE = 5000

UNITS = ("zero one two three four five six seven eight nine ten eleven twelve thirteen fourteen fifteen "
         "sixteen seventeen eighteen nineteen").split()
TENS = "twenty thirty forty fifty sixty seventy eighty ninety".split()


def spell(n):
    if n < 20:
        return [UNITS[n]]
    if n < 100:
        return [TENS[n // 10 - 2]] + ([UNITS[n % 10]] if n % 10 else [])
    for size, name in ((10 ** 9, "billion"), (10 ** 6, "million"), (1000, "thousand"), (100, "hundred")):
        if n >= size:
            return spell(n // size) + [name] + (spell(n % size) if n % size else [])


def words_of(text):
    """Normalized words, with digits spelled out ("1,072" -> one thousand seventy two) and "and" dropped."""
    out = []
    for raw in re.split(r"[\s\-]+", text.lower()):
        raw = raw.strip(".,!?;:\"'()[]…")
        if re.fullmatch(r"\d[\d,]*", raw):
            out += spell(int(raw.replace(",", "")))
        else:
            word = re.sub(r"[^a-z0-9']", "", raw)
            if word:
                out.append(word)
    return [w for w in out if w != "and"]


class Judge:
    def __init__(self):
        import torch
        import whisper
        from transformers import ASTFeatureExtractor, ASTForAudioClassification
        name = "MIT/ast-finetuned-audioset-10-10-0.4593"
        self.torch = torch
        self.fe = ASTFeatureExtractor.from_pretrained(name)
        self.ast = ASTForAudioClassification.from_pretrained(name).cuda().eval()
        idx = {v: k for k, v in self.ast.config.id2label.items()}
        self.classes = {c: idx[c] for c in LAUGH + ("Gasp", "Whispering") if c in idx}
        self.whisper = whisper.load_model("medium.en")

    def sounds(self, samples, win=0.5, hop=0.25):
        """Highest laughter score and highest gasp/whisper score over half-second windows
        (longer windows average a short gasp away)."""
        import librosa
        y = librosa.resample(samples.astype(np.float32) / 32768, orig_sr=RATE, target_sr=16000)
        starts = np.arange(0, max(len(y) / 16000 - win, 0) + 1e-6, hop)
        chunks = [y[int(s * 16000):int((s + win) * 16000)] for s in starts]
        laugh = gasp = 0.0
        for i in range(0, len(chunks), 32):
            feats = self.fe(chunks[i:i + 32], sampling_rate=16000, return_tensors="pt")["input_values"].cuda()
            with self.torch.no_grad():
                p = self.torch.sigmoid(self.ast(feats).logits).cpu().numpy()
            for row in p:
                laugh = max(laugh, max(row[self.classes[c]] for c in LAUGH if c in self.classes))
                gasp = max(gasp, max(row[self.classes[c]] for c in ("Gasp", "Whispering") if c in self.classes))
        return float(laugh), float(gasp)

    def words(self, path):
        r = self.whisper.transcribe(path, language="en", word_timestamps=True, condition_on_previous_text=False)
        return [x for s in r["segments"] for x in s["words"]], r["text"].strip()


def coverage(script, heard_words):
    """Share of script words heard, and the indexes of the heard words that belong to the script."""
    expected = words_of(script)
    heard, owner = [], []
    for i, w in enumerate(heard_words):
        for part in words_of(w["word"]):
            heard.append(part)
            owner.append(i)
    m = difflib.SequenceMatcher(a=expected, b=heard, autojunk=False)
    hit, used = 0, set()
    for tag, a0, a1, b0, b1 in m.get_opcodes():
        if tag == "equal":
            hit += a1 - a0
            used.update(owner[b0:b1])
        elif tag == "replace":
            for b in range(b0, b1):
                if any(difflib.SequenceMatcher(a=heard[b], b=expected[a]).ratio() >= 0.6 for a in range(a0, a1)):
                    hit += 1
                    used.add(owner[b])
    return min(hit, len(expected)) / max(len(expected), 1), sorted(used)


def quiet_point(samples, t, direction, limit):
    """The quietest moment within `limit` seconds of t, searching backward (-1) or forward (+1)."""
    frame = int(0.02 * RATE)
    a, b = (t - limit, t) if direction < 0 else (t, t + limit)
    a, b = max(0, int(a * RATE)), min(len(samples), int(b * RATE))
    if b - a < frame:
        return t
    x = samples[a:b].astype(np.float32)
    energy = [np.sqrt(np.mean(x[i:i + frame] ** 2)) for i in range(0, len(x) - frame + 1, frame)]
    quiet = max(energy) * 0.08
    order = range(len(energy) - 1, -1, -1) if direction < 0 else range(len(energy))
    for i in order:   # the first quiet frame next to the word, or the quietest one
        if energy[i] <= quiet:
            return (a + i * frame + frame / 2) / RATE
    return (a + int(np.argmin(energy)) * frame + frame / 2) / RATE


def trim(samples, words, used):
    start = words[used[0]]["start"]
    end = words[used[-1]]["end"]
    start = max(0.0, quiet_point(samples, start, -1, 0.35) - LEAD)
    end = min(len(samples) / RATE, quiet_point(samples, end, +1, 0.6) + TAIL)
    piece = samples[int(start * RATE):int(end * RATE)].astype(np.float32)
    fade = int(0.01 * RATE)
    piece[:fade] *= np.linspace(0, 1, fade)
    piece[-fade:] *= np.linspace(1, 0, fade)
    return piece.astype(np.int16)


def judge_take(judge, path, script, cap, work):
    samples = load(path)
    if len(samples) / RATE >= cap - 0.3:
        return {"ok": False, "why": "ran into its length limit", "score": -9}
    words, _ = judge.words(path)
    if not words:
        return {"ok": False, "why": "no speech heard", "score": -9}
    cover, used = coverage(script, words)
    if not used:
        return {"ok": False, "why": "script not heard", "score": -9}
    trimmed = trim(samples, words, used)
    tmp = os.path.join(work, "trial.wav")
    save(tmp, trimmed)
    # Judge the trimmed take as it will sound in the video.
    laugh, gasp = judge.sounds(trimmed)
    words2, heard = judge.words(tmp)
    cover2, used2 = coverage(script, words2)
    # ("and" is left out of the comparison, since "three hundred and twelve" is heard as "312")
    spoken = [(i, w) for i, w in enumerate(words2) if words_of(w["word"])]
    # Garbled or chopped speech shows up as words Whisper is unsure of, or words that are not in the script.
    low = [w["word"].strip() for i, w in spoken if w["probability"] < LOW_WORD]
    extra = [w["word"].strip() for i, w in spoken if i not in used2]
    why = []
    if min(cover, cover2) < MIN_COVER:
        why.append(f"only {min(cover, cover2):.0%} of the script heard")
    if laugh > LAUGH_MAX:
        why.append(f"laughing ({laugh:.2f})")
    if gasp > GASP_MAX:
        why.append(f"gasp or whisper ({gasp:.2f})")
    if len(low) > MAX_LOW:
        why.append(f"unclear words {low}")
    if len(extra) > MAX_EXTRA:
        why.append(f"words not in the script {extra}")
    mean_p = float(np.mean([w["probability"] for _, w in spoken])) if spoken else 0
    score = mean_p - laugh - 0.5 * gasp - 0.1 * (len(low) + len(extra)) + min(cover, cover2)
    detail = f"laugh {laugh:.2f} gasp {gasp:.2f} words p {mean_p:.2f} low {low} extra {extra}"
    return {"ok": not why, "why": ("; ".join(why) or "clean") + f"  [{detail}]", "score": score,
            "trimmed": trimmed, "heard": heard, "laugh": laugh, "gasp": gasp, "low": low}


def takes(folder, stem):
    return [f for f in glob.glob(os.path.join(folder, stem + "*.wav"))
            if not f.endswith("_clean.wav") and "_pick" not in os.path.basename(f)]


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("script", help="episode script (.md)")
    parser.add_argument("--rounds", type=int, default=3, help="re-recording rounds for beats without a clean take")
    parser.add_argument("--takes", type=int, default=4, help="new takes per beat in each round")
    parser.add_argument("--beats", help="only these beats, comma separated")
    parser.add_argument("--test", action="store_true", help="review the --test render (first 3 beats)")
    args = parser.parse_args()

    series = os.path.dirname(args.script)
    ep = os.path.basename(args.script).split("_")[0] + ("_test" if args.test else "")
    folder = os.path.join(series, "output", ep)
    work = os.path.join(series, "output", ep + "_review")
    os.makedirs(work, exist_ok=True)
    cast = json.load(open(os.path.join(series, "cast.json"), encoding="utf-8"))
    beats = parse_beats(args.script)[:3] if args.test else parse_beats(args.script)
    if args.beats:
        wanted = {int(b) for b in args.beats.split(",")}
        beats = [b for b in beats if b[0] in wanted]
    judge = Judge()
    seen, best = {}, {}

    def review(todo):
        for no, _, text in todo:
            cap = duration_cap(len(text.split()))
            for path in takes(folder, f"{ep}_vo_{no:02d}"):
                if path in seen.get(no, set()):
                    continue
                seen.setdefault(no, set()).add(path)
                r = judge_take(judge, path, text, cap, work)
                print(f"  beat {no:02d} {os.path.basename(path)}: {r['why']}", flush=True)
                if "trimmed" in r and (no not in best or (r["ok"], r["score"]) > (best[no][1]["ok"], best[no][1]["score"])):
                    best[no] = (path, r)

    print("Checking every existing take...", flush=True)
    review(beats)
    for round_no in range(1, args.rounds + 1):
        todo = [b for b in beats if not (b[0] in best and best[b[0]][1]["ok"])]
        if not todo:
            break
        print(f"Round {round_no}: re-recording {len(todo)} beats ({','.join(str(b[0]) for b in todo)}), "
              f"{args.takes} takes each", flush=True)
        tasks = []
        for no, _, text in todo:
            for k in range(args.takes):
                offset = SEED_BASE + round_no * 100 + k
                task = voice_task(cast, ep, no, text, offset)
                task["output_filename"] = f"{ep}_vo_{no:02d}_s{offset}"
                tasks.append(task)
        batch = os.path.join(series, "batches", f"{ep}_review_round{round_no}.json")
        with open(batch, "w", encoding="utf-8") as f:
            json.dump(tasks, f, indent=2)
        subprocess.run([sys.executable, "wgp.py", "--process", batch, "--output-dir", folder], check=True)
        review(todo)

    failed = []
    for no, _, _ in beats:
        if no not in best:
            failed.append((no, "no usable take"))
            continue
        path, r = best[no]
        pick = os.path.join(folder, f"{ep}_vo_{no:02d}_pick.wav")
        shutil.copyfile(path, pick)
        save(os.path.splitext(pick)[0] + "_clean.wav", r["trimmed"])
        if not r["ok"]:
            failed.append((no, r["why"]))
    print(f"Picked a take for {len(beats) - sum(1 for _, w in failed if w == 'no usable take')} beats.")
    if failed:
        print("No fully clean take for these beats (the best one is used):")
        for no, why in failed:
            print(f"  beat {no:02d}: {why}")
    else:
        print("Every beat has a clean take.")


if __name__ == "__main__":
    main()
