from interactions import *
from error_handler import on_error
from interactions.ext.database.database import Database
import Badges.stamp_viewer as view
from uuid import uuid4
import os

class Command(Extension):
    
    def GetValues(self, index):
        values = []
        
    @extension_command()
    async def profile(self, ctx):
        pass
    
    @extension_listener
    async def on_start(self):
        await Database.create_database('profile_information', Database.DatabaseType.USER, {"uid": 0, "profile_background": "Normal", "profile_description": "I am a very mysterious person!"})
    
    @profile.subcommand(description='Edit your profile.')
    async def edit(self, ctx : CommandContext):
        
        uid = uuid4()
        
        edit_buttons = [
            Button(label='Edit Background', custom_id=f'background{uid}', style=ButtonStyle.PRIMARY),
            Button(label='Edit Description', custom_id=f'description{uid}', style=ButtonStyle.PRIMARY),
            Button(label='Edit Stamp', custom_id=f'stamp{uid}', style=ButtonStyle.PRIMARY),
        ]
        
        await ctx.send('What do you want to edit?', components=edit_buttons, ephemeral = True)
        
        while True:
            button_ctx : ComponentContext = await self.client.wait_for_component(edit_buttons)
            
            data = button_ctx.data.custom_id
            
            if (data == f'description{uid}'):
                modal = Modal(
                    title = 'Edit Profile Description',
                    components=[TextInput(label = 'Description', style=TextStyleType.SHORT, custom_id='Among Us', max_length=100, placeholder='I am a very mysterious person!')],
                    custom_id='ModalSus'
                )
                
                await button_ctx.popup(modal)
                
            if (data == f'background{uid}'):
                
                profile_background_choices = [
                    SelectOption(
                        label='Normal',
                        value='Normal'
                    ),
                    SelectOption(
                        label='Red',
                        value='Red'
                    ),
                    SelectOption(
                        label='Blue',
                        value='Blue'
                    ),
                    SelectOption(
                        label='Green',
                        value='Green'
                    ),
                    SelectOption(
                        label='Yellow',
                        value='Yellow'
                    ),
                    SelectOption(
                        label='Pink',
                        value='Pink'
                    ),
                ]
                
                menu = SelectMenu(custom_id='selection', options=profile_background_choices)
                
                await button_ctx.send('Select a profile background.', components=menu, ephemeral=True)
                
                SelectOption_ : ComponentContext = await self.client.wait_for_component(menu)
                
                id_ = int(ctx.author.id)
        
                await Database.set_item(ctx, 'profile_information', {'profile_background' : SelectOption_.data.values[0]})
                
                await button_ctx.send(f'[ Successfully set profile background to: ``{SelectOption_.data.values[0]}``, use </profile view:8328932897324897> to view your changes. ]', ephemeral = True)

            if (data == f'stamp{uid}'):
                await button_ctx.send('[ Simply use </select_stamp:100> to select a stamp to use both in letters and your profile. ]', ephemeral = True)
            
    @profile.subcommand(description='View a profile.')
    @option(description='The user\'s profile to view.', required=True, type=OptionType.USER)
    async def view(self, ctx : CommandContext, user : User):
        id_ = 0

        msg = ''

        user_ = ''

        if (user == 'none'):
            id_ = int(ctx.author.id)
            user = ctx.author
            msg = '[ Loading your profile... <a:loading:1026539890382483576> ]'
            user_ = ctx.author.user.username
        else:
            id_ = int(user.id)
            msg = f'[ Loading {user.user.username}\'s profile... <a:loading:1026539890382483576> ]'
            user_ = user.user.username
        
        msg = await ctx.send(msg)

        print(user_)
        
        await view.DrawBadges(id_, user_, user.avatar_url)

        img_ = File('Badges/result.png')
        
        await msg.edit('', files = img_)
        
        os.remove('Badges/result.png')
    @extension_modal('ModalSus')
    async def set_description(self, ctx : CommandContext, description : str):
        id_ = int(ctx.author.id)
        
        await Database.set_item(ctx, 'profile_information', {'profile_description' : description})
        
        await ctx.send(f'[ Successfully set profile description to: ``{description}``, use </profile view:8328932897324897> to view your changes. ]', ephemeral = True)

    
    @profile.error
    async def error(self, ctx : CommandContext, error):
        
        embed = await on_error(error)
        
        await ctx.send(embeds=embed)
        
def setup(client):
    Command(client)