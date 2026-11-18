"""Makes sample narrator voices from a written description, so you can pick a new narrator.

Usage (from the WanGP folder):
    python stories/tools/design_voice.py stories/one_rank_higher "deep calm male voice, ..." ["second description" ...]

Writes stories/<series>/batches/voice_design.json: 4 samples for each description, all reading the same test line.
Render it with the printed command, listen to stories/<series>/output/voice_design/, and save the one you like as
stories/<series>/refs/narrator.wav. Then add to the "narrator" section of cast.json:
    "voice": "refs/narrator.wav",
    "voice_text": "<the test line below, exactly>"
From then on build_episode.py reads every line in that voice (Qwen3 voice clone), so it never drifts.
"""
import json
import os
import sys

LINE = ("At midnight, four billion people vanished from Earth. They woke up alone, on rafts, in an ocean that never "
        "ends. And one of them was about to become number one in the world.")
DESIGN_MODEL = "qwen3_tts_voicedesign"


def main():
    if len(sys.argv) < 3:
        sys.exit(__doc__)
    series, descriptions = sys.argv[1], sys.argv[2:]
    tasks = []
    for d, description in enumerate(descriptions):
        for take in range(4):
            tasks.append({
                "model_type": DESIGN_MODEL,
                "prompt": LINE,
                "alt_prompt": description + ". Speaks only the given words, clearly, no laughing, no whispering.",
                "model_mode": "english",
                "duration_seconds": 20,
                "temperature": 0.7,
                "seed": 900 + 10 * d + take,
                "output_filename": f"voice_{d + 1}{'abcd'[take]}",
            })
    out_dir = os.path.join(series, "batches")
    os.makedirs(out_dir, exist_ok=True)
    out = os.path.join(out_dir, "voice_design.json")
    with open(out, "w", encoding="utf-8") as f:
        json.dump(tasks, f, indent=2)
    print(f"Wrote {out} ({len(tasks)} samples)")
    print(f"Render: python wgp.py --process {out} --output-dir {os.path.join(series, 'output', 'voice_design')}")
    print(f"Test line (use it as voice_text): {LINE}")


if __name__ == "__main__":
    main()
