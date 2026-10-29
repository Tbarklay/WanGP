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
3. **In the morning:** the video and its captions (`.srt`, upload them in YouTube Studio > Subtitles) are in
   `stories/<series>/final`.

To redo a bad illustration: delete it from `stories/<series>/output/<ep>`, render that prompt again in the WanGP UI
(the batch file in `stories/<series>/batches` has every prompt), save it with the same name, and rerun
`python stories/tools/assemble_episode.py <script>`.

## Models
- Narration: Qwen3 TTS Custom Voice, preset speaker set in `cast.json` (same voice every episode).
- Scenes with characters: Qwen Image Edit Plus (2511), with up to 3 reference pictures per scene.
- Scenes without recurring characters: Qwen Image (2512).
- Images render at 1280x720 and are shown at 1920x1080 with a slow zoom or pan.
