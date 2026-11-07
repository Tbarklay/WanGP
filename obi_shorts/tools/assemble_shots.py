"""Joins the animated clips of a shot list into one 1080p video, with optional music.

Usage (from the WanGP folder, after the clips are rendered):
    python obi_shorts/tools/assemble_shots.py obi_shorts/test_shots.md
    python obi_shorts/tools/assemble_shots.py obi_shorts/test_shots.md --music path/to/music.mp3
    python obi_shorts/tools/assemble_shots.py obi_shorts/obi_farm_parade.md --song b   # use song take b

With a song (rendered by build_shots.py song), the clips are sped up or slowed down slightly so the
video ends with the song; plain --music is faded out at the end of the clips instead.

Writes obi_shorts/final/<shot list name>.mp4 (16:9) and <name>_short.mp4 (9:16, center crop for Shorts).
"""
import argparse
import glob
import os
import shutil
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from build_shots import parse_extras, parse_shots

LOUDNESS = "loudnorm=I=-14:TP=-1.5:LRA=11"
SFX_VOLUME = 1.6        # sound effects sit clearly above the song
COUNT_SIZE = 420        # height of the on-screen counting numbers, in pixels at 1080p


def number_png(folder, n):
    """A big friendly number with a thick dark outline, as a transparent PNG."""
    from PIL import Image, ImageDraw, ImageFont
    path = os.path.join(folder, f"count_{n}.png")
    if os.path.isfile(path):
        return path
    font = None
    for name in ("arialbd.ttf", "Arial Bold.ttf", "DejaVuSans-Bold.ttf", "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"):
        try:
            font = ImageFont.truetype(name, COUNT_SIZE)
            break
        except OSError:
            continue
    font = font or ImageFont.load_default()
    img = Image.new("RGBA", (COUNT_SIZE * 2, COUNT_SIZE + 120), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    text = str(n)
    w = draw.textlength(text, font=font)
    draw.text(((img.width - w) / 2, 20), text, font=font, fill=(255, 214, 10),
              stroke_width=COUNT_SIZE // 14, stroke_fill=(40, 30, 80))
    img.save(path)
    return path


def count_values(value):
    """'3' -> [3]; '1-4' -> [1, 2, 3, 4]."""
    first, _, last = value.partition("-")
    return list(range(int(first), int(last or first) + 1))
MUSIC_VOLUME = 0.6


def tool(name):
    local = os.path.join("ffmpeg_bins", name + (".exe" if os.name == "nt" else ""))
    return local if os.path.isfile(local) else (shutil.which(name) or sys.exit(f"{name} not found"))


def run(cmd):
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        sys.exit(f"ffmpeg failed:\n{result.stderr[-2000:]}")


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("script", help="shot list (.md)")
    parser.add_argument("--music", help="music file, faded out at the end")
    parser.add_argument("--song", help="song take (a, b or c) rendered by build_shots.py song; the clips follow its length")
    args = parser.parse_args()

    name = os.path.splitext(os.path.basename(args.script))[0]
    folder = os.path.join(ROOT, "output", name)
    clips, missing = [], []
    for no, _, _ in parse_shots(args.script):
        found = glob.glob(os.path.join(folder, f"{name}_clip_{no:02d}*"))
        if found:
            clips.append(max(found, key=os.path.getmtime))
        else:
            missing.append(no)
    if missing:
        print(f"WARNING: shots {missing} have no clip yet and were left out")
    if not clips:
        sys.exit(f"No clips in {folder}")

    durations = [float(subprocess.run([tool("ffprobe"), "-v", "error", "-show_entries", "format=duration",
                                       "-of", "csv=p=0", c], capture_output=True, text=True).stdout) for c in clips]
    total, speed = sum(durations), 1.0
    if args.song:
        found = glob.glob(os.path.join(folder, f"{name}_song_{args.song}*"))
        if not found:
            sys.exit(f"Song take {args.song} not found in {folder}")
        args.music = max(found, key=os.path.getmtime)
        song_len = float(subprocess.run([tool("ffprobe"), "-v", "error", "-show_entries", "format=duration",
                                         "-of", "csv=p=0", args.music], capture_output=True, text=True).stdout)
        speed = min(max(total / song_len, 0.85), 1.15)   # beyond 15% the motion looks wrong; hold the last frame
        total = song_len

    final = os.path.join(ROOT, "final")
    os.makedirs(final, exist_ok=True)
    inputs, chains = [], []
    for i, clip in enumerate(clips):
        inputs += ["-i", clip]
        chains.append(f"[{i}:v]scale=1920:1080:force_original_aspect_ratio=increase:flags=lanczos,"
                      f"crop=1920:1080,fps=30,setsar=1[v{i}]")
    chains.append("".join(f"[v{i}]" for i in range(len(clips))) + f"concat=n={len(clips)}:v=1:a=0[cat]")
    chains.append(f"[cat]setpts=PTS/{speed:.4f},fps=30,tpad=stop_mode=clone:stop_duration={total:.2f},"
                  f"trim=0:{total:.2f}[v]")
    # Where each shot starts in the finished video, for its counting numbers and sound effects.
    extras = parse_extras(args.script)
    starts, t = {}, 0.0
    for (no, _, _), dur in zip([s for s in parse_shots(args.script) if s[0] not in missing], durations):
        starts[no] = (t / speed, dur / speed)
        t += dur
    overlays, effects = [], []
    work = os.path.join(folder, "_assemble")
    os.makedirs(work, exist_ok=True)
    for no, items in extras.items():
        if no not in starts:
            continue
        start, length = starts[no]
        for kind, value in items:
            if kind == "count":
                numbers = count_values(value)
                step = length / len(numbers)
                for k, n in enumerate(numbers):
                    overlays.append((number_png(work, n), start + k * step + 0.15, start + (k + 1) * step - 0.05))
            else:
                effect, _, offset = value.partition("@")
                found = glob.glob(os.path.join(folder, f"{name}_sfx_{effect.strip()}_*"))
                if not found:
                    print(f"WARNING: sound effect '{effect.strip()}' not rendered yet (build_shots.py sfx), skipped")
                    continue
                effects.append((sorted(found)[0], start + float(offset or 0)))

    cmd = [tool("ffmpeg"), "-y", *inputs]
    next_input = len(clips)
    if overlays:
        chains[-1] = chains[-1].replace("[v]", "[base0]")
        for k, (png, a, b) in enumerate(overlays):
            cmd += ["-i", png]
            fade = f"fade=t=in:st={a:.2f}:d=0.15:alpha=1,fade=t=out:st={b - 0.15:.2f}:d=0.15:alpha=1"
            chains.append(f"[{next_input}:v]loop=-1:1:0,setpts=N/30/TB,format=rgba,{fade}[n{k}]")
            out_label = "[v]" if k == len(overlays) - 1 else f"[base{k + 1}]"
            chains.append(f"[base{k}][n{k}]overlay=x=(W-w)/2:y=60:enable='between(t,{a:.2f},{b:.2f})':shortest=1"
                          f"{out_label}")
            next_input += 1
    if args.music:
        cmd += ["-stream_loop", "-1", "-i", args.music]
        music_input, next_input = next_input, next_input + 1
        chains.append(f"[{music_input}:a]volume={MUSIC_VOLUME},afade=t=out:st={max(total - 2, 0):.2f}:d=2,"
                      f"atrim=0:{total:.2f}[song]")
        mix = ["[song]"]
        for k, (path, at) in enumerate(effects):
            cmd += ["-i", path]
            ms = int(at * 1000)
            chains.append(f"[{next_input}:a]volume={SFX_VOLUME},adelay={ms}|{ms},apad,atrim=0:{total:.2f}[fx{k}]")
            mix.append(f"[fx{k}]")
            next_input += 1
        chains.append("".join(mix) + f"amix=inputs={len(mix)}:duration=first:normalize=0,{LOUDNESS}[a]")
    out = os.path.join(final, f"{name}.mp4")
    cmd += ["-filter_complex", ";".join(chains), "-map", "[v]"]
    cmd += ["-map", "[a]", "-c:a", "aac", "-b:a", "192k"] if args.music else ["-an"]
    run(cmd + ["-c:v", "libx264", "-preset", "medium", "-crf", "17", "-pix_fmt", "yuv420p", out])
    short = os.path.join(final, f"{name}_short.mp4")
    run([tool("ffmpeg"), "-y", "-i", out, "-vf", "crop=ih*9/16:ih,scale=1080:1920:flags=lanczos",
         "-c:v", "libx264", "-preset", "medium", "-crf", "17", "-c:a", "copy", short])
    print(f"Wrote {out} and {short} from {len(clips)} clips")


if __name__ == "__main__":
    main()
