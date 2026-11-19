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
