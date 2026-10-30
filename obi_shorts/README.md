# Obi Shorts: animated 3D farm videos

Each shot is drawn as a keyframe from Obi's and the farmer's 3D references, then animated into a 5 second clip
with Wan 2.2 image-to-video. The clips are joined into a 1080p video plus a vertical Short.

## Once: the 3D characters
Double-click `obi_shorts\tools\make_refs.bat`. It makes 4 takes each of Obi and the farmer in 3D from the existing
2D pictures. Save the best ones as `obi_shorts\refs\obi_3d.png` and `obi_shorts\refs\farmer_3d.png`.

## Each video
1. Write the shots in a shot list like `test_shots.md`: a `[keyframe: ...]` picture and a `[motion: ...]` line per
   shot. One clear action per shot animates best.
2. Double-click `obi_shorts\tools\render_shots.bat` (or drag a shot list onto it).
3. Song videos: give the shot list `## Music` and `## Lyrics` sections (see `obi_farm_parade.md`). The launcher
   renders 3 takes of the song first and fits the clips to take `a`; to use another take, run
   `python obi_shorts\tools\assemble_shots.py <shot list> --song b`. Without lyrics, optional music can go in
   `obi_shorts\music.mp3` (YouTube Audio Library).
4. The video and the Short are in `obi_shorts\final`.

Redo a bad shot with new seeds: `python obi_shorts\tools\build_shots.py keyframes obi_shorts\test_shots.md --shots 2`
(or `animate ... --shots 2`), render the printed batch, and assemble again.

## Timing on an RTX 4070
About 2 minutes per keyframe and 5-10 minutes per 5 second clip: the 3-shot test is about 30 minutes, the
36-shot `obi_farm_parade.md` about 4-6 hours, so start it at night.
