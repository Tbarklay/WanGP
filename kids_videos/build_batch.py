"""Builds the WanGP batch files for one or more songs, in two stages.

Stage 1, keyframes: draws one picture per shot (16:9 and 9:16) from the character pictures.
    python kids_videos/build_batch.py old_macdonald keyframes
    -> render with: python wgp.py --process kids_videos/batches/<name>_keyframes.json --output-dir kids_videos/keyframes

Check the pictures in kids_videos/keyframes, delete any bad one and render the keyframes
batch again (only the missing pictures are drawn), until they all look right.

Stage 2, videos: sings the song and animates every approved keyframe.
    python kids_videos/build_batch.py old_macdonald videos
    -> render with: python wgp.py --process kids_videos/batches/<name>_videos.json --output-dir kids_videos/output

Songs: one name, several joined with '+' (old_macdonald+five_little_ducks), or all.
Add --test to build only the first shot of the first song in 16:9.
Add --seed=2000 to redraw deleted keyframes with different seeds.
"""
import glob
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from songs import MOTION, NEGATIVE, SONGS

KEYFRAME_MODEL = "qwen_image_edit_plus2_20B"            # Qwen Image Edit Plus 2511, copies the reference pictures
KEYFRAME_LORA = ("https://huggingface.co/DeepBeepMeep/Qwen_image/resolve/main/loras_accelerators/"
                 "Qwen-Image-Edit-2511-Lightning-8steps-V1.0-bf16.safetensors")
VIDEO_MODEL = "i2v_2_2_Enhanced_Lightning_v2"           # Wan 2.2 image-to-video, starts from the keyframe
SONG_MODEL = "ace_step_v1_5_turbo_lm_1_7b"              # ACE-Step 1.5 Turbo, sings the lyrics
FORMATS = {
    #        keyframe      video
    "long": ("1280x720", "832x480"),    # 16:9 YouTube video
    "short": ("720x1280", "480x832"),   # 9:16 YouTube Short
}
KEYFRAME_DIR = "kids_videos/keyframes"
CLIP_FRAMES = 81          # about 5 seconds at 16 fps
SONG_TAKES = 3            # several takes, keep the one that sounds best
BASE_SEED = 1000
# Enhancement applied to every clip right after it renders:
UPSCALE = "flashvsr2pass*2"   # FlashVSR Two Pass, x2 detail recovery -> 1664x960 / 960x1664
SMOOTH = "rife*2"             # RIFE frame interpolation, 16 -> 32 fps for smoother motion


def shot_name(song, fmt, no):
    return f"{song['slug']}_{fmt}_{no:02d}"


def shot_refs(song, shot):
    """Pictures of the characters this shot names, each once, in cast order."""
    refs = []
    for name, path in song["refs"].items():
        if "{" + name + "}" in shot and path not in refs:
            refs.append(path)
    return refs


def find_keyframe(name):
    files = [f for f in glob.glob(os.path.join(KEYFRAME_DIR, name + ".*")) if not f.endswith(".json")]
    return max(files, key=os.path.getmtime) if files else None


def keyframe_tasks(song, fmt, missing_only=True):
    tasks = []
    for no, shot in enumerate(song["shots"], 1):
        name = shot_name(song, fmt, no)
        if missing_only and find_keyframe(name):
            continue                                    # already drawn and kept
        prompt = f"{song['style']}. " + shot.format(**song["cast"])
        prompt += ", vertical portrait composition" if fmt == "short" else ", wide landscape composition"
        task = {
            "model_type": KEYFRAME_MODEL,
            "image_mode": 1,
            "prompt": prompt,
            "negative_prompt": song.get("negative", NEGATIVE),
            "resolution": FORMATS[fmt][0],
            "activated_loras": [KEYFRAME_LORA],
            "loras_multipliers": "1",
            "num_inference_steps": 8,
            "guidance_scale": 1,
            "video_prompt_type": "",
            "seed": BASE_SEED + no,                     # same seed for long and short
            "output_filename": name,
        }
        refs = [ref for ref in shot_refs(song, shot) if os.path.isfile(ref)]
        if refs:
            task["video_prompt_type"] = "I"             # reference pictures = people / objects
            task["image_refs"] = refs
            task["remove_background_images_ref"] = 1
        tasks.append(task)
    return tasks


def song_tasks(song):
    tasks = []
    for take in range(SONG_TAKES):
        name = f"{song['slug']}_song_{chr(ord('a') + take)}"
        if glob.glob(os.path.join("kids_videos/output", name + ".*")):
            continue                                    # this take was already sung, keep it
        tasks.append({
            "model_type": SONG_MODEL,
            "prompt": song["lyrics"],
            "alt_prompt": song["music"],
            "duration_seconds": song["seconds"],
            "seed": BASE_SEED + take,
            "output_filename": name,
        })
    return tasks


def clip_tasks(song, fmt):
    tasks = []
    for no, shot in enumerate(song["shots"], 1):
        name = shot_name(song, fmt, no)
        if glob.glob(os.path.join("kids_videos/output", name + ".mp4")):
            continue                                    # already animated (delete a clip to redo it)
        keyframe = find_keyframe(name)
        if keyframe is None:
            print(f"WARNING: no keyframe for {name}, this clip is left out")
            continue
        tasks.append({
            "model_type": VIDEO_MODEL,
            "prompt": shot.format(**song["cast"]) + ", " + MOTION,
            "negative_prompt": song.get("negative", NEGATIVE),
            "resolution": FORMATS[fmt][1],
            "video_length": CLIP_FRAMES,
            "image_prompt_type": "S",                   # start from the keyframe
            "image_start": keyframe.replace("\\", "/"),
            "spatial_upsampling": UPSCALE,
            "temporal_upsampling": SMOOTH,
            "seed": BASE_SEED + no,
            "output_filename": name,
        })
    return tasks


def build(slugs, stage):
    tasks = []
    if stage == "videos":
        for slug in slugs:
            tasks += song_tasks(SONGS[slug])
    # Long versions before Shorts, so the main videos finish first.
    for fmt in FORMATS:
        for slug in slugs:
            song = SONGS[slug]
            tasks += keyframe_tasks(song, fmt) if stage == "keyframes" else clip_tasks(song, fmt)
    return tasks


def song_list(arg):
    """'all', one song, or several joined with '+'. None if a song is unknown."""
    slugs = list(SONGS) if arg == "all" else arg.split("+")
    return slugs if all(slug in SONGS for slug in slugs) else None


def main():
    global BASE_SEED
    # --seed=N draws redone keyframes with new seeds (delete the bad pictures first).
    for a in sys.argv[1:]:
        if a.startswith("--seed="):
            BASE_SEED = int(a.split("=", 1)[1])
    args = [a for a in sys.argv[1:] if a != "--test" and not a.startswith("--seed=")]
    test = "--test" in sys.argv[1:]
    slugs = song_list(args[0]) if len(args) == 2 and args[1] in ("keyframes", "videos") else None
    if not slugs:
        print(f"Usage: python kids_videos/build_batch.py <{'|'.join(SONGS)}|all> <keyframes|videos> [--test]")
        print("       several songs: old_macdonald+five_little_ducks")
        sys.exit(1)
    name, stage = args
    if test:
        song = SONGS[slugs[0]]
        tasks = keyframe_tasks(song, "long", missing_only=False)[:1] if stage == "keyframes" else clip_tasks(song, "long")[:1]
        name += "_test"
    else:
        tasks = build(slugs, stage)
    os.makedirs("kids_videos/batches", exist_ok=True)
    path = f"kids_videos/batches/{name}_{stage}.json"
    with open(path, "w", encoding="utf-8") as f:
        json.dump(tasks, f, indent=2)
    songs = sum(1 for t in tasks if t["model_type"] == SONG_MODEL)
    print(f"Wrote {path}: {songs} song takes + {len(tasks) - songs} {'pictures' if stage == 'keyframes' else 'clips'}")


if __name__ == "__main__":
    main()
