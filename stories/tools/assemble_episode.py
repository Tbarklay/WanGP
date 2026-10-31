"""Turns an episode's rendered images and narration clips into the finished video.

Usage (from the WanGP folder, after the overnight render):
    python stories/tools/assemble_episode.py stories/debt_hunter/ep01_account_opened.md
    python stories/tools/assemble_episode.py stories/debt_hunter/ep01_account_opened.md --music path/to/music.mp3

Each image stays on screen for its narration plus a short pause, with a slow zoom or pan.
Writes stories/<series>/final/<ep>.mp4 and <ep>.srt (captions to upload to YouTube).
"""
import argparse
import glob
import os
import shutil
import subprocess
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from build_episode import parse_beats

WIDTH, HEIGHT, FPS = 1920, 1080, 30
PAUSE = 0.35            # silence after each narration line
MUSIC_VOLUME = 0.10     # background music level under the narrator
LOUDNESS = "loudnorm=I=-14:TP=-1.5:LRA=11"   # YouTube's playback loudness, so the narrator is not quiet
MOVES = ["zoom_in", "pan_right", "zoom_out", "pan_left"]


def tool(name):
    local = os.path.join("ffmpeg_bins", name + (".exe" if os.name == "nt" else ""))
    if os.path.isfile(local):
        return local
    found = shutil.which(name)
    if found is None:
        sys.exit(f"{name} not found. Launch WanGP once (it downloads ffmpeg) or install ffmpeg.")
    return found


def run(cmd):
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        sys.exit(f"ffmpeg failed:\n{result.stderr[-2000:]}")


def duration(path):
    out = subprocess.run([tool("ffprobe"), "-v", "error", "-show_entries", "format=duration",
                          "-of", "default=nw=1:nk=1", path], capture_output=True, text=True, check=True)
    return float(out.stdout.strip())


def newest(folder, stem):
    files = [f for f in glob.glob(os.path.join(folder, stem + "*")) if not f.endswith((".json", "_clean.wav"))]
    return max(files, key=os.path.getmtime) if files else None


def voice_clip(folder, stem):
    """The newest narration clip, or its cleaned version from clean_voices.py when that is up to date."""
    raw = newest(folder, stem)
    if raw is None:
        return None
    clean = os.path.splitext(raw)[0] + "_clean.wav"
    return clean if os.path.isfile(clean) and os.path.getmtime(clean) >= os.path.getmtime(raw) else raw


def motion(move, frames):
    """zoompan expressions for one slow camera move over the whole shot."""
    t = f"(on/{max(frames - 1, 1)})"
    if move == "zoom_in":
        z, x, y = f"1+0.12*{t}", "(iw-iw/zoom)/2", "(ih-ih/zoom)/2"
    elif move == "zoom_out":
        z, x, y = f"1.12-0.12*{t}", "(iw-iw/zoom)/2", "(ih-ih/zoom)/2"
    elif move == "pan_right":
        z, x, y = "1.12", f"(iw-iw/zoom)*{t}", "(ih-ih/zoom)/2"
    else:
        z, x, y = "1.12", f"(iw-iw/zoom)*(1-{t})", "(ih-ih/zoom)/2"
    return (f"scale={WIDTH * 2}:{HEIGHT * 2}:force_original_aspect_ratio=increase,crop={WIDTH * 2}:{HEIGHT * 2},"
            f"zoompan=z='{z}':x='{x}':y='{y}':d={frames}:s={WIDTH}x{HEIGHT}:fps={FPS},format=yuv420p")


def srt_time(seconds):
    ms = round(seconds * 1000)
    return f"{ms // 3600000:02d}:{ms // 60000 % 60:02d}:{ms // 1000 % 60:02d},{ms % 1000:03d}"


def caption_chunks(text, max_chars=42):
    chunks, line = [], ""
    for word in text.split():
        if line and len(line) + 1 + len(word) > max_chars:
            chunks.append(line)
            line = word
        else:
            line = f"{line} {word}".strip()
    return chunks + [line] if line else chunks


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("script", help="episode script (.md)")
    parser.add_argument("--music", help="background music file, looped under the narration")
    parser.add_argument("--test", action="store_true", help="assemble the --test render")
    args = parser.parse_args()

    series = os.path.dirname(args.script)
    ep = os.path.basename(args.script).split("_")[0] + ("_test" if args.test else "")
    beats = parse_beats(args.script)[:3] if args.test else parse_beats(args.script)
    rendered = os.path.join(series, "output", ep)
    work = os.path.join(series, "output", ep + "_segments")
    final_dir = os.path.join(series, "final")
    os.makedirs(work, exist_ok=True)
    os.makedirs(final_dir, exist_ok=True)

    segments, captions, clock, missing = [], [], 0.0, []
    for i, (no, _, narration) in enumerate(beats):
        image = newest(rendered, f"{ep}_img_{no:02d}")
        voice = voice_clip(rendered, f"{ep}_vo_{no:02d}")
        if image is None or voice is None:
            missing.append(no)
            continue
        length = duration(voice) + PAUSE
        frames = max(1, round(length * FPS))
        length = frames / FPS   # whole frames, so sound and picture stay in step across all segments
        # Uncompressed audio in the segments: AAC adds a little padding to every segment, which builds
        # up over an episode and puts the narration behind the pictures. It is compressed once at the end.
        segment = os.path.join(work, f"seg_{no:02d}.mkv")
        run([tool("ffmpeg"), "-y", "-loop", "1", "-i", image, "-i", voice,
             "-filter_complex", f"[0:v]{motion(MOVES[i % len(MOVES)], frames)}[v];"
                                f"[1:a]aresample=48000,apad=whole_dur={length:.3f}[a]",
             "-map", "[v]", "-map", "[a]", "-frames:v", str(frames), "-t", f"{length:.3f}",
             "-c:v", "libx264", "-preset", "veryfast", "-crf", "18",
             "-c:a", "pcm_s16le", "-ar", "48000", "-ac", "2", segment])
        segments.append(segment)

        chunks = caption_chunks(narration)
        speech = length - PAUSE
        words = sum(len(c.split()) for c in chunks)
        start = clock
        for chunk in chunks:
            end = start + speech * len(chunk.split()) / words
            captions.append((start, end, chunk))
            start = end
        clock += length
        print(f"  beat {no:02d}: {length:.1f}s")

    if missing:
        print(f"WARNING: beats {missing} have no image or narration yet and were left out")
    if not segments:
        sys.exit(f"Nothing to assemble in {rendered}")

    listing = os.path.join(work, "segments.txt")
    with open(listing, "w", encoding="utf-8") as f:
        f.writelines(f"file '{os.path.abspath(s)}'\n" for s in segments)
    joined = os.path.join(work, "joined.mkv")
    run([tool("ffmpeg"), "-y", "-f", "concat", "-safe", "0", "-i", listing, "-c", "copy", joined])

    out = os.path.join(final_dir, f"{ep}.mp4")
    if args.music:
        run([tool("ffmpeg"), "-y", "-i", joined, "-stream_loop", "-1", "-i", args.music,
             "-filter_complex", f"[1:a]volume={MUSIC_VOLUME},afade=t=out:st={max(clock - 3, 0):.2f}:d=3[m];"
                                f"[0:a][m]amix=inputs=2:duration=first:normalize=0,{LOUDNESS}[a]",
             "-map", "0:v", "-map", "[a]", "-c:v", "copy", "-c:a", "aac", "-b:a", "192k", out])
    else:
        run([tool("ffmpeg"), "-y", "-i", joined, "-af", LOUDNESS, "-c:v", "copy",
             "-c:a", "aac", "-b:a", "192k", "-ar", "48000", out])

    with open(os.path.join(final_dir, f"{ep}.srt"), "w", encoding="utf-8") as f:
        for n, (start, end, text) in enumerate(captions, 1):
            f.write(f"{n}\n{srt_time(start)} --> {srt_time(end)}\n{text}\n\n")
    print(f"Wrote {out} ({clock / 60:.1f} minutes) and its captions {ep}.srt")


if __name__ == "__main__":
    main()
