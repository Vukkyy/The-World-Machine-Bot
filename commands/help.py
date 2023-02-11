from interactions import *
from bot_data.error_handler import on_error
from bot_data.embed_gen import fancy_send

class Command(Extension):
    
    @extension_command(description = 'Put Command Description here.')
    async def help(self, ctx : CommandContext):
        await fancy_send(ctx, '[ You can view all of my commands [here](https://theworldmachinebot.carrd.co/). ]', ephemeral=True)
    
    @help.error
    async def error(self, ctx : CommandContext, error):
        
        embed = await on_error(error)
        
        await ctx.send(embeds=embed)
        
def setup(client):
    Command(client)