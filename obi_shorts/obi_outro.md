# Sing with Obi: goodbye card (about 10 seconds)

Put at the end of every video by assemble_shots.py once obi_shorts/final/obi_outro.mp4 exists. Obi waves goodbye on
the left; the right half is left plain so YouTube's end screen fits there: in YouTube Studio add a Subscribe
element and a "Best for viewer" video (or a playlist) over the last 10 seconds of every video. The singer sings
"Like and subscribe to Sing with Obi!" while parents can tap the button right there.

Make it once:
1. build_shots.py keyframes, then animate (two shots)
2. build_shots.py song --takes 6. Pick one that sings the words clearly and ends with the same
   "Sing, sing, sing with O-bi!" hook as the intro jingle; save it as obi_shorts/output/obi_outro/outro.wav
3. assemble_shots.py obi_shorts/obi_outro.md --music obi_shorts/output/obi_outro/outro.wav --length 10 --no-intro

## Music
Warm happy children's TV show goodbye song, friendly female vocal, a cheerful children's choir on the last line,
the same bouncy four-note "Sing, sing, sing with O-bi!" hook going up as the show's intro, bright ukulele strum,
glockenspiel sparkle, soft hand claps, a happy puppy woof at the very end, major key, 120 BPM, kids music

## Lyrics
[Outro]
Bye-bye, friends, see you soon!
Like and subscribe to Sing with O-bi!
Sing, sing, sing with O-bi!

## Shots

**01** `[keyframe: {obi} sitting on the left side of the picture on soft green grass in front of a red barn at golden hour, waving one paw at the camera with a big warm smile, soft floppy ears, the whole right half of the picture is plain soft green meadow and clear sky with nothing in it]`
`[motion: the puppy waves goodbye to the camera with one paw and wags his tail, ears staying floppy, camera still]`

**02** `[keyframe: {obi} lying down on the left side of the picture on soft green grass in front of a red barn at golden hour, giving a big happy wink at the camera, soft floppy ears, the whole right half of the picture is plain soft green meadow and clear sky with nothing in it]`
`[motion: the puppy winks, barks once happily and blows a little kiss with his paw, camera still]`
