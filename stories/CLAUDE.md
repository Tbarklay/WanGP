# Manhwa recap stories: rules for every episode

- **No background music.** Narration and sound only. Don't pass --music to assemble_episode.py, and don't render
  or add music tracks for new episodes. (The owner doesn't like the background music.)
- Original stories and characters only: borrow genre conventions (systems, regression, hunters, revenge), never
  an existing manhwa's plot, characters, names or look.
- **Two voices:** the narrator, and the System (lines starting `SYSTEM:` in a script are read in the System's voice).
  Both are designed voices: make samples with `stories/tools/design_voice.py <series> narrator|system`, let the owner
  pick, save the pick as `refs/narrator.wav` / `refs/system.wav` and set `voice` and `voice_text` in cast.json.
  `[image: same]` keeps the previous picture on screen (used for System lines over the same scene).
- **On-screen text:** never ask the image model for readable text. Only **ranking boards** and **character stat
  windows** get text on screen, drawn exactly by the assembler: `[ui: ranking | ...]` and `[ui: status | ...]` after a
  beat's image tag (format in stories/tools/ui_overlay.py). **No pop-ups for the System's spoken lines**: her voice
  carries them. Keep the numbers consistent with the narration and earlier episodes.
- **Episodes and compilations:** each episode has a `## Cold open` and ends on a "Next time on..." beat. For a long
  compilation, assemble episode 1 with `--compilation first` and every later episode with `--compilation next` (drops
  the cold open and the "Next time" ending), then join them, so one episode flows straight into the next. No recaps of
  earlier episodes inside an episode.
- **Hair:** never put a hairstyle (spiky, messy...) in the style line; it applies to everyone. Each character's hair
  belongs in their own cast description.
- **Review copies** (the small file uploaded to GitHub): `ffmpeg -i final/<ep>.mp4 -vf scale=1280:-2 -c:v libx264 -preset slow
  -crf 26 -g 60 -movflags +faststart -c:a aac -b:a 128k final/<ep>_review.mp4`. The `-g 60 -movflags +faststart` part
  keeps it from freezing when streamed in a browser.
