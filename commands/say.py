from interactions import *
from bot_data.error_handler import on_error
import bot_data.profile_icons as icons
import json
import bot_data.dialogue_generator as dialogue_generator
from interactions.ext.database.database import Database
from uuid import uuid4
import os
from bot_data.embed_gen import fancy_send

class Command(Extension):
    
    @extension_command(description = 'Make OneShot characters say whatever you want.')
    @option(description = 'What you want the character to say.', max_length = 184)
    async def say(self, ctx : CommandContext, text : str):
        async def check(ctx):
            return True

        text__ = icons.Emojis()
        
        select_menu = SelectMenu(
            custom_id='Custom_Select_Menu_For a ' + str(ctx.guild_id),
            disabled=True,
            options = [SelectOption(label='none', value='none')],
            placeholder='...'
        )

        msg = await fancy_send(ctx, f"[ <@{ctx.author.id}>, select a character. ]", ephemeral=True, components=text__)
        
        char_ctx : ComponentContext = await self.client.wait_for_component(text__)

        text_ = None

        val_char = char_ctx.data.values[0]
        
        options = []
        
        json_data = {}

        with open('bot_data/characters.json', 'r') as f:
            json_data = json.loads(f.read())
    
        characters = json_data['characters']
        
        char = None
        
        for character in characters:
            if character['name'] == val_char:
                char = character
                break
        
        for face in char['faces']:
            options.append(
                SelectOption(
                    label=face['face_name'],
                    value=face['id'],
                    emoji=Emoji(id=face['id'])
                )
            )
    
        select_menu = SelectMenu(
            custom_id='Custom_Select_Menu_For b ' + str(ctx.guild_id),
            disabled=False,
            options=options,
            placeholder='Select a face!'
        )
        
        text__.disabled = True
        
        await fancy_send(char_ctx, f"[ <@{ctx.author.id}>, select a face. ]", components=select_menu, ephemeral = True)
            
        char_ctx : ComponentContext = await self.client.wait_for_component(select_menu)

        value = char_ctx.data.values[0]

        msg = await fancy_send(char_ctx, "[ Generating Image... <a:loading:1026539890382483576> ]")
        
        uuid = uuid4()
        
        uuid = str(uuid)
        
        emoji = Emoji(id=value)
        
        await dialogue_generator.test(text, emoji.url, uuid)
        await msg.delete()
        file = File(filename=f'Images/{uuid}.png', description=text)
        await ctx.channel.send(f"[ Generated by <@{int(ctx.author.id)}>. ]", files=file)
        
        os.remove(f'Images/{uuid}.png')
        
        pass
        
def setup(client):
    Command(client)