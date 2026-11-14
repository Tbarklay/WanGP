"""Joins the animated clips of a shot list into one 1080p video, with optional music.

Usage (from the WanGP folder, after the clips are rendered):
    python obi_shorts/tools/assemble_shots.py obi_shorts/test_shots.md
    python obi_shorts/tools/assemble_shots.py obi_shorts/test_shots.md --music path/to/music.mp3
    python obi_shorts/tools/assemble_shots.py obi_shorts/obi_farm_parade.md --song b   # use song take b

With a song (rendered by build_shots.py song), the clips are sped up or slowed down slightly so the
video ends with the song; plain --music is faded out at the end of the clips instead.

Writes obi_shorts/final/<shot list name>.mp4 (16:9) and <name>_short.mp4 (9:16, center crop for Shorts).

Intro and goodbye cards: obi_shorts/cards/obi_intro.mp4 and obi_outro.mp4 (made in Flow, kept in the repo; a newer
version saved in obi_shorts/final/ takes their place), every video automatically opens with the "Sing, sing, sing with Obi!" jingle and ends with Obi's
goodbye card, where YouTube's end screen (Subscribe button, next video) goes. The Short gets neither (viewers
decide in the first second whether to swipe). Add --no-intro to leave them out.
A `[title: Sing with Obi]` line under a shot shows those words as big colorful letters over that shot.
A `[spell: BINGO drop=2 icon=stomp x3 @0.4-6.2]` line spells BINGO across the top in giant colored letters, 3 times
between 0.4 and 6.2 s into the shot, the sung letter drawn bigger; the first 2 letters are shown as the action's
picture (icons: clap, stomp, pat, jump, woof, wave, spin, or any emoji). Set the window from the sung words.
"""
import argparse
import glob
import os
import re
import shutil
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from build_shots import parse_extras, parse_shots

LOUDNESS = "loudnorm=I=-14:TP=-1.5:LRA=11"
SFX_VOLUME = 1.6        # sound effects sit clearly above the song
VOICE_VOLUME = 2.2      # spoken lines sit well above the song
DUCK = 0.75             # the song dips only a little under a spoken line, so it keeps its energy
COUNT_SIZE = 260        # height of the on-screen counting numbers, in pixels at 1080p
COUNT_X, COUNT_Y = 60, 40  # top-left corner, clear of the characters' faces


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


TITLE_COLORS = [(255, 82, 82), (255, 167, 38), (255, 214, 10), (102, 204, 68), (41, 182, 246), (171, 71, 188)]


def title_png(folder, text):
    """The words as big bubbly letters, each in its own bright color, with a thick dark outline (transparent PNG)."""
    from PIL import Image, ImageDraw, ImageFont
    path = os.path.join(folder, "title_" + "".join(c for c in text if c.isalnum()) + ".png")
    if os.path.isfile(path):
        return path
    font = None
    for name in ("arialbd.ttf", "Arial Bold.ttf", "DejaVuSans-Bold.ttf", "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"):
        try:
            font = ImageFont.truetype(name, 190)
            break
        except OSError:
            continue
    font = font or ImageFont.load_default()
    probe = ImageDraw.Draw(Image.new("RGBA", (10, 10)))
    width = int(probe.textlength(text, font=font)) + 80
    img = Image.new("RGBA", (width, 300), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    x, k = 40, 0
    for ch in text:
        if ch != " ":
            # every other letter sits a little higher, for a playful bounce
            draw.text((x, 40 if k % 2 else 60), ch, font=font, fill=TITLE_COLORS[k % len(TITLE_COLORS)],
                      stroke_width=14, stroke_fill=(40, 30, 80))
            k += 1
        x += draw.textlength(ch, font=font)
    if img.width > 1700:
        img = img.resize((1700, round(300 * 1700 / img.width)))
    img.save(path)
    return path


SPELL_ICONS = {"clap": "\U0001F44F", "stomp": "\U0001F462", "pat": "\u270B", "jump": "\U0001F438",
               "woof": "\U0001F436", "wave": "\U0001F44B", "spin": "\U0001F4AB"}
EMOJI_FONTS = ("seguiemj.ttf", "C:/Windows/Fonts/seguiemj.ttf", "/usr/share/fonts/truetype/noto/NotoColorEmoji.ttf",
               "/System/Library/Fonts/Apple Color Emoji.ttc")


def icon_image(icon, size):
    """A color emoji picture for an action (clap, stomp, ...), or the action word in a round badge without one."""
    from PIL import Image, ImageDraw, ImageFont
    glyph = SPELL_ICONS.get(icon, icon)
    for name in EMOJI_FONTS:
        for font_size in (size, 109):   # scalable emoji fonts take any size; bitmap ones (Noto) only 109
            try:
                font = ImageFont.truetype(name, font_size)
                img = Image.new("RGBA", (font_size * 2, font_size * 2), (0, 0, 0, 0))
                ImageDraw.Draw(img).text((font_size // 2, font_size // 2), glyph, font=font, embedded_color=True)
                box = img.getbbox()
                if box:
                    img = img.crop(box)
                    scale = size / max(img.size)
                    return img.resize((round(img.width * scale), round(img.height * scale)), Image.LANCZOS)
            except (OSError, ValueError):
                continue
    img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    draw.ellipse((4, 4, size - 4, size - 4), fill=(255, 255, 255), outline=(40, 30, 80), width=10)
    word = icon.upper()[:5]
    font = ImageFont.truetype("DejaVuSans-Bold.ttf", size // 4) if os.name != "nt" else ImageFont.truetype("arialbd.ttf", size // 4)
    w = draw.textlength(word, font=font)
    draw.text(((size - w) / 2, size * 0.36), word, font=font, fill=(40, 30, 80))
    return img


def spell_png(folder, word, drop, icon, lit):
    """The word across the screen in giant colored letters; the first `drop` letters are replaced by the action's
    picture, and letter number `lit` (counting from 0) is drawn bigger, because it is the one being sung."""
    from PIL import Image, ImageDraw, ImageFont
    path = os.path.join(folder, f"spell_{word}_{drop}_{icon}_{lit}.png")
    if os.path.isfile(path):
        return path
    size, slot = 250, 330
    font = None
    for name in ("arialbd.ttf", "Arial Bold.ttf", "DejaVuSans-Bold.ttf", "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"):
        try:
            font = ImageFont.truetype(name, size)
            break
        except OSError:
            continue
    img = Image.new("RGBA", (slot * len(word), 360), (0, 0, 0, 0))
    for k, ch in enumerate(word):
        cell = Image.new("RGBA", (slot, 360), (0, 0, 0, 0))
        if k < drop:
            pic = icon_image(icon, 230)
            cell.alpha_composite(pic, ((slot - pic.width) // 2, (360 - pic.height) // 2))
        else:
            draw = ImageDraw.Draw(cell)
            w = draw.textlength(ch, font=font)
            draw.text(((slot - w) / 2, 30), ch, font=font, fill=TITLE_COLORS[k % len(TITLE_COLORS)],
                      stroke_width=16, stroke_fill=(40, 30, 80))
        grow = 1.2 if k == lit else 0.85
        cell = cell.resize((round(slot * grow), round(360 * grow)), Image.LANCZOS)
        if k != lit:   # the letters not being sung are a little faded, so the sung one stands out
            cell.putalpha(cell.getchannel("A").point(lambda a: int(a * 0.75)))
        img.alpha_composite(cell, (max(0, k * slot + (slot - cell.width) // 2), max(0, (360 - cell.height) // 2)))
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
    parser.add_argument("--length", type=float, help="cut the video to this many seconds (for the short intro card)")
    parser.add_argument("--no-intro", action="store_true", help="don't put the Obi intro card in front")
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
    if args.length:
        total = min(total, args.length)

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
                spec, _, window = value.partition("@")
                numbers = count_values(spec.strip())
                a, b = (float(x) for x in window.split("-")) if window else (0.0, length)
                step = (b - a) / len(numbers)
                for k, n in enumerate(numbers):
                    overlays.append((number_png(work, n), start + a + k * step + 0.05, start + a + (k + 1) * step,
                                     f"x={COUNT_X}:y={COUNT_Y}"))
            elif kind == "title":
                overlays.append((title_png(work, value), start + 0.3, min(start + length, total), "x=(W-w)/2:y=40"))
            elif kind == "spell":
                # BINGO drop=2 icon=stomp x3 @0.4-6.2: the word spelled 3 times across the window, one letter per step
                spec, _, window = value.partition("@")
                parts = spec.split()
                word = parts[0]
                opts = dict(p.split("=", 1) for p in parts[1:] if "=" in p)
                times = next((int(p[1:]) for p in parts[1:] if p.startswith("x") and p[1:].isdigit()), 1)
                a, b = (float(x) for x in window.split("-")) if window else (0.0, length)
                steps = len(word) * times
                step = (b - a) / steps
                for k in range(steps):
                    png = spell_png(work, word, int(opts.get("drop", 0)), opts.get("icon", "clap"), k % len(word))
                    overlays.append((png, start + a + k * step, start + a + (k + 1) * step, "x=(W-w)/2:y=20", False))
            elif kind in ("sfx", "voice"):   # [lipsync:], [end:] and [frames:] are for build_shots.py only
                effect, _, offset = value.partition("@")
                is_voice = kind == "voice"
                found = glob.glob(os.path.join(folder, f"{name}_sfx_{effect.strip()}_*"))
                if not found:
                    print(f"WARNING: sound effect '{effect.strip()}' not rendered yet (build_shots.py sfx), skipped")
                    continue
                effects.append((sorted(found)[0], start + float(offset or 0), is_voice))

    cmd = [tool("ffmpeg"), "-y", *inputs]
    next_input = len(clips)
    if overlays:
        chains[-1] = chains[-1].replace("[v]", "[base0]")
        for k, (png, a, b, pos, *fades) in enumerate(overlays):
            cmd += ["-i", png]
            # spelling steps follow each other with no fades, so the letters don't flicker between steps
            fade = (",fade=t=in:st={a:.2f}:d=0.15:alpha=1,fade=t=out:st={b - 0.15:.2f}:d=0.15:alpha=1".format(a=a, b=b)
                    if (fades[0] if fades else True) else "")
            chains.append(f"[{next_input}:v]loop=-1:1:0,setpts=N/30/TB,format=rgba{fade}[n{k}]")
            out_label = "[v]" if k == len(overlays) - 1 else f"[base{k + 1}]"
            chains.append(f"[base{k}][n{k}]overlay={pos}:enable='between(t,{a:.2f},{b:.2f})':shortest=1"
                          f"{out_label}")
            next_input += 1
    if args.music:
        cmd += ["-stream_loop", "-1", "-i", args.music]
        music_input, next_input = next_input, next_input + 1
        ducks = ""
        for path, at, is_voice in effects:
            if is_voice:
                length = float(subprocess.run([tool("ffprobe"), "-v", "error", "-show_entries", "format=duration",
                                               "-of", "csv=p=0", path], capture_output=True, text=True).stdout)
                ducks += f",volume={DUCK}:enable='between(t,{at - 0.15:.2f},{at + length + 0.15:.2f})'"
        chains.append(f"[{music_input}:a]volume={MUSIC_VOLUME}{ducks},afade=t=out:st={total - min(2, total * 0.2):.2f}:d={min(2, total * 0.2):.2f},"
                      f"atrim=0:{total:.2f}[song]")
        mix = ["[song]"]
        for k, (path, at, is_voice) in enumerate(effects):
            cmd += ["-i", path]
            ms = int(at * 1000)
            vol = VOICE_VOLUME if is_voice else SFX_VOLUME
            chains.append(f"[{next_input}:a]volume={vol},adelay={ms}|{ms},apad,atrim=0:{total:.2f}[fx{k}]")
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
    # the cards in final/ win (a new local version); otherwise the ones kept in the repo in obi_shorts/cards/
    cards = [next((c for c in (os.path.join(final, f"obi_{part}.mp4"), os.path.join(ROOT, "cards", f"obi_{part}.mp4"))
                   if os.path.isfile(c)), None) for part in ("intro", "outro")]
    if name not in ("obi_intro", "obi_outro") and not args.no_intro and args.music and any(cards):
        body = os.path.join(work, f"{name}_body.mp4")
        shutil.move(out, body)
        parts = [p for p in (cards[0], body, cards[1]) if p]
        cmd = [tool("ffmpeg"), "-y"]
        for p in parts:
            cmd += ["-i", p]
        chain = "".join(f"[{i}:v]fps=30,setsar=1[v{i}];[{i}:a]aresample=48000[a{i}];" for i in range(len(parts)))
        chain += "".join(f"[v{i}][a{i}]" for i in range(len(parts))) + f"concat=n={len(parts)}:v=1:a=1[v][a]"
        run(cmd + ["-filter_complex", chain, "-map", "[v]", "-map", "[a]", "-c:v", "libx264", "-preset", "medium",
                   "-crf", "17", "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "192k", out])
        print("Added the Obi " + " and ".join(k for k, c in zip(("intro", "goodbye card"), cards) if c)
              + " (use --no-intro to leave them out)")
    print(f"Wrote {out} and {short} from {len(clips)} clips")
    frozen = subprocess.run([tool("ffmpeg"), "-i", out, "-vf", "freezedetect=n=0.003:d=0.5", "-map", "0:v", "-f", "null", "-"],
                            capture_output=True, text=True).stderr
    starts = re.findall(r"freeze_start: ([\d.]+)", frozen)
    lengths = re.findall(r"freeze_duration: ([\d.]+)", frozen)
    if starts:
        lengths += ["until the end"] * (len(starts) - len(lengths))   # a freeze running to the end has no length
        print("WARNING: frozen picture at " + ", ".join(
                  f"{float(a):.1f}s ({b if b == 'until the end' else f'{float(b):.1f}s long'})" for a, b in zip(starts, lengths))
              + ". Fix these before uploading: cut to the next shot earlier or add a shot (see obi_shorts/CLAUDE.md).")
    else:
        print("Frozen-frame check: none found")


if __name__ == "__main__":
    main()
