"""Joins the rendered clips and the song into the finished YouTube videos.

Usage (from the WanGP folder, after the overnight render):
    python kids_videos/merge.py old_macdonald          # uses song take "a"
    python kids_videos/merge.py old_macdonald b        # uses song take "b"
    python kids_videos/merge.py all

Writes kids_videos/final/<song>_long.mp4 and <song>_short.mp4.
The clips are sped up or slowed down slightly so the video ends with the song.
"""
import glob
import os
import shutil
import subprocess
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from songs import SONGS

OUTPUT_DIR = "kids_videos/output"
FINAL_DIR = "kids_videos/final"
MIN_SPEED, MAX_SPEED = 0.8, 1.25   # outside this range, hold the last frame or cut instead
FPS = 30


def tool(name):
    local = os.path.join("ffmpeg_bins", name + (".exe" if os.name == "nt" else ""))
    if os.path.isfile(local):
        return local
    found = shutil.which(name)
    if found is None:
        sys.exit(f"{name} not found. Launch WanGP once (it downloads ffmpeg) or install ffmpeg.")
    return found


def duration(path):
    out = subprocess.run([tool("ffprobe"), "-v", "error", "-show_entries", "format=duration",
                          "-of", "default=nw=1:nk=1", path], capture_output=True, text=True, check=True)
    return float(out.stdout.strip())


def newest(pattern):
    files = [f for f in glob.glob(os.path.join(OUTPUT_DIR, pattern)) if not f.endswith(".json")]
    return max(files, key=os.path.getmtime) if files else None


def merge(slug, take):
    song = SONGS[slug]
    audio = newest(f"{slug}_song_{take}.*") or newest(f"{slug}_song_{take}*")
    if audio is None:
        print(f"[{slug}] song take '{take}' not found in {OUTPUT_DIR}, skipping")
        return
    song_len = duration(audio)
    os.makedirs(FINAL_DIR, exist_ok=True)

    for fmt, size in (("long", "832:480"), ("short", "480:832")):
        clips = []
        for no in range(1, len(song["shots"]) + 1):
            clip = newest(f"{slug}_{fmt}_{no:02d}.*") or newest(f"{slug}_{fmt}_{no:02d}_*")
            if clip is None:
                print(f"[{slug}] missing {fmt} clip {no:02d}, it will be left out")
            else:
                clips.append(clip)
        if not clips:
            print(f"[{slug}] no {fmt} clips found, skipping")
            continue

        clips_len = sum(duration(c) for c in clips)
        speed = min(max(clips_len / song_len, MIN_SPEED), MAX_SPEED)
        inputs, chains = [], []
        for i, clip in enumerate(clips):
            inputs += ["-i", clip]
            chains.append(f"[{i}:v]scale={size}:force_original_aspect_ratio=decrease,"
                          f"pad={size}:(ow-iw)/2:(oh-ih)/2,setsar=1,fps={FPS}[v{i}]")
        concat = "".join(f"[v{i}]" for i in range(len(clips)))
        chains.append(f"{concat}concat=n={len(clips)}:v=1:a=0[cat]")
        # Fit the clips to the song, then hold the last frame if they still run short.
        chains.append(f"[cat]setpts=PTS/{speed:.4f},fps={FPS},tpad=stop_mode=clone:stop_duration={song_len:.2f}[out]")

        out_path = os.path.join(FINAL_DIR, f"{slug}_{fmt}.mp4")
        cmd = [tool("ffmpeg"), "-y", *inputs, "-i", audio,
               "-filter_complex", ";".join(chains),
               "-map", "[out]", "-map", f"{len(clips)}:a",
               "-c:v", "libx264", "-preset", "medium", "-crf", "18", "-pix_fmt", "yuv420p",
               "-c:a", "aac", "-b:a", "192k", "-t", f"{song_len:.2f}", out_path]
        print(f"[{slug}] {fmt}: {len(clips)} clips ({clips_len:.0f}s) fitted to song ({song_len:.0f}s), speed x{speed:.2f}")
        subprocess.run(cmd, check=True, capture_output=True)
        print(f"[{slug}] wrote {out_path}")


def main():
    if len(sys.argv) not in (2, 3) or (sys.argv[1] != "all" and sys.argv[1] not in SONGS):
        print(f"Usage: python kids_videos/merge.py <{'|'.join(SONGS)}|all> [song take a/b/c]")
        sys.exit(1)
    take = sys.argv[2] if len(sys.argv) == 3 else "a"
    for slug in (SONGS if sys.argv[1] == "all" else [sys.argv[1]]):
        merge(slug, take)


if __name__ == "__main__":
    main()
