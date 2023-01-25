from interactions import *
from bot_data.error_handler import on_error
from interactions.ext.database.database import Database

class Command(Extension):
    
    @extension_listener
    async def on_start(self):
        await Database.create_database('notifications', Database.DatabaseType.GUILD, {'can_notify' : True})
    
    @extension_command(description = 'Toggle whether achievement stamps are shown on this server.')
    async def stamp_notifications(self, ctx : CommandContext):
        if await ctx.author.has_permissions(Permissions.MANAGE_CHANNELS):
            db = await Database.get_item(ctx, 'notifications')
            can_notify = db['can_notify']
            
            if can_notify:
                await Database.set_item(ctx, 'notifications', {'can_notify' : False})
            else:
                await Database.set_item(ctx, 'notifications', {'can_notify' : True})
                
            await ctx.send(f'[ Set achievement stamp notifications to ``{str(not can_notify)}``. ]', ephemeral = True)
            return
        
        await ctx.send('[ You need the ``MODIFY_CHANNELS`` permission to execute this command. ]', ephemeral = True)
        pass
    
    @stamp_notifications.error
    async def error(self, ctx : CommandContext, error):
        
        embed = await on_error(error)
        
        await ctx.send(embeds=embed)
        
def setup(client):
    Command(client)