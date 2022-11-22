import interactions
import database_manager as db
import Badges.stamp_viewer as view

class Profile(interactions.Extension):
    
    profile_background_choices = [
        interactions.Choice(
            name='Normal',
            value='Normal'
        ),
        interactions.Choice(
            name='Red',
            value='Red'
        ),
        interactions.Choice(
            name='Blue',
            value='Blue'
        ),
        interactions.Choice(
            name='Green',
            value='Green'
        ),
        interactions.Choice(
            name='Yellow',
            value='Yellow'
        ),
        interactions.Choice(
            name='Pink',
            value='Pink'
        ),
    ]
    
    def __init__(self, client):
        print('Profile settings loaded!')
        
    @interactions.extension_command()
    async def profile(self, ctx):
        pass
    
    @profile.subcommand(description='Change your profile background.')
    @interactions.option(description='The profile background to set to.', choices = profile_background_choices, required = True)
    async def set_background(self, ctx : interactions.CommandContext, choice : str = 'Normal'):
        id_ = int(ctx.author.id)
        
        await db.GetDatabase(id_, 'profile', {"uid": id_, "profile_background": "Normal", "profile_description": "I am a very mysterious person!"})
        await db.SetDatabase(id_, 'profile', 'profile_background', choice)
        
        await ctx.send(f'Successfully set profile background to: ``{choice}``', ephemeral = True)
        
    @profile.subcommand(description='Change your profile description.')
    @interactions.option(description='Set profile description, with a maximum of 100 characters.', max_length = 100, required = True)
    async def set_description(self, ctx : interactions.CommandContext, description : str = "I am a very mysterious person!"):
        id_ = int(ctx.author.id)
        
        await db.GetDatabase(id_, 'profile', {"uid": id_, "profile_background": "Normal", "profile_description": "I am a very mysterious person!"})
        await db.SetDatabase(id_, 'profile', 'profile_description', description)
        
        await ctx.send(f'Successfully set profile description to: ``{description}``', ephemeral = True)
        
    @profile.subcommand(description='View a profile.')
    @interactions.option(description='The user\'s profile to view.', required=True, type=interactions.OptionType.USER)
    async def view(self, ctx : interactions.CommandContext, user : interactions.User):
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

        img_ = interactions.File('Badges/result.png')

        await msg.edit('', files = img_)

def setup(client):
    Profile(client)