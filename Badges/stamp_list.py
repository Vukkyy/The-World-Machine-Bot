import interactions
import json

stamps = [
    {
        "stamp_id" : -1, "stamp_url" : 1026181554919182416, "name" : "Default Stamp"
    },
    
    {
        "stamp_id" : 0, "stamp_url" : 1026207773559619644, "name" : "The Sun"
    },

    {
        "stamp_id" : 0.1, "stamp_url" : 1026207765661761596, "name" : "Novelty T-Shirt"
    },

    {
        "stamp_id" : 0.2, "stamp_url" : 1026181557230256128, "name" : "Glowing Die"
    },

    {
        "stamp_id" : 0.3, "stamp_url" : 1026181559482585138, "name" : "Photo of Niko"
    },
    
    {
        "stamp_id" : 2, "stamp_url" : 1026181556051648634, "name" : "Feather Pen"
    },

    {
        "stamp_id" : 1, "stamp_url" : 1026207767142342838, "name" : "Shattered Sun"
    },

    {
        "stamp_id" : 1.1, "stamp_url" : 1026207768643907705, "name" : "Bronze Shattered Sun"
    },

    {
        "stamp_id" : 1.2, "stamp_url" : 1026207771198226462, "name" : "Silver Shattered Sun"
    },

    {
        "stamp_id" : 1.3, "stamp_url" : 1026207769969307698, "name" : "Golden Shattered Sun"
    },

    {
        "stamp_id" : 69, "stamp_url" : 1026135536190111755, "name" : "Dark Clover"
    },

    {
        "stamp_id" : 100, "stamp_url" : 1026199772232695838, "name" : "Golden Clover"
    },

    {
        "stamp_id" : 699, "stamp_url" : 1027306556783603813, "name" : "Eyebrow Raise"
    },
]


async def OpenStampMenu(user_id : int):
    db = ''

    stamp_menu_list = []
        
    with open('databases/user_database.db', 'r') as f:
        db = f.read()
    
    database = db.split('\n')

    ids = []

    for data_ in database:
        data_ = json.loads(data_)
        ids.append(data_['user_id'])

    emoji = interactions.Emoji(id = stamps[0]['stamp_url'])

    stamp_menu_list.append(
        interactions.SelectOption(
            label = stamps[0]['name'],
            value = emoji.url,
            emoji = emoji
        )
    )

    for data_ in database:
        data_ = json.loads(data_)
        if (data_['user_id'] == user_id):
            index = 0
            for stamp in stamps:
                print(stamp)
                if (stamp['stamp_id'] in data_['badges_earned']):
                    emoji : interactions.Emoji = interactions.Emoji(id = stamp['stamp_url'])
                    index += 1
                    try:
                        stamp_menu_list.append(
                            interactions.SelectOption(
                                label = stamp['name'],
                                value = emoji.url,
                                emoji = emoji,
                            )
                        )
                    except:
                        pass

            return stamp_menu_list