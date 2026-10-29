"""Removes whispers, laughter and other sounds the voice model adds around the narration.

Usage (from the WanGP folder, in the WanGP Python environment, after rendering the voices):
    python stories/tools/clean_voices.py stories/debt_hunter/ep01_account_opened.md

Every narration clip is transcribed with Whisper (installed with WanGP). Only the stretches where the
script's own words are spoken are kept; everything before, after and between them that is not in the
script is cut. Each clip is saved next to the original as <name>_clean.wav, which the assembler then
uses. Clips where too little of the script was recognized are listed, with the command to re-record them.
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
from build_episode import parse_beats

RATE = 48000
LEAD_IN, TAIL = 0.12, 0.30    # seconds kept before the first and after the last script word
MAX_GAP = 0.8                 # a longer gap between two script words is shortened to BRIDGE
BRIDGE = 0.30
MIN_MATCH = 0.75              # below this share of script words recognized, the clip is re-recorded


def norm(word):
    return re.sub(r"[^a-z0-9']", "", word.lower())


def keep_intervals(script_text, words, duration):
    """Spans of the clip to keep, and the share of script words recognized.

    words: (start, end, text) from speech recognition, in time order.
    """
    expected = [w for w in (norm(x) for x in script_text.split()) if w]
    heard = [norm(w[2]) for w in words]
    matcher = difflib.SequenceMatcher(a=expected, b=heard, autojunk=False)
    matched = sorted(j for _, b, n in matcher.get_matching_blocks() for j in range(b, b + n))
    if not matched:
        return [], 0.0
    spans = [[max(0.0, words[matched[0]][0] - LEAD_IN), words[matched[0]][1]]]
    for prev, cur in zip(matched, matched[1:]):
        gap = words[cur][0] - words[prev][1]
        if cur == prev + 1 and gap <= MAX_GAP:
            spans[-1][1] = words[cur][1]
        else:
            spans.append([words[cur][0] - 0.05, words[cur][1]])
    spans[-1][1] = min(duration, spans[-1][1] + TAIL)
    return [tuple(s) for s in spans], len(matched) / len(expected)


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
