from interactions import *
from bot_data.error_handler import on_error
import random

class Command(Extension):
    
    @extension_command(description = 'Roll a dice.')
    @option(description='What sided dice to roll.', min_value = 1, max_value = 9999)
    @option(description='How many to roll.', min_value = 1, max_value = 10)
    async def roll(self, ctx : CommandContext, sides : int, amount : int = 1):
        
        dice = random.randint(1, sides)
        
        description = None
        
        g_val = int(round((dice / sides) * 255, -1))
        
        color = (0, g_val, 0)
        color = '0x%02x%02x%02x' % color
        
        if amount == 1:
            description = f'[ Rolled a **{dice}**. ]'
        else:    
            text = ''
            previous_total = 0
            total = 0
            
            for num in range(amount):
                    
                dice = random.randint(1, sides)
                
                if num == 0:
                    text = f'**{dice}**'
                    
                    previous_total = dice
                    continue
                
                text = f'{text}, **{dice}**'
                
                total = previous_total + dice
                
                previous_total = total
                    
            description = f'[ Rolled a {text}, totaling at **{total}**. ]'
            
        embed = Embed(title = f'Rolling d{sides}...', description = description, color=eval(color))
        embed.set_thumbnail('https://cdn.discordapp.com/emojis/1026181557230256128.png?size=96&quality=lossless')
        
        await ctx.send(embeds=embed)
    
    @roll.error
    async def error(self, ctx : CommandContext, error):
        
        embed = await on_error(error)
        
        await ctx.send(embeds=embed)
        
def setup(client):
    Command(client)