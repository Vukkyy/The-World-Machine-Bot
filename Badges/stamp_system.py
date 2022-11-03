import interactions
import json

guild_id = 1017479547664482444

def setup(client):
    global bot
    print('Setting up Stamp System...')
    bot = client
    pass

async def EarnBadge(ctx : interactions.Message, badge_name : str, badge_emoji : str, badge_description : str, user_id : int):
    embed=interactions.Embed(title=f"\"{badge_name}\"", description=f"{badge_description}")
    embed.set_author(name=f"✨<@{user_id}>, You earned a badge!")
    embed.set_thumbnail(url=badge_emoji)
    embed.set_footer(text="Use /select_stamps to equip it.")
    try:
        await ctx.send(embeds=embed)
    except:
        await ctx.reply(embeds=embed)

async def IncrementValue(message : interactions.Message, value : str, targeted : int):
    db = ''
        
    with open('databases/user_database.db', 'r') as f:
        db = f.read()
    
    database = db.split('\n')

    id_ = targeted

    ids = []

    for data_ in database:
        data_ = json.loads(data_)
        ids.append(data_['user_id']) # Get all the user IDs

    index = -1

    for data_ in database:
        index += 1
        
        data_ = json.loads(data_)

        if (id_ in ids):
            if (data_['user_id'] == id_):
                if (not value == 'owner_letter'):
                    data_[value] = data_[value] + 1
                    badge_earned = await CompareValues(data_[value], value, message, data_['badges_earned'], id_)
                else:
                    badge_earned = await CompareValues(0, value, message, data_['badges_earned'], id_)

                if (badge_earned != -1):
                    data_['badges_earned'].append(badge_earned)

                database[index] = json.dumps(data_)

                full = '\n'.join(database)

                with open('databases/user_database.db', 'r+') as f:
                    f.truncate(0)
                    f.write(full)
                return
        else:  
            database.append(json.dumps({
                "user_id" : id_,
                "times_messaged" : 0,
                "suns_shattered" : 0,
                "times_asked" : 0,
                "letters_sent" : 0,
                "badges_earned" : [],
                "equipped_badge" : 'https://cdn.discordapp.com/emojis/1026181554919182416.webp?size=96&quality=lossless'
            }) + '\n')

            ids.append(id_)

async def CompareValues(value : int, type : str, ctx, badges_earned : list, user_id : int):

    if (type == 'owner_letter'):
        if (HasEarned(0, 69, badges_earned, 0)):
            await EarnBadge(
                ctx = ctx,
                badge_name = "Nice!",
                badge_emoji = 'https://cdn.discordapp.com/emojis/{}.webp?size=96&quality=lossless'.format('1026135536190111755'),
                badge_description = 'Have the owner of The World Machine send you a letter.',
                user_id = user_id
            )

            return 69
    
    if (type == 'times_messaged'):
        if (HasEarned(25, 0, badges_earned, value)):
            await EarnBadge(
                ctx = ctx,
                badge_name = "You only have One Shot.",
                badge_emoji = 'https://cdn.discordapp.com/emojis/{}.webp?size=96&quality=lossless'.format('1026207773559619644'),
                badge_description = 'Send 25 messages with The World Machine in the server!',
                user_id = user_id
            )

            return 0

        if (HasEarned(100, 0.1, badges_earned, value)):
            await EarnBadge(
                ctx = ctx,
                badge_name = "Novelty T-Shirt.",
                badge_emoji = 'https://cdn.discordapp.com/emojis/{}.webp?size=96&quality=lossless'.format('1026207765661761596'),
                badge_description = 'Send 100 messages with The World Machine in the server!',
                user_id = user_id
            )

            return 0.1

        if (HasEarned(500, 0.2, badges_earned, value)):
            await EarnBadge(
                ctx = ctx,
                badge_name = "Good luck on your journey, small child!",
                badge_emoji = 'https://cdn.discordapp.com/emojis/{}.webp?size=96&quality=lossless'.format('1026181557230256128'),
                badge_description = 'Send 500 messages with The World Machine in the server!',
                user_id = user_id
            )

            return 0.2

        if (HasEarned(1000, 0.3, badges_earned, value)):
            await EarnBadge(
                ctx = ctx,
                badge_name = "The Ultimate Photo.",
                badge_emoji = 'https://cdn.discordapp.com/emojis/{}.webp?size=96&quality=lossless'.format('1026181559482585138'),
                badge_description = 'Send 1000 messages with The World Machine in the server!',
                user_id = user_id
            )

            return 0.3

    if (type == 'letters_sent'):
        if (HasEarned(25, 2, badges_earned, value)):
            await EarnBadge(
                ctx = ctx,
                badge_name = "Letter Lover",
                badge_emoji = 'https://cdn.discordapp.com/emojis/{}.webp?size=96&quality=lossless'.format('1026181556051648634'),
                badge_description = 'Send 25 letters.',
                user_id = user_id
            )
            return 2

    if (type == 'suns_shattered'):
        if (HasEarned(25, 1, badges_earned, value)):
            await EarnBadge(
                ctx = ctx,
                badge_name = "Chaotic Evil",
                badge_emoji = 'https://cdn.discordapp.com/emojis/{}.webp?size=96&quality=lossless'.format('1026207767142342838'),
                badge_description = 'Shatter 25 Suns.',
                user_id = user_id
            )
            return 1

        if (HasEarned(100, 1.1, badges_earned, value)):
            await EarnBadge(
                ctx = ctx,
                badge_name = "That can't be good for the multiverse.",
                badge_emoji = 'https://cdn.discordapp.com/emojis/{}.webp?size=96&quality=lossless'.format('1026207768643907705'),
                badge_description = 'Shatter 100 Suns.',
                user_id = user_id
            )
            return 1.1

        if (HasEarned(250, 1.2, badges_earned, value)):
            await EarnBadge(
                ctx = ctx,
                badge_name = "Mass Genocide of the cosmos.",
                badge_emoji = 'https://cdn.discordapp.com/emojis/{}.webp?size=96&quality=lossless'.format('1026207771198226462'),
                badge_description = 'Shatter 250 Suns.',
                user_id = user_id
            )
            return 1.2

        if (HasEarned(500, 1.3, badges_earned, value)):
            await EarnBadge(
                ctx = ctx,
                badge_name = "No Nikos were harmed. I think.",
                badge_emoji = 'https://cdn.discordapp.com/emojis/{}.webp?size=96&quality=lossless'.format('1026207769969307698'),
                badge_description = 'Shatter 500 Suns.',
                user_id = user_id
            )
            return 1.3

    return -1

def HasEarned(goal : int, id_, earned, value):
    if (id_ in earned):
        return False
    elif (value >= goal):
        return True
    else:
        return False

async def GetCurrentBadge(user_id : int, set_badge : bool, badge_img : str, add_badge : bool = False, badge_id : int = -1):
    db = ''
        
    with open('databases/user_database.db', 'r') as f:
        db = f.read()
    
    database = db.split('\n')

    ids = []

    for data_ in database:
        data_ = json.loads(data_)
        ids.append(data_['user_id'])

    index = -1

    for data_ in database:
        index += 1
        
        data_ = json.loads(data_)

        if (user_id in ids):
            if (data_['user_id'] == user_id):
                if (set_badge == False):
                    return data_['equipped_badge']
                else:
                    if (add_badge):
                        data_['badges_earned'].append(badge_id)
                    else:
                        data_['equipped_badge'] = ''
                        data_['equipped_badge'] = badge_img

                    

                    database[index] = json.dumps(data_)
    
                    full = '\n'.join(database)
    
                    with open('databases/user_database.db', 'r+') as f:
                        f.truncate(0)
                        f.write(full)
                    return
        else:
            print('whoops')
            database.append(json.dumps({
                "user_id" : user_id,
                "times_messaged" : 0,
                "suns_shattered" : 0,
                "times_asked" : 0,
                "letters_sent" : 0,
                "badges_earned" : [],
                "equipped_badge" : "https://cdn.discordapp.com/emojis/1026181554919182416.webp?size=96&quality=lossless"
            }) + '\n')

            ids.append(user_id)

