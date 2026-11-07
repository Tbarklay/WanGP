"""Builds WanGP batches for animated Obi shorts: 3D references, keyframes, then animated clips.

Usage (from the WanGP folder):
    python obi_shorts/tools/build_shots.py refs                              # 3D versions of Obi and the farmer
    python obi_shorts/tools/build_shots.py keyframes obi_shorts/test_shots.md
    python obi_shorts/tools/build_shots.py animate obi_shorts/test_shots.md   # after the keyframes are rendered
    python obi_shorts/tools/build_shots.py song obi_shorts/obi_farm_parade.md # 3 takes of the song, if the list has lyrics
    python obi_shorts/tools/build_shots.py sfx obi_shorts/obi_five_ducks.md   # 3 takes of each sound effect, if any

Optional per shot, on lines after its [motion: ...] line:
    `[count: 3]`    a big number 3 pops up on screen during the shot
    `[count: 1-4]`  1, 2, 3, 4 pop up one after another, spread over the shot (counting animals arriving)
    `[sfx: quack]`  plays the sound effect "quack" at the start of the shot; `[sfx: quack @2.5]` 2.5 s into it
    `[voice: doctor @0.4]` plays the spoken line "doctor" there, with the song turned down under it
Sound effects are described in a '## Sound effects' section as lines like: quack: a real mother duck quacking
Spoken lines go in a '## Voices' section as: doctor: aiden | warm playful delivery | No more bouncing, little piggies!
(name: Qwen3 preset speaker | how to say it | the words). They render with the sound effects (mode sfx).
Add --shots 2,3 to keyframes or animate to redo only some shots with new seeds.

Each mode writes a batch to obi_shorts/batches and prints the command that renders it; keyframes and clips
of a shot list all go to obi_shorts/output/<shot list name>.
"""
import argparse
import glob
import json
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(os.path.dirname(ROOT), "stories", "tools"))
from build_episode import image_task, parse_beat_list  # same keyframe logic as the story episodes

ANIMATE_MODEL = "i2v_2_2_Enhanced_Lightning_v2"   # Wan 2.2 image-to-video, 4 steps, good camera and motion
CLIP_RESOLUTION = "832x480"                       # safe on a 12 GB card; the assembler upscales to 1080p
CLIP_FRAMES = 81                                  # about 5 seconds at 16 fps
SEED = 4100

SHOT = re.compile(r"^\*\*(\d+)\*\*\s*`\[keyframe:\s*(.*?)\]`\s*\n`\[motion:\s*(.*?)\]`", re.M | re.S)

REF_SOURCES = {
    "obi_3d": ("kids_videos/refs/dog.jpg",
               "Recreate the puppy from picture 1 as a 3D animated movie character: the same fluffy shaggy black and "
               "tan coat, white chest patch, floppy ears, big brown eyes and happy pink tongue. Full body, standing on "
               "all four paws, three-quarter front view, friendly smile, plain light gray background, soft studio light."),
    "farmer_3d": ("kids_videos/refs/farmer_and_dog.jpg",
                  "Recreate only the farmer from picture 1, without the dog, as a 3D animated movie character: the same "
                  "kind elderly face with a short white beard and gray hair, dark gray cap, red and brown plaid flannel "
                  "shirt, muddy blue denim overalls and brown work boots. Full body standing, front view, warm smile, "
                  "plain light gray background, soft studio light."),
}


def load_cast():
    path = os.path.join(ROOT, "cast.json")
    cast = json.load(open(path, encoding="utf-8"))
    cast["_path"] = path
    return cast


def parse_shots(path):
    shots = [(int(n), key.strip(), " ".join(motion.split())) for n, key, motion in
             SHOT.findall(open(path, encoding="utf-8").read())]
    if not shots:
        sys.exit(f"No shots found in {path}")
    return shots


EXTRA = re.compile(r"`\[(count|sfx|voice):\s*(.*?)\]`")


def parse_extras(path):
    """Shot number -> list of (kind, value) for the optional [count: ...] and [sfx: ...] lines."""
    text = open(path, encoding="utf-8").read()
    starts = [(int(m.group(1)), m.start()) for m in re.finditer(r"^\*\*(\d+)\*\*", text, re.M)]
    extras = {}
    for i, (no, start) in enumerate(starts):
        end = starts[i + 1][1] if i + 1 < len(starts) else len(text)
        found = EXTRA.findall(text[start:end])
        if found:
            extras[no] = [(kind, value.strip()) for kind, value in found]
    return extras


def parse_sfx(path):
    """Sound effect name -> description, from the '## Sound effects' section."""
    text = open(path, encoding="utf-8").read()
    section = re.search(r"^## Sound effects\n(.+?)(?=\n## |\Z)", text, re.M | re.S)
    if not section:
        return {}
    return {m.group(1): m.group(2).strip() for m in re.finditer(r"^\s*[-*]?\s*(\w+):\s*(.+)$", section.group(1), re.M)}


def parse_voices(path):
    """Spoken line name -> (speaker, delivery, words), from the '## Voices' section."""
    text = open(path, encoding="utf-8").read()
    section = re.search(r"^## Voices\n(.+?)(?=\n## |\Z)", text, re.M | re.S)
    voices = {}
    for m in re.finditer(r"^\s*[-*]?\s*(\w+):\s*(.+)$", section.group(1) if section else "", re.M):
        parts = [p.strip() for p in m.group(2).split("|")]
        if len(parts) == 3:
            voices[m.group(1)] = tuple(parts)
    return voices


def sfx_tasks(path, name):
    tasks = []
    for line, (speaker, delivery, words) in parse_voices(path).items():
        for take in range(3):
            tasks.append({
                "model_type": "qwen3_tts_customvoice",
                "prompt": words,
                "alt_prompt": delivery + ", speaks only the given words, no laughing, no whispering",
                "model_mode": speaker,
                "duration_seconds": max(4, round(len(words.split()) * 0.7 + 3)),
                "temperature": 0.7,
                "seed": SEED + 70 + take,
                "output_filename": f"{name}_sfx_{line}_{'abc'[take]}",
            })
    for effect, description in parse_sfx(path).items():
        for take in range(3):
            tasks.append({
                "model_type": "stable_audio3_small_sfx",
                "prompt": description,
                "negative_prompt": "music, singing, speech, voice, poor quality, distorted, noisy",
                "duration_seconds": 3,
                "seed": SEED + 50 + take,
                "output_filename": f"{name}_sfx_{effect}_{'abc'[take]}",
            })
    if not tasks:
        sys.exit(f"{path} has no '## Sound effects' or '## Voices' section")
    return tasks


def song_tasks(path, name, seconds):
    text = open(path, encoding="utf-8").read()
    music = re.search(r"^## Music\n(.+?)(?=\n## )", text, re.M | re.S)
    lyrics = re.search(r"^## Lyrics\n(.+?)(?=\n## )", text, re.M | re.S)
    if not (music and lyrics):
        sys.exit(f"{path} has no '## Music' and '## Lyrics' sections")
    return [{
        "model_type": "ace_step_v1_5_turbo_lm_1_7b",
        "prompt": lyrics.group(1).strip(),
        "alt_prompt": " ".join(music.group(1).split()),
        "duration_seconds": seconds,
        "seed": SEED + take,
        "output_filename": f"{name}_song_{'abc'[take]}",
    } for take in range(3)]


def ref_tasks(cast):
    tasks = []
    for name, (source, prompt) in REF_SOURCES.items():
        for take in range(4):
            tasks.append({
                "model_type": "qwen_image_edit_plus2_20B",
                "prompt": f"{cast['style']}. {prompt}",
                "negative_prompt": cast["negative"],
                "resolution": "1024x1024",
                "video_prompt_type": "I",
                "image_refs": [source],
                "remove_background_images_ref": 0,
                "seed": SEED + 100 * len(tasks),
                "output_filename": f"{name}_{'abcd'[take]}",
            })
    return tasks


def newest(folder, stem):
    files = glob.glob(os.path.join(folder, stem + "*"))
    return max(files, key=os.path.getmtime) if files else None


def clip_task(cast, name, no, motion, keyframe, seed_offset):
    return {
        "model_type": ANIMATE_MODEL,
        "prompt": f"{motion}. {cast['style']}, smooth natural animation, consistent characters.",
        "negative_prompt": cast["negative"] + ", morphing, melting, flickering, sudden cuts, static image",
        "image_prompt_type": "S",
        "image_start": [keyframe.replace("\\", "/")],
        "resolution": CLIP_RESOLUTION,
        "video_length": CLIP_FRAMES,
        "seed": SEED + no + seed_offset,
        "output_filename": f"{name}_clip_{no:02d}",
    }


def write(name, tasks, folder=None):
    out_dir = os.path.join(ROOT, "batches")
    os.makedirs(out_dir, exist_ok=True)
    out = os.path.join(out_dir, f"{name}.json")
    with open(out, "w", encoding="utf-8") as f:
        json.dump(tasks, f, indent=2)
    print(f"Wrote {out} ({len(tasks)} tasks)")
    print(f"Render: python wgp.py --process {os.path.relpath(out)} --output-dir "
          f"{os.path.relpath(os.path.join(ROOT, 'output', folder or name))}")


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("mode", choices=["refs", "keyframes", "animate", "song", "sfx"])
    parser.add_argument("script", nargs="?", help="shot list (.md), for keyframes and animate")
    parser.add_argument("--shots", help="only these shots, for example 2,3 (rendered with new seeds)")
    args = parser.parse_args()
    cast = load_cast()

    if args.mode == "refs":
        write("refs", ref_tasks(cast))
        print("Pick the best obi_3d_* and farmer_3d_* picture and save them as obi_shorts/refs/obi_3d.png "
              "and obi_shorts/refs/farmer_3d.png")
        return
    if not args.script:
        sys.exit("Give the shot list, for example obi_shorts/test_shots.md")

    name = os.path.splitext(os.path.basename(args.script))[0]
    shots = parse_shots(args.script)
    seed_offset = 0
    if args.shots:
        wanted = parse_beat_list(args.shots)
        shots, seed_offset = [s for s in shots if s[0] in wanted], 1000

    if args.mode == "song":
        # Long enough to cover every clip; the assembler fits the clips to the song it picks.
        write(name + "_song", song_tasks(args.script, name, round(len(shots) * CLIP_FRAMES / 16) + 5), name)
        return

    if args.mode == "sfx":
        write(name + "_sfx", sfx_tasks(args.script, name), name)
        return

    if args.mode == "keyframes":
        for key in {k for _, frame, _ in shots for k in re.findall(r"\{(\w+)\}", frame)}:
            ref = cast["characters"].get(key, {}).get("ref")
            if ref and not os.path.isfile(os.path.join(ROOT, ref)):
                sys.exit(f"Missing 3D reference {os.path.join(ROOT, ref)}: run the refs step first and save the best one")
        tasks = [image_task(cast, name, no, frame, seed_offset) for no, frame, _ in shots]
        write(name + ("_redo" if args.shots else ""), tasks, name)
        return

    folder = os.path.join(ROOT, "output", name)
    tasks, missing = [], []
    for no, _, motion in shots:
        keyframe = newest(folder, f"{name}_img_{no:02d}")
        if keyframe is None:
            missing.append(no)
        else:
            tasks.append(clip_task(cast, name, no, motion, os.path.relpath(keyframe), seed_offset))
    if missing:
        sys.exit(f"No keyframe yet for shots {missing} in {folder}: render the keyframes batch first")
    write(name + "_clips" + ("_redo" if args.shots else ""), tasks, name)


if __name__ == "__main__":
    main()
