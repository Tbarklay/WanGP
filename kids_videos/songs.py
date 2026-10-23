"""Song definitions for the kids nursery rhyme videos.

Every song lists:
  - lyrics:  traditional public-domain words, tagged for ACE-Step
  - music:   ACE-Step caption describing the sound
  - seconds: song length; the merge script fits the clips to the real song
  - shots:   one prompt per ~5 second clip, in song order. The same prompt
             is rendered once in 16:9 (long video) and once in 9:16 (Short).
"""

# Shared look for the whole channel, so every video matches.
STYLE = (
    "Bright, colorful 3D animated children's cartoon, soft rounded friendly shapes, "
    "saturated cheerful colors, warm sunny lighting, smooth gentle motion, "
    "high quality kids TV animation"
)

NEGATIVE = (
    "scary, dark, creepy, violent, realistic photo, horror, sad, text, letters, "
    "subtitles, watermark, logo, blurry, low quality, deformed, extra limbs, "
    "distorted face, flickering"
)


OLD_MACDONALD = {
    "slug": "old_macdonald",
    "title": "Old MacDonald Had a Farm",
    "reference_image": "kids_videos/refs/old_macdonald.png",
    # Describes whoever is in the reference image; update it to match the image.
    "character": "Old MacDonald, a friendly cartoon farmer with a straw hat, "
                 "a red plaid shirt and blue overalls",
    "seconds": 120,
    "music": (
        "Traditional children's nursery rhyme, happy upbeat sing-along, "
        "cheerful clear male vocal with a children's choir on the E-I-E-I-O, "
        "banjo, acoustic guitar, fiddle, light hand claps, simple bouncy rhythm, "
        "116 BPM, major key, kids music"
    ),
    "lyrics": """[Verse 1]
Old MacDonald had a farm, E-I-E-I-O
And on his farm he had a cow, E-I-E-I-O
With a moo moo here and a moo moo there
Here a moo, there a moo, everywhere a moo moo
Old MacDonald had a farm, E-I-E-I-O

[Verse 2]
Old MacDonald had a farm, E-I-E-I-O
And on his farm he had a pig, E-I-E-I-O
With an oink oink here and an oink oink there
Here an oink, there an oink, everywhere an oink oink
Old MacDonald had a farm, E-I-E-I-O

[Verse 3]
Old MacDonald had a farm, E-I-E-I-O
And on his farm he had a duck, E-I-E-I-O
With a quack quack here and a quack quack there
Here a quack, there a quack, everywhere a quack quack
Old MacDonald had a farm, E-I-E-I-O

[Verse 4]
Old MacDonald had a farm, E-I-E-I-O
And on his farm he had a sheep, E-I-E-I-O
With a baa baa here and a baa baa there
Here a baa, there a baa, everywhere a baa baa
Old MacDonald had a farm, E-I-E-I-O

[Verse 5]
Old MacDonald had a farm, E-I-E-I-O
And on his farm he had a horse, E-I-E-I-O
With a neigh neigh here and a neigh neigh there
Here a neigh, there a neigh, everywhere a neigh neigh
Old MacDonald had a farm, E-I-E-I-O""",
    "shots": [
        # Intro
        "{character} waves hello in front of a big red barn on a sunny green farm, "
        "white picket fence, fluffy clouds, the camera slowly pushes in",

        # Verse 1: cow
        "{character} walks happily along a dirt path past the red barn, swinging his arms "
        "and singing, sunflowers sway in the breeze",
        "A cute friendly cartoon cow with black and white spots and a little bell trots "
        "out of the barn and stands next to {character}, who points at it with a big smile",
        "The cute spotted cow lifts its head and moos happily in a green meadow, "
        "{character} laughs and claps his hands beside it",
        "{character} and the spotted cow dance side by side in the meadow, "
        "bouncing to the music, butterflies flutter around them",

        # Verse 2: pig
        "{character} opens a wooden farm gate and sings, the camera tracks beside him, "
        "rolling green hills behind",
        "A chubby cute pink cartoon pig with a curly tail runs up to {character} "
        "near a small muddy puddle, he crouches down and smiles at it",
        "The cute pink pig wiggles its curly tail and oinks happily, splashing in "
        "a small mud puddle, {character} giggles",
        "{character} and the pink pig spin around together in a happy little dance "
        "beside the barn, hay bales in the background",

        # Verse 3: duck
        "{character} sings while walking beside a sparkling blue farm pond with lily pads, "
        "tall cattails, warm sunshine",
        "A cute fluffy yellow cartoon duck with an orange beak waddles out of the pond "
        "toward {character}, who kneels down and waves to it",
        "The cute yellow duck flaps its little wings and quacks happily on the edge of "
        "the pond, little ripples on the water, {character} flaps his arms like wings",
        "{character} and the yellow duck waddle together in a funny little march along "
        "the pond, both bobbing to the music",

        # Verse 4: sheep
        "{character} sings on top of a gentle grassy hill with a wooden windmill "
        "turning slowly behind him",
        "A cute round fluffy white cartoon sheep with a happy face bounces over the hill "
        "toward {character}, who opens his arms wide",
        "The cute fluffy sheep says baa with a big smile, its wool bouncing, "
        "{character} gently pats its fluffy head",
        "{character} and the fluffy sheep hop together across the hill in a playful dance, "
        "little daisies all around",

        # Verse 5: horse
        "{character} sings while leaning on a wooden fence beside a stable, "
        "golden hay and a bright blue sky",
        "A cute friendly brown cartoon horse with a golden mane trots up to the fence, "
        "{character} smiles and strokes its nose",
        "The cute brown horse tosses its golden mane and neighs happily, "
        "lifting one front hoof, {character} cheers",
        "{character} rides the cute brown horse at a gentle trot across the sunny meadow, "
        "waving happily",

        # Outro: everyone together
        "{character} stands in front of the red barn surrounded by all his cute animals, "
        "the spotted cow, the pink pig, the yellow duck, the fluffy sheep and the brown "
        "horse, everyone dances together",
        "{character} and all the cute farm animals wave goodbye in front of the red barn "
        "at golden sunset, the camera slowly pulls back",
    ],
}


SONGS = {song["slug"]: song for song in [OLD_MACDONALD]}
