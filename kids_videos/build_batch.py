"""Builds the overnight WanGP batch file for one or more songs.

Usage (from the WanGP folder):
    python kids_videos/build_batch.py old_macdonald
    python kids_videos/build_batch.py all

Writes kids_videos/batches/<name>.json, then render it with:
    python wgp.py --process kids_videos/batches/<name>.json --output-dir kids_videos/output
"""
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from songs import NEGATIVE, SONGS, STYLE

VIDEO_MODEL = "vace_14B_lightning_3p_2_2"      # Wan 2.2 VACE, 8 steps, keeps the reference character
SONG_MODEL = "ace_step_v1_5_turbo_lm_1_7b"     # ACE-Step 1.5 Turbo, sings the lyrics
FORMATS = {
    "long": "832x480",    # 16:9 YouTube video
    "short": "480x832",   # 9:16 YouTube Short
}
CLIP_FRAMES = 81          # about 5 seconds at 16 fps
SONG_TAKES = 3            # several takes, keep the one that sounds best
BASE_SEED = 1000


def song_tasks(song):
    tasks = []
    for take in range(SONG_TAKES):
        tasks.append({
            "model_type": SONG_MODEL,
            "prompt": song["lyrics"],
            "alt_prompt": song["music"],
            "duration_seconds": song["seconds"],
            "seed": BASE_SEED + take,
            "output_filename": f"{song['slug']}_song_{chr(ord('a') + take)}",
        })
    return tasks


def clip_tasks(song, fmt):
    tasks = []
    for no, shot in enumerate(song["shots"], 1):
        prompt = f"{STYLE}. " + shot.format(character=song["character"])
        if fmt == "short":
            prompt += ", centered vertical framing"
        tasks.append({
            "model_type": VIDEO_MODEL,
            "prompt": prompt,
            "negative_prompt": NEGATIVE,
            "resolution": FORMATS[fmt],
            "video_length": CLIP_FRAMES,
            "video_prompt_type": "I",                  # reference image = people / objects
            "image_refs": [song["reference_image"]],
            "remove_background_images_ref": 1,
            "seed": BASE_SEED + no,                     # same seed for long and short
            "output_filename": f"{song['slug']}_{fmt}_{no:02d}",
        })
    return tasks


def build(slugs):
    tasks = []
    for slug in slugs:
        song = SONGS[slug]
        if not os.path.isfile(song["reference_image"]):
            print(f"WARNING: reference image not found: {song['reference_image']}")
        tasks += song_tasks(song)
    # Long versions before Shorts, so the main videos finish first.
    for fmt in FORMATS:
        for slug in slugs:
            tasks += clip_tasks(SONGS[slug], fmt)
    return tasks


def main():
    if len(sys.argv) != 2 or (sys.argv[1] != "all" and sys.argv[1] not in SONGS):
        print(f"Usage: python kids_videos/build_batch.py <{'|'.join(SONGS)}|all>")
        sys.exit(1)
    name = sys.argv[1]
    slugs = list(SONGS) if name == "all" else [name]
    tasks = build(slugs)
    os.makedirs("kids_videos/batches", exist_ok=True)
    path = f"kids_videos/batches/{name}.json"
    with open(path, "w", encoding="utf-8") as f:
        json.dump(tasks, f, indent=2)
    clips = sum(1 for t in tasks if t["model_type"] == VIDEO_MODEL)
    print(f"Wrote {path}: {len(tasks) - clips} song takes + {clips} clips")


if __name__ == "__main__":
    main()
