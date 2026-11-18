"""Makes sample voices from a written description, so you can pick a new narrator or System voice.

Usage (from the WanGP folder):
    python stories/tools/design_voice.py stories/one_rank_higher narrator
    python stories/tools/design_voice.py stories/one_rank_higher system
    python stories/tools/design_voice.py stories/one_rank_higher narrator "a different description" ...

With no descriptions, it uses the voice variations listed below for that role. Writes
stories/<series>/batches/voice_design_<role>.json: 4 samples per description, all reading the same test line.
Render it with the printed command, listen to stories/<series>/output/voice_design/, save the one you like as
stories/<series>/refs/<role>.wav, and add to the matching section ("narrator" or "system") of cast.json:
    "voice": "refs/<role>.wav",
    "voice_text": "<the test line printed below, exactly>"
From then on build_episode.py reads every line for that role in that voice (Qwen3 voice clone), so it never drifts.
"""
import json
import os
import sys

DESIGN_MODEL = "qwen3_tts_voicedesign"
LINES = {
    "narrator": ("At midnight, four billion people vanished from Earth. They woke up alone, on rafts, in an ocean that "
                 "never ends. And one of them was about to become number one in the world."),
    "system": ("Good morning, candidate. You have been summoned to the Drift. Survival odds are low. "
               "Please try not to die. It makes the paperwork worse."),
}
VARIATIONS = {
    "narrator": [
        "An American man about 30 with a vivid, cinematic storytelling voice, clear and engaging, warm mid-low tone, "
        "steady confident pacing, able to shift from dramatic to analytical",
        "An American man about 30, a slightly deeper, more dramatic cinematic narrator with movie-trailer weight but "
        "natural and conversational, crisp clear diction, steady pacing",
        "An American man about 30, a bright, energetic and engaging storyteller like a popular recap channel host, "
        "vivid and clear, steady pace with a lively edge",
    ],
    "system": [
        "An American woman about 30, the voice of an all-knowing game system, analytical and dryly sarcastic, "
        "smooth and beautiful with a slightly robotic, precise, synthetic polish, calm even pacing",
        "An American woman about 30, a cool, clinical AI voice, crisp precise diction, a faint digital sheen, "
        "deadpan sarcasm, beautiful and composed",
        "An American woman about 30, an elegant silky AI voice with subtle synthetic resonance, amused and sarcastic "
        "but precise and analytical, unhurried pacing",
    ],
}


def main():
    if len(sys.argv) < 3 or sys.argv[2] not in LINES:
        sys.exit(__doc__)
    series, role = sys.argv[1], sys.argv[2]
    descriptions = sys.argv[3:] or VARIATIONS[role]
    tasks = []
    for d, description in enumerate(descriptions):
        for take in range(4):
            tasks.append({
                "model_type": DESIGN_MODEL,
                "prompt": LINES[role],
                "alt_prompt": description + ". Speaks only the given words, clearly, no laughing, no whispering.",
                "model_mode": "english",
                "duration_seconds": 20,
                "temperature": 0.7,
                "seed": 900 + 10 * d + take,
                "output_filename": f"{role}_{d + 1}{'abcd'[take]}",
            })
    out_dir = os.path.join(series, "batches")
    os.makedirs(out_dir, exist_ok=True)
    out = os.path.join(out_dir, f"voice_design_{role}.json")
    with open(out, "w", encoding="utf-8") as f:
        json.dump(tasks, f, indent=2)
    print(f"Wrote {out} ({len(tasks)} samples)")
    print(f"Render: python wgp.py --process {out} --output-dir {os.path.join(series, 'output', 'voice_design')}")
    print(f"Test line (use it as voice_text): {LINES[role]}")


if __name__ == "__main__":
    main()
