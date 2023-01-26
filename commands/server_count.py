from interactions import *
from bot_data.error_handler import on_error

class Command(Extension):
    
    @extension_command(description = 'View how many servers the bot is in.')
    async def server_count(self, ctx : CommandContext):
        
        await ctx.send(f'[ I am in **{len(self.client.guilds)}** servers. ]')
        pass
    
    @server_count.error
    async def error(self, ctx : CommandContext, error):
        
        embed = await on_error(error)
        
        await ctx.send(embeds=embed)
        
def setup(client):
    Command(client)