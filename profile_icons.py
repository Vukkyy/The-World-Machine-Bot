import interactions

icons = [
    "https://static.wikia.nocookie.net/oneshot/images/3/3b/En.png/revision/latest?cb=20170813153310",
    "https://static.wikia.nocookie.net/oneshot/images/1/1b/En_83c.png/revision/latest?cb=20171006214827",
    "https://static.wikia.nocookie.net/oneshot/images/c/ce/En_cry.png/revision/latest?cb=20171006221035",
    "https://static.wikia.nocookie.net/oneshot/images/2/2e/En_distressed2.png/revision/latest?cb=20171006222215",
    "https://static.wikia.nocookie.net/oneshot/images/f/fe/En_eyeclosed.png/revision/latest?cb=20171006223103",
    "https://static.wikia.nocookie.net/oneshot/images/8/82/En_pancakes.png/revision/latest?cb=20171006223511",
    "https://static.wikia.nocookie.net/oneshot/images/0/06/En_wtf2.png/revision/latest?cb=20171006224026",
    "https://static.wikia.nocookie.net/oneshot/images/6/63/En_yawn.png/revision/latest?cb=20171006224037"
]

lightbulbs = [
    'https://empire-s3-production.bobvila.com/articles/wp-content/uploads/2018/07/broken-light-bulb.jpg',
    'https://media.sketchfab.com/models/606df8ee438d442ea7b237c4894c8197/thumbnails/f9a72362c23344a9bb81a31a16b3982d/65cc0d991be8406997beac6fe09e4697.jpeg',
    'https://previews.123rf.com/images/coprid/coprid1209/coprid120900003/15094351-broken-light-bulb-isolated-on-white.jpg',
]

awesome = None

def Emojis():
    niko = interactions.Emoji(id=1019605517695463484)
    twm = interactions.Emoji(id=1023573456664662066)
    kip = interactions.Emoji(id=1019605513387900978)

    awesome = [
        interactions.SelectOption(
            label = "Niko",
            emoji = niko,
            value = 0
        ),

        interactions.SelectOption(
            label = "The World Machine",
            emoji = twm,
            value = 1
        ),

        interactions.SelectOption(
            label = "Kip",
            emoji = kip,
            value = 2
        ),
    ]

    return interactions.SelectMenu(
        type = interactions.ComponentType.SELECT,
        options=awesome,
        placeholder="Select a character!",
        custom_id="menu_component_char",
    )

async def GetEmoji(idx):
    print(awesome)
    awesome[idx]

async def GenerateModalTWM():
    normal = interactions.Emoji(id=1023573456664662066)
    talking = interactions.Emoji(id=1023573456664662066)
    happy = interactions.Emoji(id=1023573455456698368)
    crying = interactions.Emoji(id= 1023573454307463338)
    closed = interactions.Emoji(id=1023573452944322560)
    
    awesome = [
        interactions.SelectOption(
            label = "Normal",
            emoji = normal,
            value = 0
        ),
        interactions.SelectOption(
            label = "Talk",
            emoji = talking,
            value = 1
        ),
        interactions.SelectOption(
            label = "Happy",
            emoji = happy,
            value = 2
        ),
        interactions.SelectOption(
            label = "Crying",
            emoji = crying,
            value = 3
        ),
        interactions.SelectOption(
            label = "Closed Eyes",
            emoji = closed,
            value = 4
        ),
    ]

    return [
        interactions.SelectMenu(
            type = interactions.ComponentType.SELECT,
            options=awesome,
            placeholder="Select a face!",
            custom_id="menu_component",
        ),
        
        awesome
    ]
        
async def GenerateModalKip():
    normal = interactions.Emoji(id=1027240024992927814)
    left = interactions.Emoji(id=1027240038028804156)
    right = interactions.Emoji(id=1027240029803790346)
    sweat = interactions.Emoji(id=1027240026536431687)
    pout = interactions.Emoji(id=1027240031032725504)
    sad = interactions.Emoji(id=1027240032299405332)
    pensive = interactions.Emoji(id=1027240033599627264)
    wink = interactions.Emoji(id=1027240034430099678)
    worry = interactions.Emoji(id=1027240035893915711)
    cool = interactions.Emoji(id=1019605513387900978)

    awesome = [
        interactions.SelectOption(
            label = "Normal",
            emoji = normal,
            value = 0
        ),

        interactions.SelectOption(
            label = "Look Left",
            emoji = left,
            value = 1
        ),

        interactions.SelectOption(
            label = "Look Right",
            emoji = right,
            value = 2
        ),

        interactions.SelectOption(
            label = "Sweat",
            emoji = sweat,
            value = 3
        ),

        interactions.SelectOption(
            label = "Pout",
            emoji = pout,
            value = 4
        ),

        interactions.SelectOption(
            label = "Sad",
            emoji = sad,
            value = 5
        ),

        interactions.SelectOption(
            label = "Pensive",
            emoji = pensive,
            value = 6
        ),

        interactions.SelectOption(
            label = "Wink",
            emoji = wink,
            value = 7
        ),

        interactions.SelectOption(
            label = "Worry",
            emoji = worry,
            value = 8
        ),

        interactions.SelectOption(
            label = "Kip, but cool.",
            emoji = cool,
            value = 9
        ),
    ]

    return [
        interactions.SelectMenu(
            type = interactions.ComponentType.SELECT,
            options=awesome,
            placeholder="Select a face!",
            custom_id="menu_component",
        ),
        
        awesome
    ]

async def GenerateModalNiko():
    normal = interactions.Emoji(id=1019605517695463484)
    talk = interactions.Emoji(id=1019605516210667521)
    left = interactions.Emoji(id=1019605499685113909)
    right = interactions.Emoji(id=1019605501228630107)
    shock = interactions.Emoji(id=1019605514843336764)
    shocked = interactions.Emoji(id=1019605502365274252)
    confused = interactions.Emoji(id=1019605503485149377)
    popcorn = interactions.Emoji(id=1019605504957366282)
    wink = interactions.Emoji(id=1019605506152734790)
    pancake = interactions.Emoji(id=1019605507314548862)
    blush = interactions.Emoji(id=1019605508421857401)
    cry = interactions.Emoji(id=1019605509625618522)
    upset = interactions.Emoji(id=1019605510787453058)
    fedup = interactions.Emoji(id=1019605511802458185)
    
    awesome = [
        interactions.SelectOption(
            label = "Normal",
            emoji = normal,
            value = 0
        ),
        interactions.SelectOption(
            label = "Talk",
            emoji = talk,
            value = 1
        ),
        interactions.SelectOption(
            label = "Look Left",
            emoji = left,
            value = 2
        ),
        interactions.SelectOption(
            label = "Look Right",
            emoji = right,
            value = 3
        ),
        interactions.SelectOption(
            label = "Disgusted",
            emoji = shock,
            value = 4
        ),
        interactions.SelectOption(
            label = "Shocked",
            emoji = shocked,
            value = 5
        ),
        interactions.SelectOption(
            label = "Confused",
            emoji = confused,
            value = 6
        ),
        interactions.SelectOption(
            label = "Popcorn",
            emoji = popcorn,
            value = 7
        ),
        interactions.SelectOption(
            label = "Wink",
            emoji = wink,
            value = 8
        ),
        interactions.SelectOption(
            label = "Pancakes",
            emoji = pancake,
            value = 9
        ),
        interactions.SelectOption(
            label = "Blush",
            emoji = blush,
            value = 10
        ),
        interactions.SelectOption(
            label = "Cry",
            emoji = cry,
            value = 11
        ),
        interactions.SelectOption(
            label = "Upset",
            emoji = upset,
            value = 12
        ),
        interactions.SelectOption(
            label = "Fed Up",
            emoji = fedup,
            value = 13
        )
    ]

    return [
        interactions.SelectMenu(
            type = interactions.ComponentType.SELECT,
            options=awesome,
            placeholder="Select a face!",
            custom_id="menu_component",
        ),
        
        awesome
    ]