# Story Episode Tools

Turn an episode script into a finished narrated video, with WanGP doing the rendering overnight.

## One-time setup per series
- `stories/<series>/cast.json`: art style, negative prompt, narrator voice, and each character's reference
  picture and short description. Scripts refer to characters as `{cass}`, `{ledger}` and so on.
- `stories/<series>/refs/front/`: one clean single-figure picture per character (cropped from the reference sheets).
- Optional: `stories/<series>/music.mp3`, background music looped quietly under the narration.

## Each episode
1. **Test first (about 15 minutes, plus the first model downloads):** double-click `stories\tools\test_episode.bat`.
   It renders the first 3 beats and assembles a short clip, so you can check the narrator voice and the characters.
2. **Overnight:** double-click `stories\tools\render_episode.bat`. It renders every narration line and illustration,
   then assembles the episode. For another episode, drag its script onto the .bat file, or run
   `stories\tools\render_episode.bat stories\debt_hunter\ep02_interest.md`.
   Between rendering and assembling, `clean_voices.py` transcribes every narration clip with Whisper and cuts
   everything that is not in the script (whispers, laughter, sighs). Clips that went badly wrong are listed with
   the command to re-record them.
3. **In the morning:** the video and its captions (`.srt`, upload them in YouTube Studio > Subtitles) are in
   `stories/<series>/final`.

## Redoing part of an episode
Rewrite the weak `[image: ...]` prompts in the script, then render only those beats with new seeds:

    python stories/tools/build_episode.py stories/debt_hunter/ep01_account_opened.md --beats 4,41,63-70 --only images
    python wgp.py --process stories/debt_hunter/batches/ep01_redo.json --output-dir stories/debt_hunter/output/ep01
    python stories/tools/assemble_episode.py stories/debt_hunter/ep01_account_opened.md

The newest render of each beat is used automatically. `--only voices` re-records narration the same way.

To redo a single illustration by hand: delete it from `stories/<series>/output/<ep>`, render that prompt again in the WanGP UI
(the batch file in `stories/<series>/batches` has every prompt), save it with the same name, and rerun
`python stories/tools/assemble_episode.py <script>`.

## Models
- Narration: Qwen3 TTS Custom Voice, preset speaker set in `cast.json` (same voice every episode).
- Scenes with characters: Qwen Image Edit Plus (2511), with up to 3 reference pictures per scene.
- Scenes without recurring characters: Qwen Image (2512).
- Images render at 1280x720 and are shown at 1920x1080 with a slow zoom or pan.
