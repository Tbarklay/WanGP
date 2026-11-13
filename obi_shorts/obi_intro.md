# Sing with Obi: intro card (about 3.5 seconds)

The channel's sound logo: the same 4-beat hook "Sing, sing, sing with O-bi!" + a woof, and the same Obi move, at
the start of every video, so kids learn to recognize it (like the big kids' channels do).

Put in front of every video by assemble_shots.py once obi_shorts/final/obi_intro.mp4 exists, so even videos
without Obi (like Five Little Ducks) open with him and the channel name. Kept short so kids don't skip away.

Make it once:
1. build_shots.py keyframes, then animate (one shot)
2. build_shots.py song: add --takes 6 for 6 jingle takes (a-f). Pick the catchiest
   one where "Sing, sing, sing with O-bi!" is clear; trim it so the singing starts within 0.3 s and the woof lands
   by 3.5 s, and save it as obi_shorts/output/obi_intro/jingle.wav. Keep this file: the outro reuses its hook.
3. assemble_shots.py obi_shorts/obi_intro.md --music obi_shorts/output/obi_intro/jingle.wav --length 3.5 --no-intro

## Music
Super catchy short children's TV show jingle, a bright sing-song hook that starts right away, a cheerful children's
choir sings "Sing, sing, sing with O-bi!" on four bouncy notes going up, then a happy puppy woof, bright ukulele
strum, glockenspiel sparkle, hand claps, major key, 120 BPM, kids music

## Lyrics
[Jingle]
Sing, sing, sing with O-bi!

## Shots

**01** `[keyframe: {obi} popping up from behind a round golden hay bale in the bottom half of the picture, front paws on top of the bale, waving one paw at the camera with a big happy open-mouth smile, soft floppy ears, sunny green farm with a red barn far behind, the whole top half of the picture is clear bright blue sky with a few puffy clouds]`
`[motion: the puppy pops up from behind the hay bale, bounces happily three times to the beat, then waves his paw at the camera and barks, ears bouncing softly, camera still]`
`[title: Sing with Obi]`
