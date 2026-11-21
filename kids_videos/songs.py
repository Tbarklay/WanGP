"""Song definitions for the kids nursery rhyme videos.

Every song lists:
  - lyrics:  traditional public-domain words, tagged for ACE-Step
  - music:   ACE-Step caption describing the sound
  - seconds: song length; the merge script fits the clips to the real song
  - style:   the look and setting added in front of every clip prompt
  - cast:    character descriptions, inserted into the shots as {name}
  - refs:    one reference picture per cast member ({name} -> image). A shot's keyframe
             is drawn from the pictures of the characters it names, so a shot with only
             the cow never sees the dog's picture.
  - shots:   one prompt per ~5 second clip, in song order. Each shot is first drawn as a
             keyframe picture, then animated. The same prompt is drawn once in 16:9
             (long video) and once in 9:16 (Short).
"""

# Shared look for the whole channel, matching the bold reference illustrations.
ILLUSTRATION = (
    "Bold hand-drawn cartoon storybook illustration, thick dark ink outlines, "
    "vivid saturated colors, strong contrast, crisp clean coloring, bright cheerful daylight"
)


# Matches the colored-pencil reference pictures (ducks, spider, star, bear).
PENCIL = (
    "Hand-drawn colored-pencil children's storybook illustration, clean dark pencil outlines, "
    "rich warm saturated colors, solid even coloring, clear contrast, bright cheerful daylight"
)


def look(setting, art=ILLUSTRATION):
    return f"{art}, {setting}"


NEGATIVE = (
    "washed out, pale, pastel, faded, low contrast, overexposed, hazy, white haze, "
    "hybrid animal, animal with dog features, two animals merged, "
    "scary, dark, creepy, violent, realistic photo, 3D render, horror, sad, angry, text, "
    "letters, subtitles, watermark, logo, signature, blurry, low quality, deformed, "
    "extra limbs, extra dogs, duplicate characters, distorted face, flickering"
)

# Added to every animation prompt: the keyframe already sets the look, this keeps it.
MOTION = ("smooth gentle cartoon animation, characters keep facing the viewer, "
          "keep the exact colors, outlines and characters of the image")


# ---------------------------------------------------------------------------
# Old MacDonald Had a Farm
# ---------------------------------------------------------------------------

FARMER = (
    "Old MacDonald, a kind smiling elderly farmer with a short white beard and gray hair, "
    "a dark gray cap, a red and brown plaid flannel shirt with rolled sleeves, faded "
    "muddy blue denim overalls and brown work boots"
)
DOG = (
    "Old MacDonald's small scruffy long-haired black and tan doodle dog with messy shaggy fur, "
    "long droopy furry ears hanging down, a shaggy tan beard, a white chest patch "
    "and a happy pink tongue"
)

OLD_MACDONALD = {
    "slug": "old_macdonald",
    "title": "Old MacDonald Had a Farm",
    "style": look(
        "sunny blue sky with puffy white clouds, green rolling hills, red barn with a silo, "
        "wooden fences, dirt farm path with colorful wildflowers"
    ),
    # Separate pictures so each character copies its own reference.
    # farmer.jpg is made from farmer_and_dog.jpg by the first keyframe run.
    "refs": {"character": "kids_videos/refs/farmer.jpg", "dog": "kids_videos/refs/dog.jpg"},
    "cast": {"character": FARMER, "dog": DOG},
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
        # The dog stays out of the animal shots, so it can't blend into the new animal.
        "A cute friendly black and white spotted dairy cow with horns, a pink nose and a "
        "little cowbell walks up to the wooden fence, {character} points at it with a big smile",
        "The cute spotted dairy cow lifts its head and moos happily in the green meadow, "
        "{character} laughs and claps his hands",
        "{character} and the spotted dairy cow sway side by side in the meadow, bouncing to "
        "the music, butterflies flutter by",

        # Verse 2: pig
        "{character} opens a wooden farm gate and sings, {dog} runs through ahead of him, "
        "rolling green hills behind",
        "A chubby cute pink pig with a curly tail trots up to {character} near a small "
        "muddy puddle, he crouches down and smiles at it",
        "The cute pink pig wiggles its curly tail and oinks happily, splashing in the small "
        "mud puddle, {character} chuckles",
        "{character} and the pink pig turn around together in a happy little dance "
        "beside the red barn, hay bales in the background",

        # Verse 3: duck
        "{character} sings while walking beside a sparkling blue farm pond with lily pads "
        "and tall cattails, {dog} follows close behind",
        "A cute fluffy white duck with an orange beak waddles out of the pond toward "
        "{character}, who kneels down and waves to it",
        "The cute white duck flaps its wings and quacks happily at the edge of the pond, "
        "little ripples on the water, {character} flaps his arms like wings",
        "{character} and the white duck march together in a funny little parade "
        "along the pond, both bobbing to the music",

        # Verse 4: sheep
        "{character} sings on top of a gentle grassy hill, {dog} sits beside him, "
        "a few hens peck in the grass nearby",
        "A cute round fluffy white sheep with a black face and a happy smile trots over the "
        "hill toward {character}, who opens his arms wide",
        "The cute fluffy sheep says baa with a big smile, its wool bouncing, "
        "{character} gently pats its fluffy head",
        "{character} and one single fluffy sheep, the only sheep in the picture, hop together across the hill in a playful dance, "
        "daisies all around",

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
        "{character} and {dog} stand in front of the red barn, with the spotted dairy cow, "
        "the pink pig, the white duck and the fluffy sheep standing apart in a row beside "
        "them, everyone dances together",
        "{character} and {dog}, the only dog in the picture, wave goodbye with one spotted dairy cow, one pink pig, one white duck and one fluffy sheep in front of the red "
        "barn under a warm golden sunset, the camera slowly pulls back",
    ],
}


# ---------------------------------------------------------------------------
# Five Little Ducks
# ---------------------------------------------------------------------------

MOTHER_DUCK = (
    "Mother Duck, a plump friendly white duck with a bright orange beak and orange feet, "
    "wearing a small light blue bonnet with a ribbon"
)
DUCKLINGS = "fluffy round bright yellow ducklings with tiny orange beaks"

FIVE_LITTLE_DUCKS = {
    "slug": "five_little_ducks",
    "title": "Five Little Ducks",
    # Mother and one duckling cropped apart, so a shot only gets the birds it names
    # (the full picture made ducklings appear in Mother Duck's solo shots).
    "refs": {"mother": "kids_videos/refs/mother_duck.jpg", "ducklings": "kids_videos/refs/duckling.jpg"},
    "style": look(
        "sunny blue sky with puffy white clouds, a sparkling blue pond with lily pads and "
        "tall cattails, soft green rolling hills, little wooden bridge, colorful wildflowers",
        PENCIL,
    ),
    "cast": {"mother": MOTHER_DUCK, "ducklings": DUCKLINGS},
    "seconds": 95,
    "music": (
        "Traditional children's nursery rhyme, gentle happy sing-along, "
        "sweet warm female vocal with a children's choir on the quack quack quack quack, "
        "ukulele, glockenspiel, soft acoustic guitar, light hand claps, "
        "100 BPM, major key, kids music"
    ),
    "lyrics": """[Verse 1]
Five little ducks went out one day
Over the hills and far away
Mother duck said, quack quack quack quack
But only four little ducks came back

[Verse 2]
Four little ducks went out one day
Over the hills and far away
Mother duck said, quack quack quack quack
But only three little ducks came back

[Verse 3]
Three little ducks went out one day
Over the hills and far away
Mother duck said, quack quack quack quack
But only two little ducks came back

[Verse 4]
Two little ducks went out one day
Over the hills and far away
Mother duck said, quack quack quack quack
But only one little duck came back

[Verse 5]
One little duck went out one day
Over the hills and far away
Mother duck said, quack quack quack quack
But none of the five little ducks came back

[Verse 6]
Mother duck went out one day
Over the hills and far away
Mother duck said, quack quack quack quack
And all of the five little ducks came back""",
    "shots": [
        # Intro
        "{mother} stands proudly at the edge of the pond with exactly five {ducklings} lined up "
        "behind her, they all wave their little wings hello, the camera slowly pushes in",

        # Verse 1: five go out
        "Exactly five {ducklings} waddle in a happy line along the dirt path toward the green hills, "
        "wings flapping, wildflowers swaying",
        "{mother} stands by the pond and calls out quack quack with her beak wide open, "
        "wings cupped by her face, all alone with no ducklings anywhere in the picture",
        "Exactly four {ducklings} waddle back down the grassy hill toward the pond, "
        "{mother} counts them with her wing and tilts her head curiously",

        # Verse 2: four go out
        "Exactly four {ducklings} hop over a little wooden bridge and wander off toward the hills, "
        "bouncing happily",
        "{mother} calls quack quack across the meadow, a butterfly lands on her bonnet, all alone with no ducklings anywhere in the picture",
        "Exactly three {ducklings} come tumbling back over the hill, rolling playfully in the grass, "
        "{mother} smiles and gathers them close",

        # Verse 3: three go out
        "Exactly three {ducklings} splash across a shallow stream and waddle toward the far hills, "
        "the sun shining brightly",
        "{mother} stands on a little rock and calls quack quack, her bonnet ribbon "
        "fluttering in the breeze, all alone with no ducklings anywhere in the picture",
        "Exactly two {ducklings} slide down a grassy hill and land giggling at the feet of {mother}",

        # Verse 4: two go out
        "Exactly two {ducklings} waddle side by side through tall colorful wildflowers toward the hills",
        "{mother} sits by the pond and calls quack quack, dragonflies dancing over the water, all alone with no ducklings anywhere in the picture",
        "Exactly one fluffy yellow duckling hops back along the dirt path and snuggles under the "
        "wing of {mother}",

        # Verse 5: one goes out
        "Exactly one fluffy yellow duckling waddles bravely alone over the green hill, "
        "turning back to wave its little wing",
        "{mother} looks over the empty pond and calls quack quack, holding her wings to her "
        "beak, a gentle breeze in the cattails, all alone with no ducklings anywhere in the picture",

        # Verse 6: mother goes out and everyone comes back
        "{mother} waddles up the green hill and calls a big loud quack quack, "
        "her wings spread wide",
        "Exactly five {ducklings} come running and tumbling happily over the hilltop toward {mother}, "
        "flapping their little wings",

        # Outro
        "{mother} and exactly five {ducklings} swim together in a happy line across the sparkling "
        "pond under a warm golden sunset, the camera slowly pulls back",
    ],
}


# ---------------------------------------------------------------------------
# Itsy Bitsy Spider
# ---------------------------------------------------------------------------

SPIDER = (
    "Itsy, a tiny cute friendly cartoon spider no bigger than a sunflower blossom, with a round "
    "soft fuzzy purple body, big friendly sparkly eyes, a happy smile and rosy cheeks, two little "
    "purple arms with tiny waving hands and six short stubby purple legs wearing tiny pink and "
    "white sneakers"
)

ITSY_BITSY_SPIDER = {
    "slug": "itsy_bitsy_spider",
    "title": "Itsy Bitsy Spider",
    "refs": {"spider": "kids_videos/refs/itsy_bitsy_spider.jpg"},
    # Wide views keep Itsy small next to the spout; the first version drew him huge and close.
    "style": look(
        "a wide view of a cozy cottage garden, a tall blue rain downspout pipe running from the "
        "roof gutter down the white cottage wall, sunflowers and tulips, green grass, puffy clouds",
        PENCIL,
    ),
    "negative": NEGATIVE + ", giant spider, huge spider, extreme close-up, scary hairy spider, "
                "black spider, dark face, mud, dirt, person, people, child, man, woman, human",
    "cast": {"spider": SPIDER},
    "seconds": 45,
    "music": (
        "Traditional children's nursery rhyme, sweet gentle sing-along, "
        "soft warm female vocal with a children's choir, "
        "music box, xylophone, soft acoustic guitar, light shaker, "
        "96 BPM, major key, kids music"
    ),
    "lyrics": """[Verse 1]
The itsy bitsy spider climbed up the water spout
Down came the rain and washed the spider out
Out came the sun and dried up all the rain
And the itsy bitsy spider climbed up the spout again

[Verse 2]
The itsy bitsy spider climbed up the water spout
Down came the rain and washed the spider out
Out came the sun and dried up all the rain
And the itsy bitsy spider climbed up the spout again""",
    "shots": [
        # Verse 1
        "{spider}, the only spider in the picture and tiny next to the tall blue downspout, sits "
        "at the bottom of the downspout and waves hello at the viewer",
        "{spider}, tiny and the only spider in the picture, clings to the side of the tall blue downspout halfway up, holding on with "
        "its little hands, its smiling face toward the viewer",
        "Gentle cartoon raindrops fall from a soft gray cloud and a little stream of rainwater "
        "pours out of the bottom of the tall blue downspout, {spider}, tiny, sits on a big green "
        "leaf beside it, looking up in surprise",
        "The big round smiling sun peeks out from behind the clouds over the cottage garden, "
        "the last raindrops sparkling, flowers gently swaying, no people anywhere, the garden stays empty and peaceful",
        "{spider}, tiny, sits on a big green leaf next to the tall blue downspout, smiling and "
        "waving both little hands in the warm sunshine",

        # Verse 2
        "{spider}, tiny and the only spider in the picture, clings to the side of the tall blue downspout near the top, butterflies "
        "fluttering around, smiling at the viewer",
        "Soft rain falls again, {spider}, tiny, sits on a green leaf beside the tall blue "
        "downspout holding a red flower petal over its head like an umbrella, giggling",
        "A colorful rainbow appears over the sunny cottage garden, {spider}, tiny, sits on top "
        "of a big sunflower and waves both little hands at the viewer",
        "{spider}, tiny, sits on top of the tall blue downspout by the cottage roof and waves "
        "goodbye under the rainbow, the camera slowly pulls back",
    ],
}


# ---------------------------------------------------------------------------
# Twinkle Twinkle Little Star
# ---------------------------------------------------------------------------

STAR = (
    "Twinkle, a cute glowing golden-yellow cartoon star with a sweet sleepy smile, big "
    "kind eyes and rosy cheeks, softly sparkling"
)
CHILD = (
    "a sleepy little child with fluffy curly brown hair and rosy cheeks, in light blue "
    "footed pajamas with white stars, hugging a soft brown teddy bear"
)

TWINKLE_TWINKLE = {
    "slug": "twinkle_twinkle",
    "title": "Twinkle Twinkle Little Star",
    # Star and child cropped apart, so the star's solo shots don't get the child too.
    "refs": {"star": "kids_videos/refs/star.jpg", "child": "kids_videos/refs/child.jpg"},
    # Night scenes: the shared negative prompt's "dark" would fight the night sky.
    "negative": NEGATIVE.replace("scary, dark, creepy", "scary, creepy, pitch black"),
    "style": look(
        "calm deep blue night sky full of tiny twinkling stars, one single smiling crescent moon, "
        "soft glowing clouds, sleepy rolling hills with a cozy cottage with warm lit windows",
        PENCIL,
    ),
    "cast": {"star": STAR, "child": CHILD},
    "seconds": 55,
    "music": (
        "Traditional children's lullaby, soft gentle and calm, "
        "sweet tender female vocal, music box, celesta, soft piano, "
        "gentle strings, 80 BPM, major key, kids music, bedtime"
    ),
    "lyrics": """[Verse 1]
Twinkle, twinkle, little star
How I wonder what you are
Up above the world so high
Like a diamond in the sky
Twinkle, twinkle, little star
How I wonder what you are

[Verse 2]
When the blazing sun is gone
When he nothing shines upon
Then you show your little light
Twinkle, twinkle, all the night
Twinkle, twinkle, little star
How I wonder what you are""",
    "shots": [
        # Verse 1
        "{star} slowly appears high in the night sky and sparkles softly, "
        "the camera gently drifts upward",
        "{child} looks out of the cottage window at the sky, resting chin on hands, "
        "eyes full of wonder",
        "{star} floats gently above the sleepy rolling hills, little sparkles trailing "
        "behind like glitter, the thin crescent moon stays exactly the same crescent shape",
        "{star} twinkles like a shining diamond next to the smiling crescent moon, "
        "soft clouds drifting by",
        "{child} waves up at the sky from the window and {star} waves back with a soft glow",
        "{star} bobs gently up and down and twinkles, sending tiny sparkles all over the night sky",

        # Verse 2
        "A warm orange sunset glows behind the sleepy rolling hills, the sky above turning "
        "a calm deep blue with the first tiny stars",
        "{star} begins to glow brighter and brighter as the first stars appear around it",
        "{star} floats down gently and shines a soft warm light through the cottage "
        "window onto {child}",
        "{child} lies tucked in a cozy bed hugging the teddy bear, eyes slowly closing, {star} glows softly "
        "outside the window",
        "{star} twinkles softly over the sleeping cottage as the camera slowly pulls back "
        "into the starry sky",
    ],
}


# ---------------------------------------------------------------------------
# The Alphabet Song (same tune as Twinkle Twinkle)
# ---------------------------------------------------------------------------

BEAR = (
    "Benny, a cute small cuddly fuzzy honey-tan teddy bear cub with round ears, a cream "
    "muzzle and tummy, a little brown nose, a big happy smile and a red bow tie"
)

ALPHABET_SONG = {
    "slug": "alphabet_song",
    "title": "The Alphabet Song",
    "refs": {"bear": "kids_videos/refs/alphabet_song.jpg"},
    "style": look(
        "a bright cozy playroom with rainbow colored toy blocks, crayons, balloons, "
        "a big sunny window and cheerful colorful walls",
        PENCIL,
    ),
    "cast": {"bear": BEAR},
    "seconds": 50,
    "music": (
        "Traditional children's alphabet song sung to the melody of Twinkle Twinkle Little "
        "Star, happy clear and slow so every letter is easy to hear, cheerful female vocal "
        "with a children's choir, xylophone, glockenspiel, soft piano, light hand claps, "
        "92 BPM, major key, kids music, educational"
    ),
    # Sung twice so the video is long enough to learn along.
    "lyrics": """[Verse 1]
A, B, C, D, E, F, G
H, I, J, K, L, M, N, O, P
Q, R, S, T, U, V
W, X, Y and Z
Now I know my A B Cs
Next time won't you sing with me

[Verse 2]
A, B, C, D, E, F, G
H, I, J, K, L, M, N, O, P
Q, R, S, T, U, V
W, X, Y and Z
Now I know my A B Cs
Next time won't you sing with me""",
    "shots": [
        # Verse 1
        "{bear} waves hello in the middle of the bright playroom, surrounded by rainbow "
        "colored toy blocks, the camera slowly pushes in",
        "{bear} happily stacks colorful toy blocks into a tall tower, one by one, "
        "bouncing to the music",
        "{bear} dances and claps in front of a big sunny window, colorful balloons "
        "floating around",
        "{bear} hops from one big colorful soft play mat to the next, giggling",
        "{bear} sits proudly next to a tall rainbow tower of toy blocks and claps happily",

        # Verse 2
        "{bear} invites the viewer to sing along, waving both arms and smiling, "
        "confetti gently falling",
        "{bear} draws colorful swirls on a big paper with crayons, swaying to the music",
        "{bear} bounces on a soft rainbow cushion while balloons float up around him",
        "{bear} hugs a big stack of colorful toy blocks and sways happily side to side",
        "{bear} waves goodbye in the cozy playroom as warm sunlight fills the room, "
        "the camera slowly pulls back",
    ],
}


# ---------------------------------------------------------------------------
# Mary Had a Little Lamb
# ---------------------------------------------------------------------------

MARY = (
    "Mary, a sweet little girl with long golden-blonde braids tied with pink ribbons, "
    "rosy cheeks and freckles, wearing a light blue dress with a white apron, white socks "
    "and red shoes"
)
LAMB = (
    "Mary's little lamb, a small fluffy lamb with bright snow-white curly fleece, a cream "
    "face, shiny black button eyes, little pink ears and a pink ribbon bow around its neck"
)

MARY_HAD_A_LITTLE_LAMB = {
    "slug": "mary_had_a_little_lamb",
    "title": "Mary Had a Little Lamb",
    # Separate pictures, so the lamb's solo shots don't get Mary too.
    "refs": {"mary": "kids_videos/refs/mary.jpg", "lamb": "kids_videos/refs/lamb.jpg"},
    "style": look(
        "sunny countryside with green meadows full of daisies, a winding dirt path, "
        "a little red schoolhouse with a bell tower and a white picket fence, puffy white clouds",
        PENCIL,
    ),
    "cast": {"mary": MARY, "lamb": LAMB},
    "seconds": 60,
    "music": (
        "Traditional children's nursery rhyme, sweet cheerful sing-along, "
        "gentle warm female vocal with a children's choir, acoustic guitar, glockenspiel, "
        "soft piano, light hand claps, 100 BPM, major key, kids music"
    ),
    "lyrics": """[Verse 1]
Mary had a little lamb, little lamb, little lamb
Mary had a little lamb, its fleece was white as snow

[Verse 2]
And everywhere that Mary went, Mary went, Mary went
Everywhere that Mary went, the lamb was sure to go

[Verse 3]
It followed her to school one day, school one day, school one day
It followed her to school one day, which was against the rule

[Verse 4]
It made the children laugh and play, laugh and play, laugh and play
It made the children laugh and play to see a lamb at school""",
    "shots": [
        # Verse 1: Mary and her lamb
        "{mary} stands in the sunny meadow hugging {lamb}, both smiling at the viewer, "
        "the camera slowly pushes in",
        "{lamb}, the only lamb in the picture, stands alone in the green meadow, its "
        "snow-white curly fleece bright and fluffy, wiggling its little tail and smiling at the viewer",
        "{mary} gently pats the fluffy head of {lamb}, both facing the viewer and smiling, "
        "daisies all around",

        # Verse 2: everywhere that Mary went
        "{mary} skips happily along the winding path toward the viewer with {lamb} "
        "trotting right beside her",
        "{mary} walks across a little wooden bridge over a sparkling stream toward the viewer, "
        "{lamb} trotting close beside her",
        "{mary} sits on a wooden swing under a big apple tree, {lamb} sitting on the grass "
        "beside her, both smiling at the viewer",

        # Verse 3: followed her to school
        "{mary} walks up the path to the little red schoolhouse carrying her school books, "
        "{lamb} trotting happily beside her, both facing the viewer",
        "{lamb}, the only lamb in the picture, peeks out of the open red schoolhouse door "
        "with a curious happy smile, facing the viewer",
        "Inside a cozy sunny classroom, {mary} sits at her wooden school desk and {lamb} "
        "stands right beside the desk, both smiling at the viewer",

        # Verse 4: made the children laugh and play
        "Inside the sunny classroom, exactly three happy children laugh and clap, facing the "
        "viewer, while {lamb} does a happy little hop in front of them",
        "{mary} and {lamb} play in the sunny schoolyard with exactly two other smiling "
        "children, everyone facing the viewer",
        "{mary} hugs {lamb} in the meadow under a warm golden sunset, both waving goodbye, "
        "the camera slowly pulls back",
    ],
}


# ---------------------------------------------------------------------------
# Row, Row, Row Your Boat (stars Benny the bear from the Alphabet Song)
# ---------------------------------------------------------------------------

ROW_YOUR_BOAT = {
    "slug": "row_your_boat",
    "title": "Row, Row, Row Your Boat",
    "refs": {"bear": "kids_videos/refs/alphabet_song.jpg"},
    "style": look(
        "a calm sparkling blue stream winding through a sunny green forest, colorful "
        "wildflowers on the banks, gentle hills, a little red wooden rowboat",
        PENCIL,
    ),
    "cast": {"bear": BEAR},
    "seconds": 48,
    "music": (
        "Traditional children's nursery rhyme, gentle happy sing-along with a rocking "
        "boat rhythm, warm female vocal with a children's choir, ukulele, acoustic guitar, "
        "soft accordion, glockenspiel, 96 BPM, major key, kids music"
    ),
    # The traditional verse, sung four times like a playful round.
    "lyrics": """[Verse 1]
Row, row, row your boat
Gently down the stream
Merrily, merrily, merrily, merrily
Life is but a dream

[Verse 2]
Row, row, row your boat
Gently down the stream
Merrily, merrily, merrily, merrily
Life is but a dream

[Verse 3]
Row, row, row your boat
Gently down the stream
Merrily, merrily, merrily, merrily
Life is but a dream

[Verse 4]
Row, row, row your boat
Gently down the stream
Merrily, merrily, merrily, merrily
Life is but a dream""",
    # Benny rows facing the viewer the whole way, so the camera never sees his back.
    "shots": [
        "{bear} sits in a little red wooden rowboat on the sparkling stream holding two oars, "
        "waving hello at the viewer",
        "{bear} gently rows the little red rowboat down the calm stream toward the viewer, "
        "smiling",
        "{bear} rows past tall green reeds and floating lily pads, a dragonfly hovering "
        "nearby, facing the viewer",
        "{bear} sits in the little red rowboat holding the oars and waves at a friendly little "
        "green frog sitting on a lily pad beside the boat, both facing the viewer",
        "{bear} rows the little red rowboat under a small arched stone bridge, sunlight "
        "sparkling on the water, facing the viewer",
        "{bear} rests the oars and claps his paws merrily while the little red rowboat drifts "
        "gently on the stream",
        "{bear} rows past a riverbank full of colorful wildflowers, butterflies fluttering "
        "over the water, facing the viewer",
        "{bear} rows gently down the stream under a warm golden sunset sky, smiling at the viewer",
        "{bear} yawns sleepily in the little red rowboat with the oars resting, fireflies "
        "glowing softly around him",
        "{bear} lies fast asleep in the little red rowboat with a tiny blanket, eyes closed the whole time, lying still and never sitting up, drifting gently "
        "under a soft lilac evening sky with the first twinkling stars, the camera slowly pulls back",
    ],
}


SONGS = {song["slug"]: song for song in [
    OLD_MACDONALD,
    FIVE_LITTLE_DUCKS,
    ITSY_BITSY_SPIDER,
    TWINKLE_TWINKLE,
    ALPHABET_SONG,
    MARY_HAD_A_LITTLE_LAMB,
    ROW_YOUR_BOAT,
]}
