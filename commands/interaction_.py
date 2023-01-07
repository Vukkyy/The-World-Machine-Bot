from interactions import *

class Command(Extension):
    
    def load_interactions(self):
        select = [
            SelectOption(
                label='Hug',
                value=0
            ),
            SelectOption(
                label='Cuddle',
                value=1
            ),
            SelectOption(
                label='Kiss',
                value=2
            ),
            SelectOption(
                label='Pet',
                value=3
            ),
            SelectOption(
                label='Slap',
                value=4
            ),
            SelectOption(
                label='Stab',
                value=5
            ),
        ]
        
        return SelectMenu(options=select, custom_id='interaction', placeholder='What interaction do you want to use on this person?')
    
    async def result(self, ctx : CommandContext, user, interaction, targeted_user : User):

        interaction = int(interaction)
        
        interaction_data = {"name" : "[ UNIDENTIFIED ]", "action" : "[ UNIDENTIFIED ]"}
        
        if interaction == 0:
            interaction_data = {"name" : "Hug", "action" : "hugged"}
        if interaction == 1:
            interaction_data = {"name" : "Cuddle", "action" : "cuddled"}
        if interaction == 2:
            interaction_data = {"name" : "Kiss", "action" : "kissed"}
        if interaction == 3:
            interaction_data = {"name" : "Pet", "action" : "petted"}
        if interaction == 4:
            interaction_data = {"name" : "Slap", "action" : "slapped"}
        if interaction == 5:
            interaction_data = {"name" : "Stab", "action" : "stabbed"}
                
        name = interaction_data['name']
        action = interaction_data['action']
        
        embed = Embed(
            title = f'{name}!',
            description = f'<@{user}> {action} <@{targeted_user.id}>!',
            color=0x7d00b8
        )
        
        button = Button(
            style=ButtonStyle.DANGER,
            label=f'{name} back!',
            custom_id='AAAAA'
        )
        
        
        
        if targeted_user.id == user:
            
            if interaction == 5:
                await ctx.send('[ Hey! Don\'t do that. Do you need to talk to someone? ]', ephemeral = True)
                return
            
            await ctx.defer(edit_origin=True)
            
            embed = Embed(
                title = f'{name}!',
                description = f'<@{user}> {action} themselves.',
                color=0x7d00b8
            )
            
            await ctx.channel.send(embeds=embed)

            return
        
        await ctx.defer(edit_origin=True)
        
        msg = await ctx.channel.send(embeds=embed, components=button)
        
        async def check(button_ctx):
            if button_ctx.author.id != targeted_user.id:
                await ctx.send('[ Sorry! But you can\'t respond to this interaction! ]', ephemeral = True)
                return False
            if interaction == 5:
                await ctx.send('[ You can\'t stab back, you\'re already dead! ]', ephemeral = True)
                return False
            return True
        
        if not targeted_user.bot:
            button_ctx = await self.client.wait_for_component(button, check=check)
        else:
            button_ctx = ctx
            
        await msg.edit(components = [])
        
        embed = Embed(
            title = f'{name} back!',
            description = f'<@{targeted_user.id}> {action} <@{user}> back!',
            color=0x7d00b8
        )
        
        msg = await msg.reply(embeds = embed)
        
        await msg.create_reaction('♥')
    
    @extension_command(description = 'Do an interaction towards someone.')
    @option(description='The user to do interaction to.')
    async def interaction(self, ctx : CommandContext, user : User):
        
        component = Command.load_interactions(self)
        
        await ctx.send(components = component, ephemeral = True)
        
        async def check(ctx):
            if ctx.data.values[0] == "5" and user.bot:
                await ctx.send('[ You can\'t kill bots. ]', ephemeral = True)
                return False
            return True
        
        component_ctx = await self.client.wait_for_component(component, check=check)
        
        await Command.result(self, component_ctx, ctx.author.id, component_ctx.data.values[0], user)
        
    @extension_user_command(name = '💡 Interact...')
    async def interact(self, ctx : CommandContext):
        await Command.interaction(ctx = ctx, user = ctx.target)
    
        
def setup(client):
    Command(client)