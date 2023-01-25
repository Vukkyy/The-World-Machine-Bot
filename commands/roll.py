from interactions import *
from bot_data.error_handler import on_error
import random

class Command(Extension):
    
    @extension_command(description = 'Roll a dice.')
    @option(description='What sided dice to roll.')
    async def roll(self, ctx : CommandContext, sides : int):
        
        dice = random.randint(1, sides)
        
        description = None
        
        g_val = int(round((dice / sides) * 255, -1))
        
        color = (0, g_val, 0)
        color = '0x%02x%02x%02x' % color
            
        embed = Embed(title = f'Rolling d{sides}...', description = f'[ Rolled a **{dice}** ]', color=eval(color))
        embed.set_thumbnail('https://cdn.discordapp.com/emojis/1026181557230256128.png?size=96&quality=lossless')
        
        print(dice)
        
        await ctx.send(embeds=embed)
    
    @roll.error
    async def error(self, ctx : CommandContext, error):
        
        embed = await on_error(error)
        
        await ctx.send(embeds=embed)
        
def setup(client):
    Command(client)