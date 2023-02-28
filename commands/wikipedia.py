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
    
    @extension_command(description = 'A random wikipedia article.')
    async def amogus(self, ctx : CommandContext):
        await ctx.send('https://media.discordapp.net/attachments/868336598067056690/958829667513667584/1c708022-7898-4121-9968-0f0d24b8f986-1.gif')
def setup(client):
    Command(client)