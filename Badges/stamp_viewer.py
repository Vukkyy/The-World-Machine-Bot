from PIL import Image, ImageDraw, ImageFont, ImageEnhance
from os import listdir
from interactions.ext.database.database import Database
import Badges.stamp_list as list_
import aiohttp        
import aiofiles
import Badges.stamp_system as stamps_
import json
import chars
import textwrap
import database_manager as db
    
async def DrawBadges(user_id : int, ctx, user : str = 'awesome person', user_pfp : str = ''):
    print('Viewing Badges...')

    images = []

    for stamp in list_.stamps:
        images.append(f'https://cdn.discordapp.com/emojis/{stamp["stamp_url"]}.png')

    msg = f'{user}\'s Profile'

    print(user)
    
    profile = await Database.get_item(ctx, 'profile_information')

    bg = Image.open(f'Badges/Images/Backgrounds/{profile["profile_background"]}.png')

    equipped = await stamps_.GetCurrentBadge(user_id, False, '')

    img_equipped = await DownloadImage(equipped, 'equipped')

    fnt = ImageFont.truetype("font/TerminusTTF-Bold.ttf", 25) # Font
    title_fnt = ImageFont.truetype("font/TerminusTTF-Bold.ttf", 25) # Font
    
    d = ImageDraw.Draw(bg)

    d.text((32, 32), msg, font=title_fnt, fill=(252, 186, 86), stroke_width=1, stroke_fill=(252, 186, 86))

    description = textwrap.fill(profile['profile_description'], 35)
    
    d.text((210, 140), f"\"{description}\"", font = fnt, fill=(255,255,255))
    
    pfp = await DownloadImage(user_pfp, 'profile_picture')
    
    pfp = pfp.resize((148, 148))
    
    bg.paste(pfp, (32, 80), pfp.convert('RGBA'))
    
    icons = []
    ids = []

    idx = 0
    
    for item in images:
        img = await DownloadImage(item, 'icon')
        img = img.convert('RGBA')
        img = img.resize((35, 35), Image.Resampling.NEAREST)
        icons.append(img)
        ids.append(list_.stamps[idx]['stamp_id'])

        idx += 1

    init_index = 90
    index = init_index
    i = 0
    pos_y = 300
    
    for icon in icons:
        i += 1
        endexo = 0
        
        for id_ in ids:
            if (await GetStamps(user_id, id_)):
                pass
            else:
                enhancer = ImageEnhance.Brightness(icons[endexo])
                icons[endexo] = enhancer.enhance(0)
            endexo += 1

        bg.paste(icon, (index, pos_y), icon.convert('RGBA'))
        index += 100
        
        if (i > 5):
            index = init_index
            pos_y += 50
            i = 0
            
    bg.paste(img_equipped, (659, 25), img_equipped.convert('RGBA'))

    d.text((648, 32), 'Equipped Stamp:', font = fnt, fill=(255,255,255), anchor='rt', align='right')
    
    coins = await db.GetDatabase(user_id, 'ram', {"uid" : user_id, "coins" : 0})
    d.text((648, 250), f'{coins["coins"]} x', font = fnt, fill=(255,255,255), anchor='rt', align='right')
    wool_ = await DownloadImage('https://cdn.discordapp.com/emojis/1044668364422918176.png', 'wool')
    
    bg.paste(wool_, (659, 243), wool_.convert('RGBA'))
    
    d.text((42, 251), 'Unlocked Achievement Stamps:', font = fnt, fill=(255,255,255))
    
    bg.save('Badges/result.png')
    print('finished')

async def DownloadImage(image_url, filename):
    async with aiohttp.ClientSession() as session:
        async with session.get(image_url) as resp:
            if resp.status == 200:
                f = await aiofiles.open(f'Badges/Images/{filename}.png', mode='wb')
                await f.write(await resp.read())
                await f.close()
    
    return Image.open(f'Badges/Images/{filename}.png')

async def GetStamps(user_id, stamp_id):

    db = ''
        
    with open('databases/user_database.db', 'r') as f:
        db = f.read()
    
    database = db.split('\n')

    ids = []
    
    for data_ in database:
        data_ = json.loads(data_)
        ids.append(data_['user_id'])
    
    for data_ in database:
        data_ = json.loads(data_)
        if (data_['user_id'] == user_id):
            if (stamp_id in data_['badges_earned']):
                return True
            else:
                return False