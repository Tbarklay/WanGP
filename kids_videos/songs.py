"""Song definitions for the kids nursery rhyme videos.

Every song lists:
  - lyrics:  traditional public-domain words, tagged for ACE-Step
  - music:   ACE-Step caption describing the sound
  - seconds: song length; the merge script fits the clips to the real song
  - shots:   one prompt per ~5 second clip, in song order. The same prompt
             is rendered once in 16:9 (long video) and once in 9:16 (Short).
"""

# Shared look for the whole channel, matching the reference illustrations.
STYLE = (
    "Hand-drawn children's storybook illustration come to life, clean ink outlines, "
    "soft colored-pencil and watercolor shading, bright cheerful colors, sunny blue sky "
    "with puffy white clouds, green rolling hills, red barn with a silo, wooden fences, "
    "dirt farm path with colorful wildflowers, gentle smooth 2D animation"
)

NEGATIVE = (
    "scary, dark, creepy, violent, realistic photo, 3D render, horror, sad, angry, text, "
    "letters, subtitles, watermark, logo, signature, blurry, low quality, deformed, "
    "extra limbs, extra dogs, distorted face, flickering"
)

FARMER = (
    "Old MacDonald, a kind smiling elderly farmer with a short white beard and gray hair, "
    "a dark gray cap, a red and brown plaid flannel shirt with rolled sleeves, faded "
    "muddy blue denim overalls and brown work boots"
)
DOG = (
    "Obi, Old MacDonald's fluffy shaggy black and tan puppy with a white chest patch, floppy ears "
    "and a happy pink tongue"
)


OLD_MACDONALD = {
    "slug": "old_macdonald",
    "title": "Old MacDonald Had a Farm",
    # Farmer and dog together; VACE keeps both looking the same in every clip.
    "reference_image": "kids_videos/refs/farmer_and_dog.jpg",
    "character": FARMER,
    "dog": DOG,
    "seconds": 120,
    "music": (
        "Traditional children's nursery rhyme, happy upbeat sing-along, "
        "warm friendly male vocal with a children's choir on the E-I-E-I-O, "
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
And on his farm he had a dog, E-I-E-I-O
With a woof woof here and a woof woof there
Here a woof, there a woof, everywhere a woof woof
Old MacDonald had a farm, E-I-E-I-O""",
    "shots": [
        # Intro
        "{character} stands on the dirt path in front of the red barn with {dog} sitting "
        "beside him, he waves hello and the dog wags its tail, the camera slowly pushes in",

        # Verse 1: cow
        "{character} walks happily along the dirt path past the red barn, swinging his arms "
        "and singing, {dog} trots beside him, wildflowers sway in the breeze",
        "A cute friendly black and white spotted cow with a little bell walks up to the "
        "wooden fence, {character} points at it with a big smile while {dog} looks up at it",
        "The cute spotted cow lifts its head and moos happily in the green meadow, "
        "{character} laughs and claps his hands, {dog} tilts its head",
        "{character} and the spotted cow sway side by side in the meadow, bouncing to the "
        "music, {dog} hops around them, butterflies flutter by",

        # Verse 2: pig
        "{character} opens a wooden farm gate and sings, {dog} runs through ahead of him, "
        "rolling green hills behind",
        "A chubby cute pink pig with a curly tail trots up to {character} near a small "
        "muddy puddle, he crouches down and smiles at it, {dog} sniffs the pig's nose",
        "The cute pink pig wiggles its curly tail and oinks happily, splashing in the small "
        "mud puddle, {character} chuckles and {dog} jumps back playfully",
        "{character}, the pink pig and {dog} turn around together in a happy little dance "
        "beside the red barn, hay bales in the background",

        # Verse 3: duck
        "{character} sings while walking beside a sparkling blue farm pond with lily pads "
        "and tall cattails, {dog} follows close behind",
        "A cute fluffy white duck with an orange beak waddles out of the pond toward "
        "{character}, who kneels down and waves to it, {dog} wags its tail",
        "The cute white duck flaps its wings and quacks happily at the edge of the pond, "
        "little ripples on the water, {character} flaps his arms like wings",
        "{character}, the white duck and {dog} march together in a funny little parade "
        "along the pond, all bobbing to the music",

        # Verse 4: sheep
        "{character} sings on top of a gentle grassy hill, {dog} sits beside him, "
        "a few hens peck in the grass nearby",
        "A cute round fluffy white sheep with a happy face trots over the hill toward "
        "{character}, who opens his arms wide, {dog} runs to greet it",
        "The cute fluffy sheep says baa with a big smile, its wool bouncing, "
        "{character} gently pats its fluffy head",
        "{character} and the fluffy sheep hop together across the hill in a playful dance, "
        "{dog} bounces between them, daisies all around",

        # Verse 5: dog
        "{character} sings and kneels down on the dirt path, {dog} runs toward him "
        "with its tail wagging, chickens scatter playfully",
        "{character} gently pats the head of {dog}, who sits proudly beside him, "
        "in front of the red barn and silo",
        "{dog} barks woof woof happily, bouncing on its front paws, "
        "{character} laughs and claps",
        "{dog} runs happy circles around {character} on the dirt path, "
        "ears flopping, butterflies all around",

        # Outro: everyone together
        "{character} and {dog} stand in front of the red barn with the spotted cow, the pink "
        "pig, the white duck and the fluffy sheep, everyone dances together",
        "{character}, {dog} and all the cute farm animals wave goodbye in front of the red "
        "barn under a warm golden sunset, the camera slowly pulls back",
    ],
}


SONGS = {song["slug"]: song for song in [OLD_MACDONALD]}
