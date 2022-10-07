from PIL import Image, ImageDraw, ImageFont, ImageEnhance
from os import listdir
import Badges.stamp_list as list_
import aiohttp        
import aiofiles
import Badges.stamp_system as stamps_
import json
    
async def DrawBadges(user_id : int, user : str = 'awesome person'):
    print('Viewing Badges...')

    images = []

    for stamp in list_.stamps:
        images.append(f'https://cdn.discordapp.com/emojis/{stamp["stamp_url"]}.png')

    msg = f'{user}\'s unlocked stamps:'

    print(user)

    bg = Image.open('Badges/background.png')

    equipped = await stamps_.GetCurrentBadge(user_id, False, '')

    async with aiohttp.ClientSession() as session:
            async with session.get(equipped) as resp:
                if resp.status == 200:
                    f = await aiofiles.open('Badges/equipped.png', mode='wb')
                    await f.write(await resp.read())
                    await f.close()

    img_equipped = Image.open('Badges/equipped.png')

    width, height = bg.size

    fnt = ImageFont.truetype("font/TerminusTTF-Bold.ttf", 25) # Font
    
    d = ImageDraw.Draw(bg)

    w, h = fnt.getsize(msg)

    text_x = ((width - w) / 2)
    text_y = 40

    d.text((text_x, text_y), msg, font=fnt, fill=(255,255,255))

    d.text((30, height - 60), 'Equipped Stamp:', font = fnt, fill=(255,255,255))
    
    icons = []
    ids = []

    idx = 0
    
    for item in images:
        print(item)
        async with aiohttp.ClientSession() as session:
            async with session.get(item) as resp:
                if resp.status == 200:
                    f = await aiofiles.open('Badges/icon.png', mode='wb')
                    await f.write(await resp.read())
                    await f.close()
        img = Image.open('Badges/icon.png')
        img = img.convert('RGBA')
        img = img.resize((60, 60), Image.Resampling.NEAREST)
        icons.append(img)
        ids.append(list_.stamps[idx]['stamp_id'])

        idx += 1

    init_index = 68
    
    index = init_index

    i = 0

    pos_y = 80
    
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
        bg.paste(img_equipped, (230, height - 65), img_equipped.convert('RGBA'))
        index += 100
        
        if (i > 5):
            index = init_index
            pos_y += 70
            i = 0

    bg.save('Badges/result.png')
    print('finished')

async def GetStamps(user_id, stamp_id):

    db = ''
        
    with open('user_database.json', 'r') as f:
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