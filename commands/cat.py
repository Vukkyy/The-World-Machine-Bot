from interactions import *
from bot_data.error_handler import on_error
from bot_data.embed_gen import fancy_send
import requests
import json
import random

class Command(Extension):
    @extension_command(description = 'Random Cat. Meow.')
    async def cat(self, ctx : CommandContext):
        
        embed = Embed(
            title='You found...',
            color=0x7e00b8
        )
        
        if random.randint(0, 100) == 67:
            embed.description = 'Niko!'
            embed.set_image('https://cdn.discordapp.com/attachments/1028022857877422120/1075445796113219694/ezgif.com-gif-maker_1.gif')
            embed.set_footer('A 1 in 100 chance! Lucky!')
            return await ctx.send(embeds=embed)
        
        data = requests.get('https://api.thecatapi.com/v1/images/search')
        
        json_data = json.loads(data.text)
        
        image = json_data[0]['url']
        
        embed.description = 'a cat!'
        embed.set_image(image)
        embed.set_footer('thecatapi.com')
        return await ctx.send(embeds=embed)
    
    @cat.error
    async def error(self, ctx : CommandContext, error):
        
        embed = await on_error(error)
        
        await ctx.send(embeds=embed)
        
def setup(client):
    Command(client)