from PIL import Image, ImageDraw, ImageFont
import textwrap
from asyncio import sleep
import aiohttp
import aiofiles
 
async def test(l1, image_url, uuid):
    img = Image.open("Images/niko-background.png") # Opening Images for both the background...
    
    await DownloadImage(image_url=image_url, filename='Images/niko.png')
    
    icon = Image.open("Images/niko.png") #...And the niko face selected in the command

    fnt = ImageFont.truetype("font/TerminusTTF-Bold.ttf", 20) # Font
    
    d = ImageDraw.Draw(img) # Textbox background
    # The X and Y starting positions
    text_x = 20
    text_y = 17
    for line in textwrap.wrap(l1, width=46): # Text Wrap Length
        d.text((text_x, text_y), line, font=fnt, fill=(255,255,255)) # Text and Text Wrapping
        text_y += 25 # Width of line breaks, by y value
      
    img.paste(icon, (496, 16), icon.convert('RGBA')) # The face sprite to use on the textbox
    
    img.save(f'Images/{uuid}.png')
    
    await sleep(0.2)
    
async def DownloadImage(image_url, filename):
    async with aiohttp.ClientSession() as session:
        async with session.get(image_url) as resp:
            if resp.status == 200:
                f = await aiofiles.open(filename, mode='wb')
                await f.write(await resp.read())
                await f.close()