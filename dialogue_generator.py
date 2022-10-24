from PIL import Image, ImageDraw, ImageFont
import textwrap
 
async def test(l1):
    img = Image.open("Images/niko-background.png") # Opening Images for both the background...
    icon = Image.open("Images/niko.png") #...And the niko face selected in the command

    fnt = ImageFont.truetype("font/TerminusTTF-Bold.ttf", 20) # Font
    
    d = ImageDraw.Draw(img) # Textbox background
    # The X and Y starting positions
    text_x = 21
    text_y = 19
    for line in textwrap.wrap(l1, width=46): # Text Wrap Length
        d.text((text_x, text_y), line, font=fnt, fill=(255,255,255)) # Text and Text Wrapping
        text_y += 25 # Width of line breaks, by y value
      
    img.paste(icon, (496, 14), icon.convert('RGBA')) # The face sprite to use on the textbox
    
    img.save('Images/pil_text.png')