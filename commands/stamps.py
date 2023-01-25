from interactions import *
from bot_data.error_handler import on_error
import Badges.stamp_list as stamp_list
import Badges.stamp_system as stamps
import uuid

class Command_(Extension):
    
    @extension_command(description = 'Put Command Description here.')
    async def letters(self, ctx : CommandContext):
        # await ctx.send('hello world')
        pass
    
    @letters.subcommand(description='Equip a stamp.')
    async def equip_stamp(self, ctx : CommandContext):
        stamps_ = await stamp_list.OpenStampMenu(int(ctx.author.id))

        select = SelectMenu(
            options = stamps_,
            placeholder = 'Default Stamp',
            custom_id = 'selectmenuuusfkhjfsdkhjfsdhj'
        )

        await ctx.send('[ Select a stamp you have unlocked. ]', components = select, ephemeral = True)

        async def check(ctx):
            return True

        select_ctx = await self.client.wait_for_component(components=select)

        await stamps.GetCurrentBadge(int(ctx.author.id), True, select_ctx.data.values[0])

        await select_ctx.send(f'[ Stamp change successful! ]', ephemeral = True)
        
    @letters.subcommand(name = 'opt-in', description='Opt in or out for letter sending.')
    async def awesome(self, ctx : CommandContext):
        button = Button(
            style = ButtonStyle.PRIMARY,
            label = 'Yes',
            custom_id = str(uuid.uuid4())
        )
        
        with open('databases/loveletters.db', 'r') as f:
            lllist = f.readlines()
            
            lllist = [line.strip() for line in lllist]
        
            if (ctx.author.id in lllist):
                
                with open('databases/loveletters.db', 'w') as db:
                    lllist.remove(str(ctx.author.id))

                    result = '\n'.join(lllist)
                    
                    db.write(result)

                await ctx.send('[ You have opted out from recieving (and sending!) letters. If you wish to recieve or send letters again, run this command again. ]', ephemeral=True)
            else:        
                await ctx.send('[ Are you sure you want to recieve (and send) letters? ]', components=button, ephemeral=True)

                button_ctx = await self.client.wait_for_component(components=button)
                
                with open('databases/loveletters.db', 'w') as db:
                    lllist.append(str(ctx.author.id))
                    
                    result = '\n'.join(lllist)
                    
                    db.write(result)
                    
                await button_ctx.send('[ You will now recieve letters. To opt out of this, run this command again. ]', ephemeral=True)
                
    async def letter(self, ctx : CommandContext, user : Member, message : str):
        
        with open ('databases/loveletters.db', 'r') as db:
            lllist = db.read()
            lllist = lllist.split('\n')

        embed = Embed(
            description = f'{message}',
            footer = EmbedFooter(text= f'Sent by {ctx.author.user.username} in {ctx.guild.name}', icon_url = ctx.author.user.avatar_url),
            author = EmbedAuthor(name = '💌 You got a letter!'),
            thumbnail = EmbedImageStruct(url = await stamps.GetCurrentBadge(int(ctx.author.id), False, 0)),
            color = 0xd0d2d7
        )
        
        awesome = None
        
        if user.user.bot:
            await ctx.send('[ Cannot send letters to bots. ]', ephemeral=True)
            return

        if (user.id in lllist and ctx.author.id in lllist or ctx.author.id == 302883948424462346):
            try:
                awesome = await user.send(embeds=embed)
                
                await ctx.send('[ Successfully sent letter! ]', ephemeral=True)
            except:
                await ctx.send('[ Cannot send letters to this user. ]', ephemeral=True)
                return

            await stamps.IncrementValue(ctx, 'letters_sent', int(ctx.author.id))
            if (ctx.author.id == 302883948424462346):
                await stamps.IncrementValue(ctx, 'owner_letter', int(user.id))
            
        elif (not user.id in lllist):
            await ctx.send('[ This user has not opted in for recieving letters. Ask the other person to use `/letters opt-in` to recieve letters. ]', ephemeral=True)
        else:
            await ctx.send('[ In order to send letters, you need to opt in. Use `/letters opt-in` to recieve and send letters. ]', ephemeral=True)

    async def send_letter(self, ctx, user):
        modal_ = Modal(
            custom_id = 'Mooodal',
            title = 'Send a letter!',
            components = [
                TextInput(
                    style = TextStyleType.SHORT,
                    label = "Send your Letter!",
                    custom_id = 'djhsfdjkhhsdfkjh'
                )
            ]
        )
        
        print('sending letter...')

        await ctx.popup(modal_)

        modal_ctx = await self.client.wait_for_modal(modal_)
        
        letter = modal_ctx[0].data.components[0].components[0].value
        
        await Command_.letter(self, modal_ctx[0], user, letter)
    
    @letters.subcommand(description='Send a letter.')
    @option(description='The user to send a letter to.')
    async def send(self, ctx : CommandContext, user : User):
        await Command_.send_letter(self, ctx, user)

    @extension_user_command(name = '💡 Send Letter...')
    async def send_(self, ctx : CommandContext):
        await Command_.send_letter(self, ctx, ctx.target)
        
    @letters.error
    async def error(self, ctx : CommandContext, error):
        
        embed = await on_error(error)
        
        await ctx.send(embeds=embed)
        
def setup(client):
    Command_(client)