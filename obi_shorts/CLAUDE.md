# Sing with Obi: rules for every video

These come from the channel's analytics: thumbnails and titles already get clicked (6-11% CTR), but kids leave
after 35-55 seconds (21-32% average viewed). Retention is what makes YouTube keep recommending a video. The best
retention so far is the rain-rescue video (61%, a real story with a problem to solve each verse) and the 20-minute
compilation (59%). Follow these rules when writing or rendering any Obi video.

## Writing a shot list
1. **The song starts within 3 seconds.** No slow scenery or empty establishing shots, no long instrumental intro.
   Shot 01 already shows characters doing something fun (the intro card plays before it).
2. **Obi is in every video**, and early. A song without him as the star still gets him in a shot or two, and the
   intro and goodbye cards always show him.
3. **A mini story every verse**: a small problem, an attempt, a funny payoff (like the rain rescue), not just
   "here is the animal".
4. **Something new every 2-3 seconds**: a new angle, a gag, a sound effect, an expression. Most shots are one
   clear action, and shots on the same line alternate wide and close-up.
5. **Follow-along songs** (actions kids copy): while the action is sung, keep ONE steady shot of the characters
   facing the camera doing it, with no cutaways, so kids always have someone to copy.
6. **Counting songs**: numbers belong to characters (numbered, colored outfits), and the counted one acts on its
   number. Never put numbers over faces.
7. Keep the look consistent: Obi's ears stay soft and floppy, every character uses its reference picture from
   cast.json, and plain areas are left where overlays go (sky at the top for [spell:], a wall corner for [count:]).
8. Classic public-domain songs parents search for, or originals with the same pull. Titles: "Song Name! 🐶 hook |
   ... | Sing with Obi".

Run `python obi_shorts/tools/build_shots.py check <shot list>` after writing: it warns about the mistakes above
that can be spotted in the text.

## Rendering and assembling
- Never hold or freeze a frame to fill time. If a clip is shorter than its slot (lip-synced lines often are), cut
  to the next shot early or add a shot. assemble_shots.py runs a frozen-frame check on every video it writes and
  prints the times to fix.
- Lip-synced shots play at normal speed, starting exactly on their line.
- The intro jingle (cards/obi_intro.mp4) and the goodbye card (cards/obi_outro.mp4) are added automatically to
  every long video, never to Shorts. cards/obi_intro_alt_own_sound.mp4 is the same intro with the other jingle take.
- Before uploading, make a per-second contact sheet and check every shot: no extra characters, no text in the
  picture, no strangers, ears floppy, nothing frozen.
- Upload each video as a GitHub release on Tbarklay/kids-videos, with notes on what was fixed.
