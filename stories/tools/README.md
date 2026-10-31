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
   Between rendering and assembling, `review_voices.py` checks every narration take: an AudioSet sound
   classifier listens for laughter, gasps and whispering, and Whisper medium.en checks for missing or garbled
   words. It trims only the silence before and after the speech, never inside it. Beats without a clean take are
   re-recorded with new seeds (it runs `wgp.py` itself), and the chosen take is saved as `<ep>_vo_NN_pick.wav`
   plus `<ep>_vo_NN_pick_clean.wav`, which the assembler uses. Beats that never got a clean take are listed at the
   end; their best take is used.
3. **In the morning:** the video and its captions (`.srt`, upload them in YouTube Studio > Subtitles) are in
   `stories/<series>/final`.

## Redoing part of an episode
Rewrite the weak `[image: ...]` prompts in the script, then render only those beats with new seeds:

    python stories/tools/build_episode.py stories/debt_hunter/ep01_account_opened.md --beats 4,41,63-70 --only images
    python wgp.py --process stories/debt_hunter/batches/ep01_redo.json --output-dir stories/debt_hunter/output/ep01
    python stories/tools/assemble_episode.py stories/debt_hunter/ep01_account_opened.md

The newest render of each beat is used automatically.

To check or redo narration for some beats only (it re-records bad takes by itself, no separate step):

    python stories\tools\review_voices.py stories\debt_hunter\ep01_account_opened.md --beats 4,21,63

Options: `--rounds 3` (re-recording rounds), `--takes 4` (new takes per beat per round), `--test` (the 3-beat
test render). It needs ffmpeg on PATH: the launchers add WanGP's `ffmpeg_bins`; from a command prompt run
`set PATH=C:\WanGP\ffmpeg_bins;%PATH%` first. `clean_voices.py` is replaced by it and no longer runs.

To redo a single illustration by hand: delete it from `stories/<series>/output/<ep>`, render that prompt again in the WanGP UI
(the batch file in `stories/<series>/batches` has every prompt), save it with the same name, and rerun
`python stories/tools/assemble_episode.py <script>`.

## Models
- Narration: Qwen3 TTS Custom Voice, preset speaker set in `cast.json` (same voice every episode), checked by
  review_voices.py with an AudioSet AST sound classifier and Whisper medium.en.
- Scenes with characters: Qwen Image Edit Plus (2511), with up to 3 reference pictures per scene.
- Scenes without recurring characters: Qwen Image (2512).
- Images render at 1280x720 and are shown at 1920x1080 with a slow zoom or pan.
- Assembly keeps uncompressed audio in each segment and makes every segment a whole number of frames, so the
  narration stays in step with the pictures and captions to the end of the episode.
