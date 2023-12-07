import random

# Variables with lists of possible elements
adjectives = [
    "mystical",
    "shiny",
    "dark",
    "colorful",
    "tranquil",
    "ancient",
    "futuristic",
    "vibrant",
    "dystopian",
    "serene",
    "cosmic",
    "dreamy",
    "nebulous",
    "twinkling",
    "ghostly",
    "celestial",
    "rustic",
    "fabled",
    "luminous",
    "mythic",
    "abandoned",
    "floating",
    "mysterious",
    "underwater",
    "forgotten",
    "haunted",
    "space",
    "ethereal",
    "incandescent",
    "melodic",
    "frosty",
    "fiery",
    "shadowy",
    "golden",
    "silvered",
    "arcane",
    "enigmatic",
    "sacred",
    "profane",
    "emerald",
    "crystalline",
    "majestic",
    "regal",
    "ornate",
    "prismatic",
    "opaque",
    "translucent",
    "radiant",
    "gloomy",
    "enchanting",
    "perilous",
    "tempestuous",
    "whimsical",
    "effulgent",
    "phantasmal",
    "auroral",
    "stellar",
    "eclipsing",
    "crescent",
    "bountiful",
    "desolate",
    "verdant",
    "lush",
    "sterling",
    "nautical",
    "aerial",
    "subterranean",
    "alabaster",
    "draconic",
    "spectral",
    "iridescent",
    "kaleidoscopic",
    "dazzling",
    "charmed",
    "bewitching",
    "velvet",
    "silken",
    "coppery",
    "zephyrous",
    "obscure",
    "divine",
    "infernal",
    "terrestrial",
    "aquatic",
    "sylvan",
    "harmonious",
    "discordant",
    "resplendent",
    "ephemeral",
    "eternal",
    "chronal",
    "primordial",
    "arcadian",
    "wondrous",
    "surreal",
    "bizarre",
    "elusive",
    "forged",
    "revered",
    "mythological",
    "legendary",
    "enveloping",
    "shifting",
    "tumultuous",
    "sonorous",
    "lustrous",
    "whispered",
    "echoing",
    "forgotten",
    "otherworldly",
    "entangled",
    "enraptured",
    "forbidden",
    "untamed",
    "boundless",
    "infinite",
    "celestial",
    "abyssal",
    "venerable",
    "sacrosanct",
    "mirrored",
    "illustrious",
    "hidden",
    "unveiled",
    "serrated",
    "veiled",
    "skeletal",
    "reverberating",
    "silent",
    "gilded",
    "adamantine",
    "eldritch",
    "infernal",
    "sage",
    "hallowed",
    "cursed",
    "blessed",
    "vexed",
    "embered",
    "azure",
    "cerulean",
    "crimson",
    "scarlet",
    "viridescent",
    "opalescent",
    "pearlescent",
    "kohl-rimmed",
    "fey-touched",
    "tenebrous",
    "lambent",
    "candescent",
    "indigo",
    "molten",
    "frozen",
    "crackling",
    "humming",
    "throbbing",
    "pulsating",
    "shimmering",
    "swirling",
    "twisted",
    "gnarled",
    "sinuous",
    "coiled",
    "spiraled",
    "whirling",
    "winding",
    "undulating",
    "perpetual",
    "cataclysmic",
    "epochal",
    "anachronistic",
    "fleeting",
    "decaying",
    "withering",
    "blooming",
    "vibrating",
    "resonating",
    "quivering",
    "trembling",
    "oscillating",
    "quaking",
    "shaking",
    "shuddering",
    "vibrant",
    "piercing",
    "cutting",
    "slicing",
    "rending",
    "tearing",
    "shattering",
    "crushing",
    "smashing",
    "rending",
    "splintering",
    "shredding",
    "dissonant",
    "resonant",
    "cacophonic",
    "euphonic",
    "melodious",
    "harmonic",
    "discordant",
    "rhythmic",
    "symphonic",
    "atonal",
    "sonic",
    "ultrasonic",
    "infrasonic",
    "acoustic",
    "electronic",
    "electric",
    "magnetic",
    "gravitic",
    "kinetic",
    "thermal",
    "aetheric",
    "luminal",
    "subluminal",
    "transluminal",
    "antropomorphic",
    "antropomorphic",  # TODO: Add probabilities
]

contexts = [
    "under the starry night",
    "in the autumn",
    "under the rain",
    "in the winter",
    "during a thunderstorm",
    "in the fog",
    "in full bloom",
    "in the silence of night",
    "under a rainbow",
    "under the northern lights",
    "at the edge of the world",
    "amidst a meteor shower",
    "in the realm of dreams",
    "on a moonlit night",
    "at the end of a rainbow",
    "in the twilight hour",
    "beyond the cosmic veil",
    "at the dawn of time",
    "during high tide",
    "at sunset",
    "in the heat of summer",
    "in a blizzard",
    "during a hailstorm",
    "in a sandstorm",
    "in a whirlwind",
    "during a lunar eclipse",
    "at the stroke of midnight",
    "in the golden hour",
    "in the dead of winter",
    "in the height of noon",
    "during an earthquake",
    "in a volcanic eruption",
    "under a comet's tail",
    "at the crossroads",
    "in a time loop",
    "in a quantum state",
    "in the eye of the storm",
    "in the afterglow",
    "in the zenith",
    "in the nadir",
    "in a moment of serendipity",
    "in a fleeting instant",
    "in the abyss",
    "in the void",
    "in the limelight",
    "in the shadows",
    "amongst ancient ruins",
    "in a forgotten realm",
    "in a melting glacier",
    "on a crystal field",
    "in a frozen wasteland",
    "amidst a coral garden",
    "in a burning forest",
    "at the gates of a forgotten castle",
    "in the halls of a crystal palace",
    "on a pathway of floating stones",
    "in a city of clouds",
    "in a garden of singing flowers",
    "on a river of stars",
    "in a forest of giant mushrooms",
    "on a bridge of rainbows",
    "in a cave of wonders",
    "in a lair of dragons",
    "at the heart of a nebula",
    "in a village of whispers",
    "on the rings of Saturn",
    "in a theater of illusions",
    "on the wings of a storm",
    "in a valley of echoes",
    "at the fountain of youth",
    "on a canopy of endless trees",
    "in a desert of red sands",
    "in the labyrinth of reflections",
    "on the shores of oblivion",
    "in a city of endless towers",
    "on a sea of glass",
    "in a world without color",
    "in a realm of endless dusk",
    "in a never-ending waterfall",
    "at the cradle of creation",
    "in a field of floating orbs",
    "in a dimension of mirrors",
    "on the trail of falling stars",
    "in a land of forgotten lore",
    "in a reality of shifting sands",
    "on a mountain of whispers",
    "in a grove of eternal spring",
    "under a sky woven with time's fabric",
    "amidst a dance of fireflies",
    "in a garden of secrets",
    "on a glowing beach",
    "within a bioluminescent cavern",
    "at the edge of a mirror-like lake",
    "on a cliff overlooking clouds",
    "in a storytelling meadow",
    "under a liquid light waterfall",
    "within an ancient forest",
    "on a nocturnal hill",
    "in a stardust galaxy",
    "amidst shifting auroras",
    "in a crystal ocean",
    "on a star-touching peak",
    "in a singing valley",
    "inside a floating bubble",
    "on a door-lined path",
    "on a giant turtle",
    "at parallel universes' meeting",
    "in a light forest",
    "on a world-grain plain",
    "under a mythic constellation sky",
    "in a cosmic lotus",
    "a bustling city market",
    "On a serene lakeside at dawn",
    "Atop a snow-capped mountain",
    "Inside a vibrant coral reef",
    "In the heart of a dense jungle",
    "Amongst the ruins of an ancient civilization",
    "On a tranquil beach at twilight",
    "In a bustling urban metropolis at night",
    "On a quaint village street in spring",
    "At a lively carnival",
    "Within a mysterious, foggy forest",
    "Amidst a vibrant autumn forest",
    "On a busy downtown street during rush hour",
    "In a peaceful monastery in the mountains",
    "At a vibrant festival in a historic city",
    "Under a sky filled with a dazzling meteor shower",
    "On a futuristic space station orbiting Earth",
    "In the depths of a colorful, neon-lit cybercity",
    "In a futuristic laboratory conducting experiments",
    "On a crowded subway train during peak hours",
    "At a remote research station in Antarctica",
    "On a graffiti-filled street in an urban area",
]

objects = [
    "handcrafted marionette",
    "radio",
    "piano",
    "guitar",
    "Vintage Camera",
    "domino",
    "presents",
    "egg",
    "Teapot",
    "Tornado",
    "Jet suit",
    "Umbrella",
    "Shoes",
    "Bicycle",
    "Kite",
    "Chess",
    "Hat",
    "Spoon",
    "Book",
    "Laptop",
    "Sunglasses",
    "Backpack",
    "Skateboard",
    "Microscope",
    "Violin",
    "Compass",
    "Candle",
    "Paintbrush",
    "Clock",
    "Basketball",
    "Telescope",
    "Yoga Mat",
    "Calculator",
    "Chessboard",
    "Gardening Gloves",
    "Perfume Bottle",
    "Key",
    "Magnifying Glass",
    "Origami Crane",
    "Drumsticks",
    "Bonsai Tree",
    "Picnic Basket",
    "Jigsaw Puzzle",
    "Scarf",
    "Ice Skates",
    "Lantern",
    "Binoculars",
    "Accordion",
    "Snow Globe",
    "Roller Skates",
    "Butterfly Net",
    "Suitcase",
    "Hourglass",
    "Harmonica",
    "Pottery Wheel",
    "Sandcastle Bucket",
    "Typewriter",
    "Parachute",
    "Sushi Rolling Mat",
    "Quill and Ink",
    "Hammock",
    "Solar Panel",
    "Surfboard",
    "Dumbbells",
    "Model Airplane",
    "Treasure Chest",
    "Boots",
    "Saxophone",
    "Metal Detector",
    "Puppet",
    "Rubik's Cube",
    "Tarot Cards",
    "Unicycle",
    "Snorkel and Fins",
    "Didgeridoo",
    "Crystal Ball",
    "Electric Fan",
    "Mosaic Tiles",
    "Yo-Yo",
    "Archery Bow",
    "Camping Tent",
    "Stethoscope",
    "Hot Air Balloon",
    "Chandelier",
    "Geiger Counter",
    "Wind Chime",
    "Pogo Stick",
    "Barometer",
    "Calligraphy Set",
    "Velocipede",
    "Altimeter",
    "Beekeeping Suit",
    "Mandolin",
    "Climbing Gear",
    "Ventriloquist Dummy",
    "Glider Plane",
    "Submarine Model",
    "Theremin",
    "Astronaut Helmet",
    "Blacksmith Anvil",
    "Circus Cannon",
    "Ant Farm",
    "3D Printer",
    "Steam Engine Model",
    "Loom",
    "Pipe Organ",
    "Espresso Machine",
    "Fire Extinguisher",
    "Gramophone",
    "Kite Surfing Board",
    "Ghost Hunting Equipment",
    "Bonsai",
    "Fountain Pen" "Monocular",
    "Origami Paper",
    "Maracas",
    "Pilates Ball",
    "Paddleboard",
    "Birdhouse",
    "Taxidermy Deer Head",
    "Torch",
    "Theatre mask",
    "Jail",
    "Trumpet",
    "Paper ship",
    "Map",
    "Fruit",
    "Bones",
    "Arco Iris",
    "Car",
    "Cute Robot",
]

creatures = [
    "dragon",
    "unicorn",
    "phoenix",
    "griffin",
    "giant spider",
    "mermaid",
    "sphinx",
    "centaur",
    "fairy",
    "troll",
    "werewolf",
    "elemental spirit",
    "gargoyle",
    "chimera",
    "dream weaver",
    "cosmic serpent",
    "lightning bird",
    "lunar moth",
    "stellar wolf",
    "solar deer",
    "nebula whale",
    "celestial bear",
    "kraken",
    "yeti",
    "bigfoot",
    "sasquatch",
    "cyclops",
    "harpy",
    "minotaur",
    "basilisk",
    "siren",
    "nymph",
    "dryad",
    "salamander",
    "wyvern",
    "manticore",
    "banshee",
    "poltergeist",
    "djinn",
    "kelpie",
    "selkie",
    "wendigo",
    "vampire",
    "zombie",
    "ghost",
    "demon",
    "angel",
    "leviathan",
    "behemoth",
    "quetzalcoatl",
    "kitsune",
    "tanuki",
    "tengu",
    "kappa",
    "yokai",
    "oni",
    "naga",
    "asura",
    "rakshasa",
    "gorgon",
    "satyr",
    "pegasus",
    "hippogriff",
    "cockatrice",
    "will-o'-the-wisp",
    "pixie",
    "brownie",
    "leprechaun",
    "gnome",
    "dwarf",
    "elf",
    "orc",
    "goblin",
    "ogre",
    "Bake-kujira (Japanese ghost whale)",
    "Cetus (Greek sea monster)",
    "Devil Whale (English ship-swallowing whale)",
    "Encantado (Brazilian shapeshifter dolphin)",
    "Glashtyn (Celtic sea horse goblin)",
    "Makara (Hindu half terrestrial, aquatic creature)",
    "Sea goat (Greek goat-fish hybrid)",
    "Water bull (Scottish amphibious bull)",
    "Anansi (West African spider trickster)",
    "Arachne (Cursed Greek weaver-spider)",
    "Carbuncle (Chilote fiery light creature)",
    "Gold-digging ant (Greek mythical ant)",
    "Jorōgumo (Japanese spider woman)",
    "Khepri (Egyptian sun-pushing beetle)",
    "Mothman (American moth-like cryptid)",
    "Myrmecoleon (Christian ant-lion)",
    "Chalkydri (Creature of light)",
    "Rainbow crow (Rainbow-associated bird)",
    "Rainbow Serpent (Mythical serpent)",
    "Alicanto (Metal/gold bird)",
    "Pixiu (Chinese mythical creature)",
    "Chrysomallos (Golden-fleeced ram)",
    "Raijū (Japanese thunder creature)",
    "Aspidochelone",
    "Bloody Bones",
    "Bunyip",
    "Camenae",
    "Capricorn",
    "Charybdis",
    "Chinese Dragon",
    "Cai Cai-Vilu",
    "Davy Jones' Locker",
    "Draug",
    "Elemental",
    "Fish People",
    "Fossegrim",
    "Fur-bearing trout",
    "Gargouille",
    "Grindylow creature",
    "Hippocamp",
    "Hydra",
    "Ichthyocentaur",
    "Jasconius",
    "Jengu",
    "Kappa creature",
    "Kelpie",
    "Kraken",
    "Lake monster",
    "Lavellan",
    "Leviathan",
    "Loch Ness monster",
    "Lorelei",
    "Makara",
    "Mami Wata",
    "Mermaid man",
    "Merrow",
    "Morgens",
    "Muc-sheilch",
    "Naiad",
    "Näkki",
    "Nereid",
    "Nix",
    "Nymph",
    "Pisces",
    "Potamus",
    "Rusalka",
    "Sea monster",
    "Sea serpent",
    "Selkie",
    "Shen",
    "Siren",
    "Tiamat",
    "Triton",
    "Ondine",
    "Vodyanoy",
    "Water dragon",
    "Water leaper",
    "Water sprite",
    "Zaratan creature",
    "Dog",
    "Cat",
    "Rabbit",
    "Mouse",
    "Frog",
    "Dolphin",
    "Orca",
    "Tiger",
    "Horse",
    "Lion",
    "Koala",
    "Panda",
    "Wolf",
    "Deer",
    "Hippo",
    "Shark",
    "Elephant",
    "Squirrel",
    "Hedgehog",
    "Turtle",
    "Sloth",
    "Axolotl",
    "Penguin",
    "Polar Bear",
    "Pig",
    "Sheep",
    "Cow",
    "Goat",
    "Chicken",
    "Duck",
    "Turkey",
    "Peacock",
    "Parrot",
    "Owl",
    "Eagle",
    "Falcon",
    "Raven",
    "Swan",
    "Leopard",
    "Panther",
    "Racoon",
    "Snail",
    "Octopus",
    "Lemur",
    "Cute Dragon",
    "Bubble Creature",
]

characters = [
    "Wizard",
    "Alien",
    "Spaceman",
    "Samurai",
    "Detective",
    "Necromancer",
    "Vampire",
    "Fisherman",
    "Knight",
    "Pirate",
    "Scientist",
    "Gladiator",
    "Ninja",
    "Astronaut",
    "Zombie",
    "Superhero",
    "Ghost",
    "Cowboy",
    "Mermaid",
    "Witch",
    "Dragon",
    "Elf",
    "Robot",
    "Spy",
    "Queen",
    "King",
    "Bard",
    "Explorer",
    "Time Traveler",
    "Cyborg",
    "Angel",
    "Werewolf",
    "Sorceress",
    "Fairy",
    "Assassin",
    "Monk",
    "Barbarian",
    "Druid",
    "Archer",
    "Paladin",
    "Alchemist",
    "Warlock",
    "Shaman",
    "Priest",
    "Gnome",
    "Dwarf",
    "Giant",
    "Demigod",
    "Griffin",
    "Valkyrie",
    "Vampire Hunter",
    "Mage",
    "Bounty Hunter",
    "Highlander",
    "Gunslinger",
    "Martial Artist",
    "Medusa",
    "Siren",
    "Steampunk Inventor",
    "Cyberpunk Hacker",
    "Shape-shifter",
    "Minotaur",
    "Chimera",
    "Diplomat",
    "Archaeologist",
    "Necrolyte",
    "Elemental Wizard",
    "Space Marine",
    "Ninja Warrior",
    "Sky Pirate",
    "Cybernetic Soldier",
    "Mystic",
    "Oracle",
    "Beastmaster",
    "Firefighter",
    "Ice Mage",
    "Urban Legend Character",
    "Revolutionary Leader",
    "Mutant",
    "Survivalist",
    "Knight Templar",
    "Demon Hunter",
    "Alien Overlord",
    "Timekeeper",
    "Sea Captain",
    "Airship Pilot",
    "Dimensional Traveler",
    "Jungle Explorer",
    "Phantom Thief",
    "Police Officer",
    "Software Engineer",
    "Prisoner",
    "Monk",
    "Man made of rocks",
    "Cat Man",
    "Viking",
    "Fire girl",
    "Banana Man",
    "Jelly Guy",
    "Lizard Wizard",
    # Famous Characters
    "Robin Hood",
    "Zorro",
    "Dracula",
    "Sherlock Holmes",
    "John Carter",
    "Frankenstein's Monster",
    "Scarecrow",
    "Dorothy Gale",
    "Tin Woodman",
    "The Hunchback of Notre Dame",
    "King Kong",
    "Ivanhoe",
    "Alice (from Wonderland)",
    "Jack Pumpkinhead",
    "Gravestone",
    "Man of War",
    "Dr. Jekyll Mr. Hyde",
    "Cthulhu",
    "Hercules",
    "Natty Bumppo",
    "Paul Bunyan",
    "Long John Silver",
    "Wizard Of Oz",
    "Firehair",
    "Captain Nemo",
    "King Arthur",
    "Woggle-Bug",
    "Mystico",
    "Cheshire Cat",
    "Wilhelmina Murray",
    "Queen Of Hearts",
    "Brad Spencer, Wonderman",
    "Mad Hatter",
    "Achilles",
    "Nyarlathotep",
    "Red Comet",
    "Allan Quatermain",
    "Atoman",
    "Helen of Troy",
    "Mouthpiece",
    "Moby Dick",
    "Wicked Witch of the West",
    "Victor Frankenstein",
    "Sinbad",
    "The Sphinx",
    "Headless Horseman",
    "Abraham Van Helsing",
    "Ares",
    "Abdul Alhazred",
    "C. Auguste Dupin",
    "Ayesha",
    "Aladdin",
    "Barbarella",
    "Buddy",
    "Beowulf",
    "Bride of Frankenstein",
    "Captain Ahab",
    "Creature from the Black Lagoon",
    "Cyclone",
    "Dorian Gray",
    "Dagar, Desert Hawk",
    "Don Quixote",
    "Ebenezer Scrooge",
    "Gulliver",
    "Grendel",
    "Green Giant",
    "D'Artagnan",
    "Huckleberry Finn",
    "Aramis",
    "Porthos",
    "Judy of the Jungle",
    "Loch Ness Monster",
    "Moon Girl",
    "Magno",
    "Hugo Danner",
    "Green Lama",
    "Fighting Yank",
    "Octobriana",
    "Odysseus",
    "Red Riding Hood",
    "Rapunzel",
    "Rumpelstiltskin",
    "Rosie The Riveter",
    "Rocketgirl",
    "The Yellow Kid",
    "The Wolf Man",
    "Winnie-the-Pooh",
    "Anne (from 'Anne of Green Gables')",
    "Judah Ben-Hur (from 'Ben-Hur')",
    "Cinderella",
    "Mowgli",
    "The Phantom of the Opera",
    "Snow White character",
    "Tarzan",
    "Oswald the Lucky Rabbit",
    "Felix the Cat",
    "Black Beauty",
    "Sara Crewe (from 'A Little Princess')",
    "The Nutcracker",
]


settings = [
    "castle",
    "forest",
    "cave",
    "oasis",
    "temple",
    "mansion",
    "station",
    "monastery",
    "ship",
    "city",
    "labyrinth",
    "garden",
    "clouds",
    "observatory",
    "sanctuary",
    "meadow",
    "lake",
    "valley",
    "island",
    "utopia",
    "desert",
    "volcano",
    "waterfall",
    "tundra",
    "swamp",
    "space station",
    "moon base",
    "jungle",
    "mountain peak",
    "underwater city",
    "glacier",
    "ruins",
    "haunted house",
    "farm",
    "beach",
    "skyscraper",
    "village",
    "amusement park",
    "zoo",
    "aquarium",
    "airport",
    "train station",
    "colosseum",
    "pyramid",
    "bazaar",
    "library",
    "museum",
    "school",
    "hospital",
    "prison",
    "fortress",
    "windmill",
    "lighthouse",
    "cathedral",
    "arena",
    "coral reef",
    "savanna",
    "rainforest",
    "canyon",
    "cliff",
    "marsh",
    "steppe",
    "battlefield",
    "dungeon",
    "mine",
    "factory",
    "floating island",
    "sky castle",
    "nebula",
    "black hole",
    "wasteland",
    "iceberg",
    "dimensional portal",
    "clocktower",
    "dojo",
    "igloo",
    "treehouse",
    "submarine",
    "spaceship",
    "casino",
    "theater",
    "opera house",
    "circus",
    "stadium",
    "mall",
    "arcade",
    "lunar colony",
    "asteroid mine",
    "alien planet",
    "magic shop",
    "wizard tower",
    "dragons lair",
    "eldritch realm",
    "fairy glen",
    "vampire castle",
    "werewolf den",
    "ghost town",
    "cyberpunk city",
    "steampunk factory",
    "post apocalyptic city",
    "underground bunker",
    "secret base",
    "nuclear silo",
    "abandoned asylum",
    "ancient temple",
    "sacred grove",
    "elven city",
    "dwarven mine",
    "orc camp",
    "goblin market",
    "pirate ship",
    "robot factory",
    "virtual reality",
    "parallel universe",
    "quantum realm",
    "celestial palace",
    "infernal pit",
    "heavenly garden",
    "purgatory",
    "limbo",
    "nirvana",
    "shangri la",
    "atlantis",
    "eldorado",
    "avalon",
    "asgard",
    "olympus",
    "underworld",
    "valhalla",
    "middle earth",
    "galactic federation",
    "interstellar embassy",
    "wormhole",
    "pocket dimension",
    "haunted cemetery",
    "crypt",
    "mausoleum",
    "pet cemetery",
    "ancient ruins",
    "sphinx",
    "moai statues",
    "stonehenge",
    "chichen itza",
    "great wall",
    "taj mahal",
    "mount rushmore",
    "grand canyon",
    "niagara falls",
    "sahara desert",
    "everest basecamp",
    "north pole",
    "south pole",
    "deep sea trench",
    "bamboo forest",
    "cherry blossom grove",
    "lavender field",
    "sunflower field",
    "tea plantation",
    "coffee farm",
    "vineyard",
    "maze",
    "emerald city",
    "starship station",
    "Land of Oz",
    "crystal cavern",
    "sky gardens",
    "ghost ship",
    "Luminous Forest",
]

themes = [
    "Ghibli style",
    "Anime style",
    "Abstract style",
    "Cubist style",
    "Surrealism style",
    "Pixel art style",
    "Graffiti style",
    "Futurist style",
    "Pointillist style",
    "Symbolist style",
    "Steampunk style",
    "Cyberpunk style",
    "Manga style",
    "Psychedelic style",
    "Horror style",
    "Fantasy style",
    "Digital art style",
    "Analog photo style",
    "3D style",
    "Comic style",
    "Low Poly style",
    "Vector style",
    "Silhouette style",
    "Origami style",
    "Paper Cut-Out style",
    "Isometric style",
    "Blueprint style",
    "Sketch style",
    "Doodle style",
    "Zentangle style:0.25",
    "Mosaic style",
    "Stained Glass style:0.25",
    "Neon style",
    "Glitch Art style",
    "X-Ray style",
    "Thermal Imaging style",
    "Double Exposure style",
    "Bokeh style",
    "Goth style",
    "Punk style",
    "Retro style",
    "Watercolour style",
    "Dark fantasy style",
    "Patchwork collage style",
    "Phantasmal iridescent style",
    "Japanese ink art",
    "Lowbrow Art Style",
    "Hyper-Realistic Style",
    "Pop Art Style",
    "Ukiyo-e Art Style",
    "Cute 3D Render Style",
    "Crayon drawing style",
    "Dieselpunk style",
    "Retro anime style",
    "Beksinski style",
    "Van Gogh style:0.5",
]


STYLES = {
    "general": [
        {
            "model_path": "segmind/SSD-1B",
            "model_scheduler": "euler_a",
            "prompt": {
                "positive": "{theme} {character} on {setting} close-up, 8k, high quality",
                "negative": "bad quality, text",
                "guidance_scale": 7,
            },
            "height": 688,
            "width": 512,
            "num_inference_steps": 35,
            "num_images": 1,
            "seed": -1,
        },
        {
            "model_path": "segmind/SSD-1B",
            "model_scheduler": "euler_a",
            "prompt": {
                "positive": "{theme} {adjective} {character} {context} close-up, 8k, high quality",
                "negative": "bad quality, text",
                "guidance_scale": 7,
            },
            "height": 688,
            "width": 512,
            "num_inference_steps": 35,
            "num_images": 1,
            "seed": -1,
        },
        {
            "model_path": "segmind/SSD-1B",
            "model_scheduler": "euler_a",
            "prompt": {
                "positive": "{theme} {creature} {context} close-up, 8k, high quality",
                "negative": "bad quality, text",
                "guidance_scale": 7,
            },
            "height": 688,
            "width": 512,
            "num_inference_steps": 35,
            "num_images": 1,
            "seed": -1,
        },
        {
            "model_path": "segmind/SSD-1B",
            "model_scheduler": "euler_a",
            "prompt": {
                "positive": "{theme} {adjective} {creature} on {setting} close-up, 8k, high quality",
                "negative": "bad quality, text",
                "guidance_scale": 7,
            },
            "height": 688,
            "width": 512,
            "num_inference_steps": 35,
            "num_images": 1,
            "seed": -1,
        },
        {
            "model_path": "segmind/SSD-1B",
            "model_scheduler": "euler_a",
            "prompt": {
                "positive": "{theme} {adjective} {object} on {setting} close-up, 8k, high quality",
                "negative": "bad quality, text",
                "guidance_scale": 7,
            },
            "height": 688,
            "width": 512,
            "num_inference_steps": 35,
            "num_images": 1,
            "seed": -1,
        },
    ],
}
