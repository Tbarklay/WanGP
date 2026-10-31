"""REPLACED by review_voices.py: do not use this script.

It left laughter at the start of clips (Whisper base.en word times are loose), cut pieces out of the middle of
speech, and cut real words that Whisper wrote as digits. review_voices.py checks every take with a sound
classifier and Whisper medium.en, trims only the silence around the speech, and re-records bad takes.

Only RATE, load() and save() are still used, by review_voices.py.
"""
import argparse
import difflib
import glob
import os
import re
import subprocess
import sys
import wave

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from build_episode import duration_cap, parse_beats

RATE = 48000
LEAD_IN, TAIL = 0.15, 0.45    # kept before the first and after the last spoken word (Whisper's word ends run early)
JOIN_GAP = 1.0                # pauses up to this long between kept words stay as they are
BRIDGE = 0.35                 # longer gaps (where junk was cut) are shortened to this
JUNK_MIN = 0.6                # extra words lasting at least this long in a row are treated as junk and cut
MIN_MATCH = 0.75              # below this share of script words recognized, the clip is re-recorded
UNITS = "zero one two three four five six seven eight nine ten eleven twelve thirteen fourteen fifteen sixteen " \
        "seventeen eighteen nineteen".split()
TENS = "twenty thirty forty fifty sixty seventy eighty ninety".split()
NUMBERS = {str(n): UNITS[n] if n < 20 else TENS[n // 10 - 2] + (UNITS[n % 10] if n % 10 else "") for n in range(100)}


def norm(word):
    word = re.sub(r"[^a-z0-9']", "", word.lower())
    return NUMBERS.get(word, word)


def similar(a, b):
    return a == b or difflib.SequenceMatcher(a=a, b=b).ratio() >= 0.6


def keep_intervals(script_text, words, duration):
    """Spans of the clip to keep, and the share of script words recognized.

    words: (start, end, text) from speech recognition, in time order. Words Whisper heard slightly
    differently from the script (a name, "M.C.") are kept. Only runs of extra words that last a while,
    like laughter or whispering, plus everything before the first and after the last script word, are cut.
    """
    expected = [w for w in (norm(x) for x in script_text.split()) if w]
    heard = [norm(w[2]) for w in words]
    if not expected or not heard:
        return [], 0.0
    script_like = [False] * len(words)
    recognized = 0
    matcher = difflib.SequenceMatcher(a=expected, b=heard, autojunk=False)
    for tag, a0, a1, b0, b1 in matcher.get_opcodes():
        if tag == "equal":
            recognized += a1 - a0
            script_like[b0:b1] = [True] * (b1 - b0)
        elif tag == "replace":
            for b in range(b0, b1):
                if any(similar(heard[b], expected[a]) for a in range(a0, a1)):
                    script_like[b] = True
                    recognized += 1
    recognized = min(recognized, len(expected))
    script_words = [i for i, k in enumerate(script_like) if k]
    if not script_words:
        return [], 0.0
    first, last = script_words[0], script_words[-1]
    # Between the first and last script word, a run of other words is kept when it is short
    # (a mishearing) and cut when it lasts (laughter, whispering, babble).
    keep = script_like[:]
    b = first
    while b <= last:
        if keep[b]:
            b += 1
            continue
        end = b
        while end <= last and not keep[end]:
            end += 1
        if words[end - 1][1] - words[b][0] < JUNK_MIN:
            keep[b:end] = [True] * (end - b)
        b = end
    kept = [w for w, k in zip(words, keep) if k]
    spans = [[max(0.0, kept[0][0] - LEAD_IN), kept[0][1]]]
    prev_index = None
    for idx, (start, end, _) in enumerate(words):
        if not keep[idx] or idx == first:
            prev_index = idx if keep[idx] else prev_index
            continue
        adjacent = prev_index is not None and all(keep[prev_index:idx + 1])
        if adjacent and start - spans[-1][1] <= JOIN_GAP:
            spans[-1][1] = end
        else:
            spans.append([start - 0.1, end])
        prev_index = idx
    spans[-1][1] = min(duration, spans[-1][1] + TAIL)
    return [tuple(s) for s in spans], recognized / len(expected)


def load(path):
    raw = subprocess.run(["ffmpeg", "-v", "error", "-i", path, "-f", "s16le", "-ac", "1", "-ar", str(RATE), "-"],
                         capture_output=True, check=True).stdout
    return np.frombuffer(raw, dtype=np.int16)


def save(path, samples):
    with wave.open(path, "wb") as f:
        f.setnchannels(1)
        f.setsampwidth(2)
        f.setframerate(RATE)
        f.writeframes(samples.astype(np.int16).tobytes())


def splice(samples, spans):
    silence = np.zeros(int(BRIDGE * RATE), dtype=np.int16)
    pieces = []
    for i, (start, end) in enumerate(spans):
        if i:
            pieces.append(silence)
        piece = samples[int(start * RATE):int(end * RATE)].astype(np.float32)
        fade = min(len(piece) // 2, int(0.01 * RATE))   # 10 ms fades so cuts do not click
        if fade:
            piece[:fade] *= np.linspace(0, 1, fade)
            piece[-fade:] *= np.linspace(1, 0, fade)
        pieces.append(piece.astype(np.int16))
    return np.concatenate(pieces)


def raw_clips(folder, stem):
    return [f for f in glob.glob(os.path.join(folder, stem + "*"))
            if not f.endswith((".json", "_clean.wav"))]


def main():
    sys.exit("clean_voices.py is replaced: run python stories\\tools\\review_voices.py <episode script> instead")
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("script", help="episode script (.md)")
    parser.add_argument("--test", action="store_true", help="clean the --test render")
    parser.add_argument("--model", default="base.en", help="Whisper model (default: base.en)")
    args = parser.parse_args()

    import whisper
    model = whisper.load_model(args.model)

    series = os.path.dirname(args.script)
    ep = os.path.basename(args.script).split("_")[0] + ("_test" if args.test else "")
    beats = parse_beats(args.script)[:3] if args.test else parse_beats(args.script)
    folder = os.path.join(series, "output", ep)
    redo, removed = [], 0.0
    for no, _, narration in beats:
        clips = raw_clips(folder, f"{ep}_vo_{no:02d}")
        if not clips:
            print(f"  beat {no:02d}: no narration clip yet")
            continue
        clip = max(clips, key=os.path.getmtime)
        samples = load(clip)
        duration = len(samples) / RATE
        result = model.transcribe(clip, language="en", word_timestamps=True, condition_on_previous_text=False)
        words = [(w["start"], w["end"], w["word"]) for s in result["segments"] for w in s.get("words", [])]
        spans, score = keep_intervals(narration, words, duration)
        if score < MIN_MATCH:
            redo.append(no)
            print(f"  beat {no:02d}: only {score:.0%} of the script recognized, needs re-recording")
            continue
        if duration >= duration_cap(len(narration.split())) - 0.3:
            redo.append(no)
            print(f"  beat {no:02d}: the clip ran into its length limit, so its last words may be cut off")
            continue
        cleaned = splice(samples, spans)
        save(os.path.splitext(clip)[0] + "_clean.wav", cleaned)
        cut = duration - len(cleaned) / RATE
        removed += cut
        print(f"  beat {no:02d}: {score:.0%} matched, removed {cut:.1f}s")

    print(f"Removed {removed:.0f} seconds of non-script audio in total")
    if redo:
        beats_arg = ",".join(str(n) for n in redo)
        print(f"Re-record these beats ({beats_arg}), then run this cleanup again:\n"
              f"  python stories/tools/build_episode.py {args.script} --beats {beats_arg} --only voices\n"
              f"  python wgp.py --process {os.path.join(series, 'batches', ep.replace('_test', '') + '_redo.json')} "
              f"--output-dir {folder}")


if __name__ == "__main__":
    main()
