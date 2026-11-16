"""Makes a follow-along shot where the character does the action exactly where the dropped letters are sung.

BINGO-style songs drop one more letter each round and do an action instead ("CLAP-I-N-G-O"). The video model can't
time an action to a beat, so this cuts it in afterwards from two clips that start and end on the same picture:
  - an idle loop: the farmer and Obi bobbing to the music (rendered with [end: same])
  - one action: a single clap / stomp / pat / jump / bark, about 1 second (rendered with [end: same] [frames: 17])
Wherever a dropped letter is sung, the action clip plays, timed so the clap lands on the sung beat; everywhere else
the idle loop plays on. Because both clips begin and end on the same picture, the cuts don't show.

Usage (from the WanGP folder):
    python obi_shorts/tools/beat_cut.py IDLE.mp4 ACTION.mp4 OUT.mp4 --letters 0.42,0.88,1.31,... --drop 2 --word BINGO --length 6.8
--letters: when each letter is sung, in seconds from the start of the shot, all repetitions in order (from Whisper word
timestamps or the beat grid). --drop: how many letters at the start of each repetition are replaced by the action.
--length: how long the finished shot must be. --hit: where in the action clip the clap lands, as a fraction of the
clip (default 0.5).
"""
import argparse
import os
import shutil
import subprocess
import sys


def tool(name):
    local = os.path.join("ffmpeg_bins", name + (".exe" if os.name == "nt" else ""))
    return local if os.path.isfile(local) else (shutil.which(name) or sys.exit(f"{name} not found"))


def duration(path):
    return float(subprocess.run([tool("ffprobe"), "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0",
                                 path], capture_output=True, text=True, check=True).stdout)


def plan(letters, word_len, drop, length, action_len, hit):
    """[(start, end, 'idle' | 'action')] covering 0..length: each dropped letter gets the action clip, retimed so its
    hit moment lands on the sung letter; the rest is idle."""
    pieces, t = [], 0.0
    for i, at in enumerate(letters):
        if i % word_len >= drop:
            continue
        # one letter's worth of time, placed so the action's hit moment lands exactly on the sung letter
        gap = (letters[i + 1] - at) if i + 1 < len(letters) else (at - letters[i - 1] if i else 0.5)
        span = max(0.25, min(gap, 1.2))
        start = max(t, at - hit * span)
        end = min(length, at + (1 - hit) * span)
        if start > t + 0.02:
            pieces.append((t, start, "idle"))
        pieces.append((start, end, "action"))
        t = end
    if t < length - 0.02:
        pieces.append((t, length, "idle"))
    return pieces


def main():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("idle")
    p.add_argument("action")
    p.add_argument("out")
    p.add_argument("--letters", required=True, help="comma-separated times (s) of every sung letter")
    p.add_argument("--drop", type=int, required=True)
    p.add_argument("--word", default="BINGO")
    p.add_argument("--length", type=float, required=True)
    p.add_argument("--hit", type=float, default=0.5)
    args = p.parse_args()

    letters = [float(x) for x in args.letters.split(",") if x.strip()]
    action_len = duration(args.action)
    pieces = plan(letters, len(args.word), args.drop, args.length, action_len, args.hit)
    n_idle = sum(1 for *_, kind in pieces if kind == "idle")
    n_action = len(pieces) - n_idle
    common = "fps=30,scale=1920:1080:force_original_aspect_ratio=increase:flags=lanczos,crop=1920:1080,setsar=1"
    chains = [f"[0:v]{common},split={max(n_idle, 1)}" + "".join(f"[i{k}]" for k in range(max(n_idle, 1))),
              f"[1:v]{common},split={max(n_action, 1)}" + "".join(f"[a{k}]" for k in range(max(n_action, 1)))]
    labels, ki, ka = [], 0, 0
    for k, (start, end, kind) in enumerate(pieces):
        if kind == "idle":
            # the idle loop keeps running in real time underneath, so its motion carries on across the actions
            chains.append(f"[i{ki}]trim=start={start:.3f}:end={end:.3f},setpts=PTS-STARTPTS[s{k}]")
            ki += 1
        else:
            stretch = (end - start) / action_len
            chains.append(f"[a{ka}]setpts={stretch:.4f}*(PTS-STARTPTS),fps=30,trim=end={end - start:.3f},"
                          f"setpts=PTS-STARTPTS[s{k}]")
            ka += 1
        labels.append(f"[s{k}]")
    for k in range(ki, max(n_idle, 1)):
        chains.append(f"[i{k}]nullsink")
    for k in range(ka, max(n_action, 1)):
        chains.append(f"[a{k}]nullsink")
    chains.append("".join(labels) + f"concat=n={len(labels)}:v=1:a=0[v]")
    subprocess.run([tool("ffmpeg"), "-y", "-v", "error", "-stream_loop", "-1", "-i", args.idle, "-i", args.action,
                    "-filter_complex", ";".join(chains), "-map", "[v]", "-t", f"{args.length:.3f}",
                    "-c:v", "libx264", "-preset", "medium", "-crf", "17", "-pix_fmt", "yuv420p", args.out], check=True)
    for start, end, kind in pieces:
        print(f"  {start:5.2f}-{end:5.2f}  {kind}")
    print(f"Wrote {args.out} ({args.length:.2f} s, {n_action} actions on the dropped letters)")


if __name__ == "__main__":
    main()
