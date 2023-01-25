from interactions import *
from bot_data.error_handler import on_error

class Command(Extension):
    
    @extension_command(description = 'Put Command Description here.')
    async def command_name(self, ctx : CommandContext):
        # await ctx.send('hello world')
        pass
    
    @command_name.error
    async def error(self, ctx : CommandContext, error):
        
        embed = await on_error(error)
        
        await ctx.send(embeds=embed)
        
def setup(client):
    Command(client)