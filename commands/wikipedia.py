from interactions import *
from bot_data.error_handler import on_error
from bot_data.embed_gen import fancy_send

class Command(Extension):
    
    @extension_command(description = 'A random wikipedia article.')
    async def wikipedia(self, ctx : CommandContext):
        await fancy_send(ctx, '[ [Here](https://en.wikipedia.org/wiki/Special:Random) is your random wikipedia article. ]')
    
    @wikipedia.error
    async def error(self, ctx : CommandContext, error):
        
        embed = await on_error(error)
        
        await ctx.send(embeds=embed)
        
def setup(client):
    Command(client)