# Kids Nursery Rhyme Videos

Renders a sung nursery rhyme plus a 16:9 YouTube video and a 9:16 Short from one overnight run on your PC.

| Part | Model | Output |
|---|---|---|
| Song | ACE-Step 1.5 Turbo | 3 takes: `<song>_song_a/b/c` |
| Long video clips | Wan 2.2 VACE Lightning, 832x480 | `<song>_long_01..NN.mp4` |
| Short clips | Same prompts, 480x832 | `<song>_short_01..NN.mp4` |
| Final videos | `merge.py` (ffmpeg) | `final/<song>_long.mp4`, `final/<song>_short.mp4` |

## Before bed

1. Save your character image as `kids_videos/refs/old_macdonald.png`.
2. Double-click `kids_videos/render_overnight.bat`
   (or from the WanGP folder: `kids_videos\render_overnight.bat old_macdonald`).

It builds the batch, renders the 3 song takes and every clip, then merges the finished videos into `kids_videos/final`.

## In the morning

- Listen to the 3 song takes in `kids_videos/output`. If you prefer take `b` or `c`, re-merge with it:
  `python kids_videos/merge.py old_macdonald b`
- Optional: upscale the finished videos to 1080p with FlashVSR in WanGP's post-processing tab.
- Upload. Mark the videos **Made for Kids** and turn on the **altered or synthetic content** disclosure.

## Changing things

Everything is in `songs.py`: the lyrics, the music style, the character description (keep it matching your image), and one prompt per ~5 second clip. Run `python kids_videos/build_batch.py old_macdonald` after editing, or just run the overnight script again.

To redo a single bad clip, delete it from `kids_videos/output`, render that prompt again in the WanGP UI with the same seed, name it the same, and re-run `merge.py`.
