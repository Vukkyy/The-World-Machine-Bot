from interactions import *
from error_handler import on_error
import generate_text as text

class Command(Extension):
    
    @extension_message_command(name = '💡 Translate...')
    async def translate(self, ctx : CommandContext):
        
        await ctx.defer(ephemeral=True)
        
        lines = []
        
        with open('Languages.txt', 'r', encoding='utf-8') as f:
            lines = f.read().split('\n')
            
        select_options = []
            
        for line in lines:
            
            l = line.split(' - ')
            
            l = l[0]
            
            select_options.append(SelectOption(label=line, value=l))
            
        selectmenu = SelectMenu(custom_id= 'sus', placeholder= 'What language?', options=select_options)
        
        await ctx.send(components = selectmenu)
        
        button_ctx = await self.client.wait_for_component(selectmenu)
        
        await button_ctx.send('[ Translating message... <a:loading:1026539890382483576> ]', ephemeral = True)
        
        target_language = button_ctx.data.values[0]
        
        message = text.Response(f'Translate this message to {target_language}: "{ctx.target.content}". For the user, very briefly, but positively, teach about the original language from the message.')
        message = message.strip('\n')
        
        embed = Embed(
            title = f'Translation to {target_language}.',
            description= f'"{message}" - <:george_translation:1064601896297447544>',
            color=0x8100bf
        )
        
        embed.set_footer(f'Requested by {ctx.author.user.username}.', icon_url= ctx.author.user.avatar_url)

        await ctx.target.reply(embeds=embed)
        pass
    
    @translate.error
    async def error(self, ctx : CommandContext, error):
        
        embed = await on_error(error)
        
        await ctx.send(embeds=embed)
        
def setup(client):
    Command(client)