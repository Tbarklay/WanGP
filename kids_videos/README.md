# Kids Nursery Rhyme Videos

Renders a sung nursery rhyme plus a 16:9 YouTube video and a 9:16 Short from one overnight run on your PC.

| Part | Model | Output |
|---|---|---|
| Song | ACE-Step 1.5 Turbo | 3 takes: `<song>_song_a/b/c` |
| Long video clips | Wan 2.2 VACE Lightning, 832x480 | `<song>_long_01..NN.mp4` |
| Short clips | Same prompts, 480x832 | `<song>_short_01..NN.mp4` |
| Final videos | `merge.py` (ffmpeg) | `final/<song>_long.mp4`, `final/<song>_short.mp4` |

## Test first (about 5-10 minutes, plus the first model download)

Double-click `kids_videos/test_clip.bat`. It renders the first Old MacDonald clip with the farmer and dog reference
and opens the folder so you can check that both characters look right.

## Before bed

1. Put one reference image per song in `kids_videos/refs`:
   `farmer_and_dog.jpg` (already there), `five_little_ducks.jpg`, `itsy_bitsy_spider.jpg`,
   `twinkle_twinkle.jpg`, `alphabet_song.jpg`. A song without its image is made from the text only.
2. Double-click `kids_videos/render_overnight.bat` to render all five songs
   (or one song from the WanGP folder: `kids_videos\render_overnight.bat old_macdonald`).

It builds the batch, renders the 3 song takes of every song, then all the 16:9 clips, then all the 9:16 clips,
and merges the finished videos into `kids_videos/final`.

## In the morning

- Listen to the 3 song takes in `kids_videos/output`. If you prefer take `b` or `c`, re-merge with it:
  `python kids_videos/merge.py old_macdonald b`
- Optional: upscale the finished videos to 1080p with FlashVSR in WanGP's post-processing tab.
- Upload. Mark the videos **Made for Kids** and turn on the **altered or synthetic content** disclosure.

## Changing things

Everything is in `songs.py`: the lyrics, the music style, the character description (keep it matching your image), and one prompt per ~5 second clip. Run `python kids_videos/build_batch.py old_macdonald` after editing, or just run the overnight script again.

To redo a single bad clip, delete it from `kids_videos/output`, render that prompt again in the WanGP UI with the same seed, name it the same, and re-run `merge.py`.
