"""Builds the overnight WanGP batch for one story episode: narration clips and illustrations.

Usage (from the WanGP folder):
    python stories/tools/build_episode.py stories/debt_hunter/ep01_account_opened.md
    python stories/tools/build_episode.py stories/debt_hunter/ep01_account_opened.md --test

Reads the episode script (beats written as **NN**, an `[image: ...]` line, then the narration) and
the series' cast.json. Writes stories/<series>/batches/<ep>.json; render it with
    python wgp.py --process stories/<series>/batches/<ep>.json --output-dir stories/<series>/output/<ep>
--test keeps only the first 3 beats, to check the voice and the characters before a full night.
"""
import json
import os
import re
import sys

TTS_MODEL = "qwen3_tts_customvoice"          # fixed preset voices, so the narrator never changes
EDIT_MODEL = "qwen_image_edit_plus2_20B"     # combines several reference pictures in one scene
T2I_MODEL = "qwen_image_2512_20B"            # same family, for scenes without a recurring character
RESOLUTION = "1280x720"
MAX_REFS = 3                                 # more reference pictures than this blurs identities
SEED = 2026

BEAT = re.compile(r"^\*\*(\d+)\*\*\s*`\[image:\s*(.*?)\]`\s*\n(.+?)(?=\n\s*\n|\Z)", re.M | re.S)
KEY = re.compile(r"\{(\w+)\}")


def parse_beats(path):
    text = open(path, encoding="utf-8").read()
    beats = [(int(n), image.strip(), " ".join(narration.split())) for n, image, narration in BEAT.findall(text)]
    if not beats:
        sys.exit(f"No beats found in {path}")
    return beats


def image_task(cast, ep, no, image):
    keys = list(dict.fromkeys(KEY.findall(image)))
    unknown = [k for k in keys if k not in cast["characters"]]
    if unknown:
        sys.exit(f"Beat {no}: unknown character {unknown}, add it to cast.json")
    pictured = keys[:MAX_REFS]

    def describe(match):
        key = match.group(1)
        desc = cast["characters"][key]["desc"]
        return f"{desc} (picture {pictured.index(key) + 1})" if key in pictured else desc

    scene = KEY.sub(describe, image)
    task = {
        "negative_prompt": cast["negative"],
        "resolution": RESOLUTION,
        "seed": SEED + no,
        "output_filename": f"{ep}_img_{no:02d}",
    }
    if not pictured:
        task.update(model_type=T2I_MODEL, prompt=f"{cast['style']}. {scene}.")
        return task
    series = os.path.dirname(cast["_path"])
    task.update(
        model_type=EDIT_MODEL,
        prompt=f"{cast['style']}. {scene}. Draw a brand new scene: keep each referenced character's face, hair, "
               "outfit and colors exactly as in their picture. Each character appears exactly once, in a natural "
               "pose that fits the action and the camera angle, not standing stiffly facing the viewer. Do not copy "
               "the plain backgrounds or poses of the reference pictures.",
        video_prompt_type="I",
        image_refs=[os.path.join(series, cast["characters"][k]["ref"]).replace("\\", "/") for k in pictured],
        remove_background_images_ref=1,
    )
    return task


def voice_task(cast, ep, no, narration):
    words = len(narration.split())
    return {
        "model_type": TTS_MODEL,
        "prompt": narration,
        "alt_prompt": cast["narrator"]["instruction"],
        "model_mode": cast["narrator"]["speaker"],
        "duration_seconds": max(15, round(words / 2 + 10)),  # a cap, generously above the reading time
        "seed": SEED,
        "output_filename": f"{ep}_vo_{no:02d}",
    }


def main():
    args = [a for a in sys.argv[1:] if a != "--test"]
    if len(args) != 1:
        sys.exit(__doc__)
    script = args[0]
    series = os.path.dirname(script)
    cast_path = os.path.join(series, "cast.json")
    cast = json.load(open(cast_path, encoding="utf-8"))
    cast["_path"] = cast_path
    ep = os.path.basename(script).split("_")[0]

    beats = parse_beats(script)
    if "--test" in sys.argv:
        beats, ep = beats[:3], ep + "_test"
    for _, image, _ in beats:
        for key in KEY.findall(image):
            ref = os.path.join(series, cast["characters"].get(key, {}).get("ref", ""))
            if key in cast["characters"] and not os.path.isfile(ref):
                sys.exit(f"Missing reference image for {key}: {ref}")

    # Voices first (fast), then plain scenes, then reference scenes: grouping avoids reloading models.
    voices = [voice_task(cast, ep, no, narration) for no, _, narration in beats]
    images = [image_task(cast, ep, no, image) for no, image, _ in beats]
    images.sort(key=lambda t: t["model_type"] != T2I_MODEL)
    tasks = voices + images

    out_dir = os.path.join(series, "batches")
    os.makedirs(out_dir, exist_ok=True)
    out = os.path.join(out_dir, f"{ep}.json")
    with open(out, "w", encoding="utf-8") as f:
        json.dump(tasks, f, indent=2)
    plain = sum(t["model_type"] == T2I_MODEL for t in images)
    print(f"Wrote {out}: {len(voices)} narration clips, {len(images)} images "
          f"({len(images) - plain} with character references, {plain} without)")


if __name__ == "__main__":
    main()
