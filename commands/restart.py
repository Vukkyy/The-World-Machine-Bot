from interactions import *
from bot_data.error_handler import on_error
import bot_data.load_data as data
import requests

class Command(Extension):
    
    @extension_command(description = 'Put Command Description here.')
    async def restart(self, ctx : CommandContext):
        if (ctx.author.id == 302883948424462346 or ctx.author.id == 400054986530357268):
            await ctx.send('Restarting Now!')

            API_KEY = 'Bearer ' + data.load_config('SPARKED')

            header = {"Authorization" : API_KEY}
            r = requests.post('https://control.sparkedhost.us/api/client/servers/92aeea52/power', json={"signal": "restart"}, headers=header)
            print(r.status_code)
            return

        await ctx.send('You cannot use this command.', ephemeral = True)
        pass
    
    @restart.error
    async def error(self, ctx : CommandContext, error):
        
        embed = await on_error(error)
        
        await ctx.send(embeds=embed)
        
def setup(client):
    Command(client)