import database_manager as db
import Badges.stamp_viewer as view

from interactions import *
from interactions.ext.wait_for import *

class Profile(Extension):
    
    def __init__(self, client):
        print('Profile settings loaded!')
        
    def GetValues(index):
        values = []
        
    @extension_command()
    async def profile(self, ctx):
        pass
    
    @profile.subcommand(description='Edit your profile.')
    async def edit(self, ctx : CommandContext):
        
        edit_buttons = [
            Button(label='Edit Background', custom_id='background', style=ButtonStyle.PRIMARY),
            Button(label='Edit Description', custom_id='description', style=ButtonStyle.PRIMARY),
        ]
        
        await ctx.send('What do you want to edit?', components=edit_buttons, ephemeral = True)
        
        while True:
            button_ctx : ComponentContext = await wait_for_component(self.client, edit_buttons)
            
            data = button_ctx.data.custom_id
            
            if (data == 'description'):
                modal = Modal(
                    title = 'Edit Profile Description',
                    components=[TextInput(label = 'Description', style=TextStyleType.SHORT, custom_id='Among Us', max_length=100, placeholder='I am a very mysterious person!')],
                    custom_id='ModalSus'
                )
                
                await button_ctx.popup(modal)
                
            if (data == 'background'):
                
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
                
                SelectOption_ : ComponentContext = await wait_for_component(self.client, components = menu)
                
                id_ = int(ctx.author.id)
        
                await db.GetDatabase(id_, 'profile', {"uid": id_, "profile_background": "Normal", "profile_description": "I am a very mysterious person!"})
                await db.SetDatabase(id_, 'profile', 'profile_background', SelectOption_.data.values[0])
                
                await button_ctx.send(f'Successfully set profile background to: ``{SelectOption_.data.values[0]}``, use </profile view:8328932897324897> to view your changes.', ephemeral = True)

            if (data == 'stamp'):
                await button_ctx.send('Simply use </select_stamp:100> to select a stamp to use both in letters and your profile!', ephemeral = True)
                
            if (data == 'character'):
                await button_ctx.send('Simply use </transmit hidden-profile:100> to select a character to use for Transmissions and your profile!', ephemeral = True)
            
    @profile.subcommand(description='View a profile.')
    @option(description='The user\'s profile to view.', required=True, type=OptionType.USER)
    async def view(self, ctx : CommandContext, user : User):
        id_ = 0

        msg = ''

        user_ = ''

        if (user == 'none'):
            id_ = int(ctx.author.id)
            user = ctx.author
            msg = 'Loading your profile... <a:loading:1026539890382483576>'
            user_ = ctx.author.user.username
        else:
            id_ = int(user.id)
            msg = f'Loading {user.user.username}\'s profile... <a:loading:1026539890382483576>'
            user_ = user.user.username
        
        msg = await ctx.send(msg)

        print(user_)
        
        await view.DrawBadges(id_, user_, user.avatar_url)

        img_ = File('Badges/result.png')
        
        edit_profile_button = Button(label='Edit Profile', custom_id='editprofile', style=ButtonStyle.SUCCESS)

        await msg.edit('', files = img_, components=edit_profile_button)
        
        while True:
            edit_profile : ComponentContext = await wait_for_component(self.client, edit_profile_button)
            
            if edit_profile.author.id != ctx.author.id:
                edit_profile.send('Sorry! Only the person that owns this profile can edit it!', ephemeral=True)
                return
            
            edit_buttons = [
                Button(label='Edit Background', custom_id='background', style=ButtonStyle.PRIMARY),
                Button(label='Edit Description', custom_id='description', style=ButtonStyle.PRIMARY),
                Button(label='How to change stamp?', custom_id='stamp', style=ButtonStyle.PRIMARY),
                Button(label='How to change character?', custom_id='character', style=ButtonStyle.PRIMARY),
            ]
        
            await edit_profile.send('What do you want to edit?', components=edit_buttons, ephemeral = True)
            
            button_ctx : ComponentContext = await wait_for_component(self.client, edit_buttons)
            
            data = button_ctx.data.custom_id
            
            if (data == 'description'):
                modal = Modal(
                    title = 'Edit Profile Description',
                    components=[TextInput(label = 'Description', style=TextStyleType.SHORT, custom_id='Among Us', max_length=100, placeholder='I am a very mysterious person!')],
                    custom_id='ModalSus'
                )
                
                await button_ctx.popup(modal)
                
            if (data == 'background'):
                
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
                
                SelectOption_ : ComponentContext = await wait_for_component(self.client, components = menu)
                
                id_ = int(ctx.author.id)
        
                await db.GetDatabase(id_, 'profile', {"uid": id_, "profile_background": "Normal", "profile_description": "I am a very mysterious person!"})
                await db.SetDatabase(id_, 'profile', 'profile_background', SelectOption_.data.values[0])
                
                await button_ctx.send(f'Successfully set profile background to: ``{SelectOption_.data.values[0]}``, use </profile view:8328932897324897> to view your changes.', ephemeral = True)

            if (data == 'stamp'):
                await button_ctx.send('Simply use </select_stamp:100> to select a stamp to use both in letters and your profile!', ephemeral = True)
                
            if (data == 'character'):
                await button_ctx.send('Simply use </transmit hidden-profile:100> to select a character to use for Transmissions and your profile!', ephemeral = True)
    @extension_modal('ModalSus')
    async def set_description(self, ctx : CommandContext, description : str):
        id_ = int(ctx.author.id)
        
        await db.GetDatabase(id_, 'profile', {"uid": id_, "profile_background": "Normal", "profile_description": "I am a very mysterious person!"})
        await db.SetDatabase(id_, 'profile', 'profile_description', description)
        
        await ctx.send(f'Successfully set profile description to: ``{description}``, use </profile view:8328932897324897> to view your changes.', ephemeral = True)

def setup(client):
    Profile(client)