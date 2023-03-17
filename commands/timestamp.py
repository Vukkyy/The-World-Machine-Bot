from interactions import *
from bot_data.error_handler import on_error
from bot_data.embed_gen import fancy_send

from datetime import datetime

class Command(Extension):
    
    @extension_command(description = 'Generate a timestamp. (UTC ONLY)')
    @option(description = 'Set the hour.', min_value = 1, max_value = 12)
    @option(description = 'Set the minute.', min_value = 0, max_value = 59)
    @option(description = 'AM or PM?', choices = [Choice(name='AM', value=0), Choice(name='PM', value=12)])
    async def timestamp(self, ctx : CommandContext, hour : int, minutes : int, am_pm : int):
        
        today = datetime.today().strftime('%m/%d/%y')
        
        date = f'{today} {hour + am_pm}:{minutes}:00'
        
        datetime_object = datetime.strptime(date, '%m/%d/%y %H:%M:%S')
        
        time = int(datetime_object.timestamp())
        
        await fancy_send(ctx, f'Here is your formatted time. Copy and paste this into any message. `<t:{time}:t>`', ephemeral=True)
    
    @timestamp.error
    async def error(self, ctx : CommandContext, error):
        
        embed = await on_error(error)
        
        await ctx.send(embeds=embed)
        
def setup(client):
    Command(client)