import asyncio
import re
import interactions
import os
import random
import uuid
import aiohttp        
import aiofiles
import requests
import json
import datetime
from dotenv import load_dotenv
load_dotenv()
import cleantext
import io
import validators

# Other Scripts
import custom_source
import dialogue_generator
import profile_icons as icons
import generate_text
import music_utilities as music
import Badges.stamp_system as stamps
import Badges.stamp_list as stamp_list
import Badges.stamp_viewer as view
from slur_detection import slurs

# Extension Libraries
from interactions.ext.wait_for import wait_for_component, setup, wait_for
from interactions.ext.lavalink import VoiceClient
import interactions.ext.files
from interactions.ext.enhanced import cooldown
import exts.music
import exts.transmit
import exts.embed_creator

TOKEN = os.getenv('BOT-TOKEN')

bot = VoiceClient(token=TOKEN, intents=interactions.Intents.DEFAULT | interactions.Intents.GUILD_MESSAGE_CONTENT)
    
bot.load('interactions.ext.files')
bot.load('exts.music')
bot.load('exts.transmit')
bot.load('exts.embed_creator')

setup(bot)

responses = []

@bot.event()
async def on_start():
    global responses

    stamps.setup(bot)

    random.shuffle(responses)

    await bot.change_presence(
        interactions.ClientPresence(
            status=interactions.StatusType.ONLINE,
            activities=[
                interactions.PresenceActivity(
                    name="On Little Cat Feet",
                    type=interactions.PresenceActivityType.LISTENING)
            ]))

    await change_picture()

    music.bot = bot
    
    print(f"{bot.me.name} is ready!")



async def change_picture():
    profile_pictures = icons.icons
    ran_num = random.randint(0, len(profile_pictures) - 1)
    picture = profile_pictures[ran_num]

    async with aiohttp.ClientSession() as session:
        url = picture
        async with session.get(url) as resp:
            if resp.status == 200:
                f = await aiofiles.open('Images/picture.png', mode='wb')
                await f.write(await resp.read())
                await f.close()

    image = interactions.Image("Images/picture.png")

    try:
        await bot.modify(avatar=image, username=bot.me.name)
    except:
        print("Couldn't change avatar. Whoops, either way...")


@bot.command(name="say",
             description="Repeats whatever the user puts in.",
             options=[
                 interactions.Option(name="text",
                                     description="The text to repeat.",
                                     required=True,
                                     type=interactions.OptionType.STRING)
             ])
async def say_command(ctx: interactions.CommandContext, text: str):
    #stops the bot from mass pinging users

        ban_list = []
        
        with open('ban_list.txt', 'r') as f:
            ban_list = f.readlines()
            
        if (str(ctx.author.id) in ban_list):
            await ctx.send('Sorry! But you are banned from using this command.', ephemeral = True)
            return
        
        print('among us')
    
        if '@' in text:
            await ctx.send('Please don\'t ping users with the say command! Contains: `@`', ephemeral = True)
            return
        
        slurs_ = []
        
        print('slur detection time')
        
        for slur in slurs:
            if slur in text.lower():
                await ctx.send(f'Please do not use slurs with the say command! Contains: `{slur}`', ephemeral = True)
                
                report_channel = await interactions.get(bot, interactions.Channel, object_id=1025158352549982299)
                
                await report_channel.send(f'User `{ctx.author.name}` with id `{ctx.author.id}` sent `{text}` with the say command.')
                return
            
        channel = ctx.channel
        await channel.send(text)
        msg = await ctx.send("** **") # Makes sure it returns something 
        await msg.delete()


@bot.command(name="text-generator",
             description="Generates text in the style of OneShot!",
             options=[
                 interactions.Option(
                     name="text",
                     description="The text to add.",
                     type=interactions.OptionType.STRING,
                     required=True,
                     max_length = 184
                 )
             ])
async def text_gen(ctx: interactions.CommandContext, text: str):

    async def check(ctx):
        return True

    text__ = icons.Emojis()

    msg = await ctx.send(f"<@{ctx.author.id}>, select a character!", components=text__, ephemeral=True)
    
    char_ctx : interactions.ComponentContext = await wait_for_component(bot, components=text__, check=check)

    text_ = None

    val_char : int = int(char_ctx.data.values[0])

    if (val_char == 0):
        text_ = await icons.GenerateModalNiko()
        
    elif (val_char == 1):
        print('lol')
        text_ = await icons.GenerateModalTWM()
        
    elif (val_char == 2):
        text_ = await icons.GenerateModalKip()

    print(text_)

    await char_ctx.send(f"<@{ctx.author.id}>, select a text face!", components=text_[0], ephemeral=True)
    
    text_ctx : interactions.ComponentContext = await wait_for_component(bot, components=text_[0], check=check)
    
    val = int(text_ctx.data.values[0])

    print(val)

    selection = text_[1][val] # this looks like ass but whatever

    emoji = selection.emoji.url

    print(emoji)
    
    async with aiohttp.ClientSession() as session:
        url = emoji
        async with session.get(url) as resp:
            if resp.status == 200:
                f = await aiofiles.open('Images/niko.png', mode='wb')
                await f.write(await resp.read())
                await f.close()

    msg = await text_ctx.send("Generating Image... <a:loading:1026539890382483576>")
    await dialogue_generator.test(text)
    await msg.delete()
    file = interactions.File(filename="Images/pil_text.png")
    await ctx.channel.send(f"Generated by: {ctx.author.name}", files=file)


# --------------------------------------------------------------------
    

@bot.command(
    name = "purge",
    description = "Delete multiple messages at once. User must have the 'Administrator' Permission.",
    default_member_permissions=interactions.Permissions.ADMINISTRATOR,
    options = [
        interactions.Option(
            name = "amount",
            required = True,
            description = "The amount of messages to delete up to 100.",
            type = interactions.OptionType.INTEGER,
            max_value = 100
        )
    ]
)
async def testing_lol(ctx : interactions.CommandContext, amount : int):
    await ctx.channel.purge(amount)
    await ctx.send(f"Deleted {amount} messages.", ephemeral=True)

@bot.command(
    name = "actions",
    description = "Do an action towards someone.",
    options = [
        interactions.Option(
            name = "choices",
            description = "The action you wish to do",
            type = interactions.OptionType.STRING,
            required = True,
            choices = [
                interactions.Choice(
                    name = "Hug",
                    value = 'hugg'
                ),

                interactions.Choice(
                    name = "Kiss",
                    value = 'kiss'
                ),

                interactions.Choice(
                    name = "Cuddle",
                    value = 'cuddl'
                ),

                interactions.Choice(
                    name = "Pet",
                    value = 'pett'
                ),

                interactions.Choice(
                    name = "Punch",
                    value = 'punch'
                ),

                interactions.Choice(
                    name = "Slap",
                    value = 'slapp'
                ),

                interactions.Choice(
                    name = "Kill",
                    value = "murder"
                ),
            ]
        ),

        interactions.Option(
            name = "user",
            required = True,
            description = 'The person to do the action towards.',
            type=interactions.OptionType.USER
        )
    ]
)
async def action(ctx : interactions.CommandContext, user : str, choices : str):

    if (choices == 'user_command'):
        choice = GetChoices()

        id = uuid.uuid4()

        select = interactions.SelectMenu(
            type = interactions.ComponentType.SELECT,
            options = choice,
            placeholder = "Select an Action!",
            custom_id = str(id)
        )

        await ctx.send(f'What action do you want to do towards {user.name}?', components = select, ephemeral = True)

        contexto : interactions.ComponentContext = await wait_for_component(bot, components = select)

        ctx = contexto
        
        choices = contexto.data.values[0]
    
    verb = f'{choices}ed'

    title_ = await GetTitles(choices)
    
    if (user.id == ctx.author.user.id):
        if (choices == 'murder' or choices == 'slapp' or choices == 'punch'):
            await ctx.send('Hey! Don\'t do that. That ain\'t cool. Love yourself. ♥', ephemeral = True)
            return
        else:
            embed = interactions.Embed(
                title = f'{title_}!',
                description = f'<@{ctx.author.user.id}> {verb} themselves.'
            )   
    else:
        embed = interactions.Embed(
            title = f'{title_}!',
            description = f'<@{ctx.author.user.id}> {verb} <@{user.id}>.'
        )

    button = interactions.Button(
        style = interactions.ButtonStyle.PRIMARY,
        label = await GetTitles(choices) + ' back',
        custom_id = f'sussy {user.id}'
    )

    if (user.id == ctx.author.user.id):
        msg = await ctx.send(embeds = embed)
    else:
        msg = await ctx.send(embeds = embed, components = button)

    async def check(ctx):
        if (ctx.author.id == user.id):
            return True
        else:
            await ctx.send(f'Sorry! Only the user <@{user.id}> can respond to this action!', ephemeral = True)
            return False

    
    
    if (user.id == bot.me.id or user.user.bot):

        button_ctx = ctx
        
        if (choices == 'murder'):
            embed = interactions.Embed(
                title = f'Whoops.',
                description = f'<@{user.id}> could not murder <@{ctx.author.user.id}> back. For they are very much deceased.' 
            )

            await msg.edit(components = [])
        
            await button_ctx.send(embeds=embed)
        else:
    
            embed = interactions.Embed(
                title = f'A {title_} back!',
                description = f'<@{user.id}> {verb} <@{ctx.author.user.id}> back.'
            )
        
            await msg.edit(components = [])
        
            await button_ctx.send(embeds=embed)
    else:
        button_ctx = await wait_for_component(bot, components=button, check=check)
        
        if (choices == 'murder'):
            embed = interactions.Embed(
                title = f'lol',
                description = f'<@{user.id}> could not murder <@{ctx.author.user.id}> back. For they are very much deceased.' 
            )

            await msg.edit(components = [])
        
            await button_ctx.send(embeds=embed)
        else:
    
            embed = interactions.Embed(
                title = f'A {title_} back!',
                description = f'<@{user.id}> {verb} <@{ctx.author.user.id}> back.'
            )
        
            await msg.edit(components = [])
        
            await button_ctx.send(embeds=embed)

def GetChoices():
    return [
            interactions.SelectOption(
                label = "Hug",
                value = 'hugg'
            ),

            interactions.SelectOption(
                label = "Kiss",
                value = 'kiss'
            ),

            interactions.SelectOption(
                label = "Cuddle",
                value = 'cuddl'
            ),

            interactions.SelectOption(
                label = "Pet",
                value = 'pett'
            ),

            interactions.SelectOption(
                label = "Punch",
                value = 'punch'
            ),

            interactions.SelectOption(
                label = "Slap",
                value = 'slapp'
            ),

            interactions.SelectOption(
                label = "Kill",
                value = "murder"
            ),
        ]

async def GetTitles(choice):
    if (choice == 'hugg'):
        return 'Hug'
    if (choice == 'kiss'):
        return 'Kiss'
    if (choice == 'cuddl'):
        return 'Cuddle'
    if (choice == 'pett'):
        return 'Pet'
    if (choice == 'slapp'):
        return 'Slap'
    if (choice == 'punch'):
        return 'Punch'
    if (choice == 'murder'):
        return 'Kill'
        
@bot.command(
    name = 'ask',
    description = 'Ask a question, with the bot responding using OpenAI\'s GPT-3.',
)
async def gen_text(ctx : interactions.CommandContext):
    
    modal = Modal('')
    
    await ctx.popup(modal)

@bot.modal('funny modal')
async def on_modal(ctx, prompt : str):
    msg = await ctx.send('Generating text... <a:loading:1026539890382483576>')

    await stamps.IncrementValue(ctx, 'times_asked', int(ctx.author.id))
    
    result = await generate_text.GenerateText(prompt + '?', ctx.author.user.username)

    newline = '\n'

    embed = interactions.Embed(
        title = 'Result',
        description = f'**{prompt}**' + f'\n\n[ {result[0].strip(newline)} ]'
    )

    await msg.edit('', embeds=embed)

def Modal(starting_prompt : str):
    return interactions.Modal(
            title = 'Enter Prompt',
            description = 'Enter your prompt and the bot will respond. Asking the bot questions about itself might lead to spoilers for the game OneShot.',
            components = [
                interactions.TextInput(
                    style=interactions.TextStyleType.PARAGRAPH,
                    label="Enter your prompt.",
                    custom_id="text_input_response",
                    type = interactions.ComponentType.INPUT_TEXT,
                    placeholder = 'How are you feeling?, What are you up to?'
                )
            ],
            custom_id='funny modal'
        )

@bot.command(
    name = 'get_pfp',
    description = 'Get a Profile Picture of a user in the server.',
    options = [
        interactions.Option(
            name = 'user',
            description = 'The user to get the profile picture from.',
            type = interactions.OptionType.USER,
            required = True
        )
    ]
)
async def wow_beautiful(ctx : interactions.CommandContext, user : interactions.Member):
    embed = interactions.Embed(
        title = f'{user.name}\'s Profile Picture.',
        image = interactions.EmbedImageStruct(url = user.user.avatar_url, width = 300, height = 300)
    )

    await ctx.send(embeds = embed)

@bot.command(
    name = 'send_letter',
    description = 'Send a letter to someone.',
    options = [
        interactions.Option(
            name = 'user',
            description = 'The user to send the letter to.',
            type = interactions.OptionType.USER,
            required = True
        ),

        interactions.Option(
            name = 'message',
            description = 'The message to send.',
            type = interactions.OptionType.STRING,
            required = True
        ),
    ]
)
async def letter(ctx : interactions.CommandContext, user : interactions.Member, message : str):

    ban_list = []
        
    with open('ban_list.txt', 'r') as f:
        ban_list = f.readlines()
        
    if (str(ctx.author.id) in ban_list):
        await ctx.send('Sorry! But you are banned from using this command.', ephemeral = True)
        return
    
    with open ('databases/loveletters.db', 'r') as db:
        lllist = db.read()
        lllist = lllist.split('\n')

    embed = interactions.Embed(
        description = f'{message}',
        footer = interactions.EmbedFooter(text= f'Sent by {ctx.author.user.username} in {ctx.guild.name}', icon_url = ctx.author.user.avatar_url),
        timestamp = datetime.datetime.utcnow(),
        author = interactions.EmbedAuthor(name = '💌 You got a letter!'),
        thumbnail = interactions.EmbedImageStruct(url = await stamps.GetCurrentBadge(int(ctx.author.id), False, 0))
    )

    if (user.id in lllist and ctx.author.id in lllist or ctx.author.id == 302883948424462346):
        await stamps.IncrementValue(ctx, 'letters_sent', int(ctx.author.id))

        if (ctx.author.id == 302883948424462346):
            await stamps.IncrementValue(ctx, 'owner_letter', int(user.id))
        
        await user.send(embeds=embed)
        print('sending letter')
        await ctx.send('Letter sent successfully!', ephemeral=True)
    elif (not user.id in lllist):
        await ctx.send('This user has not opted in for recieving letters. Ask the other person to use /toggle_letters to recieve letters.', ephemeral=True)
    else:
        await ctx.send('In order to send letters, you need to opt in. Use /toggle_letters to recieve and send letters.', ephemeral=True)

@bot.command(
    name = 'toggle_letters',
    description = 'Allows you to recieve letters from anyone.',
)
async def allow(ctx : interactions.CommandContext):
    button = interactions.Button(
        style = interactions.ButtonStyle.PRIMARY,
        label = 'Yes',
        custom_id = str(uuid.uuid4())
    )

    db = open('databases/loveletters.db', 'r+')
    
    f = db.read()
    lllist = f.split('\n')
    
    if (ctx.author.id in lllist):
        lllist.remove(str(ctx.author.id))

        result = '\n'.join(lllist)
        
        db.write(result)

        await ctx.send('You have opted out from recieving (and sending!) letters. If you wish to recieve or send letters again, run this command again', ephemeral=True)
    else:
        await ctx.send('Are you sure you want to recieve (and send) letters?', components=button, ephemeral=True)

        button_ctx = await wait_for_component(bot, components = button)
        
        db.write(f + f'\n{str(ctx.author.id)}')
        await button_ctx.send('You will now recieve letters. To opt out of this, run this command again.', ephemeral=True)
        
    db.close()

@bot.user_command(name="Send Letter")
async def send_letter(ctx : interactions.CommandContext):
    
    ban_list = []
        
    with open('ban_list.txt', 'r') as f:
        ban_list = f.readlines()
        
    if (str(ctx.author.id) in ban_list):
        await ctx.send('Sorry! But you are banned from using this command.', ephemeral = True)
        return
    
    modal_ = interactions.Modal(
        custom_id = 'Mooodal',
        title = 'Send a letter!',
        components = [
            interactions.TextInput(
                style = interactions.TextStyleType.SHORT,
                label = "Send your Letter!",
                custom_id = 'djhsfdjkhhsdfkjh'
            )
        ]
    )

    async def check(ctx):
        return True;
        
    await ctx.popup(modal_)

    modal_ctx : interactions.CommandContext = await wait_for(bot = bot, name = 'on_modal', check=check)

    letter_ = []

    print('lolcat')

    if modal_ctx.data.components:
        for component in modal_ctx.data.components:
            if component.components:
                letter_.append([_value.value for _value in component.components][0]) # Messy solution, but it should work so who cares!

    ctx.target._client = bot._http # Needs HTTP Client to be set for some reason
    
    await letter(modal_ctx, ctx.target, letter_[0])


@bot.user_command(name="Action")
async def action_command_hug(ctx : interactions.CommandContext):
    await action(ctx, ctx.target, 'user_command')

async def stop_killing_people(ctx, amount):
    await ctx.send('Please refrain from murdering entire worlds for 1 minute please!!!', ephemeral = True)

@bot.command(
    name = 'explode',
    description = 'what'
)
@cooldown(minutes=1, type='user', error = stop_killing_people)
async def explosion(ctx):

    await stamps.IncrementValue(ctx, 'suns_shattered', int(ctx.author.id))

    if(random.randint(0, 1000) > 990 or ctx.guild.id == 850069038804631572):
        embed = interactions.Embed(
            title = '???',
            image = interactions.EmbedImageStruct(url = 'https://i.ibb.co/bKG17c2/image.png'),
            footer = interactions.EmbedFooter(
                text = 'You killed Niko.'
            )
        )

        await ctx.send(embeds=embed)
        return
    
    sun = 0
    f = ''
    
    with open('databases/explosions.count', 'r') as db:
        f = db.read()
    
    result = int(f) + 1
    
    with open('databases/explosions.count', 'w') as db:
        db.write(str(result))
    
    sun = f

    img = icons.lightbulbs[random.randint(0, len(icons.lightbulbs) - 1)]
    
    embed = interactions.Embed(
        title = 'oh no you have doomed us ALL',
        image = interactions.EmbedImageStruct(url = img),
        footer = interactions.EmbedFooter(
            text = f'The Sun has been shattered {sun} times!'
        )
    )

    if (sun == '69'):
        embed = interactions.Embed(
            title = 'Nice.',
            image = interactions.EmbedImageStruct(url = img),
            footer = interactions.EmbedFooter(
                text = f'The Sun has been shattered {sun} times!'
            )
        )

    if (sun == '100'):
        embed = interactions.Embed(
            title = 'A little too much.',
            image = interactions.EmbedImageStruct(url = img),
            footer = interactions.EmbedFooter(
                text = f'The Sun has been shattered {sun} times!'
            )
        )

    if (sun == '420'):
        embed = interactions.Embed(
            title = 'Nice. x2',
            image = interactions.EmbedImageStruct(url = img),
            footer = interactions.EmbedFooter(
                text = f'The Sun has been shattered {sun} times!'
            )
        )

    if (sun == '1000'):
        embed = interactions.Embed(
            title = 'Definitely too much.',
            image = interactions.EmbedImageStruct(url = 'https://empire-s3-production.bobvila.com/articles/wp-content/uploads/2018/07/broken-light-bulb.jpg'),
            footer = interactions.EmbedFooter(
                text = f'The Sun has been shattered {sun} times!'
            )
        )

    if (sun == '69420'):
        embed = interactions.Embed(
            title = 'Nice. x3',
            image = interactions.EmbedImageStruct(url = 'https://empire-s3-production.bobvila.com/articles/wp-content/uploads/2018/07/broken-light-bulb.jpg'),
            footer = interactions.EmbedFooter(
                text = f'The Sun has been shattered {sun} times!'
            )
        )

    await ctx.send(embeds=embed)

@bot.command(
    name = 'generate-battles',
    description = 'Generate battles using GPT-3 from OpenAI.',
    options = [
        interactions.Option(
            name = 'bcl_',
            description = 'Battle Contestant List',
            type = interactions.OptionType.ATTACHMENT,
            required = True
        )
    ],
    default_member_permissions=interactions.Permissions.ADMINISTRATOR,
    scope=1017531963000754247
)
async def fight(ctx : interactions.CommandContext, bcl_ : interactions.Attachment):
    
    text_file : io.BytesIO = await bcl_.download()
    
    bcl = text_file.read().decode('utf-8')
    
    await ctx.send('BCL Loaded!', ephemeral=True)
    
    contestants = bcl.split('^')
    
    battles = []
    
    i = 1
    for contestant in contestants:
        if i % 2 == 0:
            battles.append([contestants[i - 2], contestants[i - 1]])
            
        i += 1
        
    for battle in battles:
        
        c_one = battle[0].split('>')
        c_two = battle[1].split('>')

        btl = await ctx.channel.send(f"**A battle begins! {c_one[0]} versus {c_two[0]}!**")
        
        btl1 = await btl.reply('Generating battle... <a:loading:1026539890382483576>')
        
        num = random.randint(0, 1)
        
        winner = None
        
        if num == 0:
            winner = c_one
        else:
            winner = c_two
        
        text = await generate_text.GenerateBattle(c_one[1], c_one[0], c_one[2], c_one[3], c_two[1], c_two[0], c_two[2], c_two[3], winner[0])
        
        embed = interactions.Embed(
            title = f'{c_one[0]} versus {c_two[0]}',
            description = text[0]
        )
        
        result = await btl1.edit(content = '', embeds=embed)
        
        result_embed = interactions.Embed(
            title = f'{winner[0]} is the winner!',
            thumbnail=interactions.EmbedImageStruct(url=winner[4]),
            description='The next battle will begin in 10 seconds!'
        )
        
        await result.reply(embeds=result_embed)
        
        await asyncio.sleep(10)
        
@bot.command(scope=1017531963000754247)
async def generate_bcl(ctx):
    modal = interactions.Modal(
            custom_id='battle',
            title = 'Generate a Battle Contestant',
            components=[
                interactions.TextInput(
                    style = interactions.TextStyleType.SHORT,
                    custom_id='name',
                    label='Name',
                    placeholder='What is their name?',
                    required=True
                ),
                interactions.TextInput(
                    style = interactions.TextStyleType.SHORT,
                    custom_id='gender',
                    label='Gender',
                    placeholder='Examples include Male / Female or any other gender.',
                    required=True
                ),
                interactions.TextInput(
                    style = interactions.TextStyleType.SHORT,
                    custom_id='weapon',
                    label='Weapon',
                    placeholder='What weapon do they wield?',
                    required=True
                ),
                interactions.TextInput(
                    style = interactions.TextStyleType.PARAGRAPH,
                    custom_id='description',
                    label='Personality',
                    placeholder='Write a short description of your fighter\'s personality.',
                    required=True
                ),
                interactions.TextInput(
                    style = interactions.TextStyleType.SHORT,
                    custom_id='url',
                    label='Image URL',
                    placeholder='https://image/my_image.png',
                    required=True
                )
            ]
        )
        
    await ctx.popup(modal)    
@bot.modal('battle')
async def on_modal(ctx, name, gender, weapon, personality, image_url):
    
    if validators.url(image_url):
        await ctx.send(f'{name}>{gender}>{weapon}>{personality}>{image_url}')
        return
    
    await ctx.send('You need to put in a valid image url!', ephemeral = True)
    
      

@bot.command(
    name = 'select_stamp',
    description = 'Select a stamp to put on your letters.'
)
async def djhsdf(ctx):
    stamps_ = await stamp_list.OpenStampMenu(int(ctx.author.id))

    select = interactions.SelectMenu(
        options = stamps_,
        placeholder = 'Default Stamp',
        custom_id = 'selectmenuuusfkhjfsdkhjfsdhj'
    )

    await ctx.send('Select a badge you have unlocked.', components = select, ephemeral = True)

    async def check(ctx):
        return True
    
    select_ctx = await wait_for_component(bot=bot, components=select, check=check)

    await stamps.GetCurrentBadge(int(ctx.author.id), True, select_ctx.data.values[0])

    await select_ctx.send(f'Stamp change successful!', ephemeral = True)

@bot.command(
    name = 'assign-stamp',
    description = 'Allows you to assign a stamp. Can only be used by the owner.',
    options = [
        interactions.Option(
            name = 'user',
            description = 'The user to assign the stamp to.',
            required = True,
            type = interactions.OptionType.USER
        ),

        interactions.Option(
            name = 'stamp_id',
            description = 'The ID of the stamp to assign.',
            required = True,
            type = interactions.OptionType.NUMBER
        )
    ]
)
async def assign_stamp(ctx : interactions.CommandContext, user : interactions.Member, stamp_id):
    if (ctx.author.id == 302883948424462346):
        await stamps.GetCurrentBadge(int(user.id), True, None, True, stamp_id)

        badges = stamp_list.stamps

        name = ''
        id_ = ''

        for badge in badges:
            if (stamp_id == badge['stamp_id']):
                name = badge['name']
                id_ = f'https://cdn.discordapp.com/emojis/{str(badge["stamp_url"])}.png'
        
        await ctx.send('Assigned Stamp to ' + user.user.username)
        await stamps.EarnBadge(ctx, name, id_, 'You recieved this stamp from the owner of the bot, congrats!', int(user.id))
    else:
        await ctx.send('Sorry, you cannot use this command!', ephemeral=True)

@bot.command(
    name = 'view_stamps',
    description = 'Show off those stylish stamps!',
    options = [interactions.Option(name = 'user', description = 'Select someone to view their stamps.', type = interactions.OptionType.USER)]
)
async def view_stamp(ctx : interactions.CommandContext, user = 'none'):

    id_ = 0

    msg = ''

    user_ = ''

    if (user == 'none'):
        id_ = int(ctx.author.id)
        msg = 'Loading your beautiful stamps... <a:loading:1026539890382483576>'
        user_ = ctx.author.user.username
    else:
        id_ = int(user.id)
        msg = f'Loading {user.user.username}\'s beautiful stamps... <a:loading:1026539890382483576>'
        user_ = user.user.username
    
    msg = await ctx.send(msg)

    print(user_)
    
    await view.DrawBadges(id_, user_)

    img_ = interactions.File('Badges/result.png')

    await msg.edit('', files = img_)

@bot.command(
    name = 'blacklist-server-messages',
    description = 'Blacklist this server from getting message-based stamp achievements.',
    default_member_permissions=interactions.Permissions.ADMINISTRATOR,
)
async def blacklist__(ctx):
    with open('databases/message_blacklist.db', 'r+') as db:
        f = db.read()
        blacklist = f.split('\n')
        blacklist.append(str(ctx.guild_id))

        db.write('\n'.join(blacklist))

    await ctx.send('This server has been added to the blacklist.', ephemeral = True)
    
@bot.event
async def on_message_create(message: interactions.Message):
    blacklist = []
    
    with open('databases/message_blacklist.db', 'r') as db:
        f = db.read()
        blacklist = f.split('\n')

    if (message.guild_id in blacklist): # If a server owner has blocked message achievements then do nothing.
        return
    
    if not message.author.bot:
        content = message.content
    
        content = cleantext.replace_urls(content, '`< URL >`')
        
        await stamps.IncrementValue(message, "times_messaged", int(message.author.id)) # Increment the times messaged by 1.

        with open('Transmissions/connected.userphone', 'r') as f:
            channel_ids = f.read().split('>')
            
            for channel_id in channel_ids:
                channel_id = json.loads(channel_id)
                if (int(channel_id['connection_one']) == int(message.channel_id)):
                    webhook = None
                    data = await generate_userphone_embed(channel_id['hidden'], message)
                        
                    channel = await interactions.get(bot, interactions.Channel, object_id=int(channel_id['connection_two']))
                    
                    await bot._http.trigger_typing(channel_id=int(channel_id['connection_two']))
                    
                    webhook : interactions.Webhook = await interactions.Webhook.create(bot._http, channel.id, data[0], data[1])
                    
                    if len(message.attachments) > 0:
                        
                        files = []
                        for a in message.attachments:
                            a._client = bot._http
                            files.append(interactions.File(a.filename, await a.download()))
                        
                        await webhook.execute(message.content, files=files)
                    else:
                        await webhook.execute(message.content)
                    await webhook.delete()
                    break
                elif (int(channel_id['connection_two']) == int(message.channel_id)):                  
                    webhook = None
                    data = await generate_userphone_embed(channel_id['hidden'], message)
                        
                    channel = await interactions.get(bot, interactions.Channel, object_id=int(channel_id['connection_one']))
                    
                    await bot._http.trigger_typing(channel_id=int(channel_id['connection_one']))
                    
                    webhook : interactions.Webhook = await interactions.Webhook.create(bot._http, channel.id, data[0], data[1])
                    
                    if len(message.attachments) > 0:
                        files = []
                        for a in message.attachments:
                            a._client = bot._http
                            files.append(interactions.File(a.filename, await a.download()))
                        
                        await webhook.execute(message.content, files=files)
                    else:
                        await webhook.execute(message.content)
                    await webhook.delete()
                    break

async def generate_userphone_embed(hidden : bool, message):
    if hidden:
        user_ = await interactions.get(bot, interactions.User, object_id = 744248932263133234)
        
        picture = user_.avatar_url
        
        username = user_.username + f'#{str(message.author.id)[2 : 6]}'
                    
        async with aiohttp.ClientSession() as session:
            url = picture
            async with session.get(url) as resp:
                if resp.status == 200:
                    f = await aiofiles.open('Images/transmitpfp.png', mode='wb')
                    await f.write(await resp.read())
                    await f.close()
                    
        picture = interactions.Image('Images/transmitpfp.png')
                    
        return [username, picture]
    else:
        picture = message.author.avatar_url
                    
        async with aiohttp.ClientSession() as session:
            url = picture
            async with session.get(url) as resp:
                if resp.status == 200:
                    f = await aiofiles.open('Images/transmitpfp.png', mode='wb')
                    await f.write(await resp.read())
                    await f.close()
                    
        fpicture = interactions.Image('Images/transmitpfp.png')
        
        return [message.author.username, fpicture]

@bot.command()
async def restart_bot(ctx):
    if (ctx.author.id == 302883948424462346 or ctx.author.id == 400054986530357268):
        await ctx.send('Restarting Now!')
        
        API_KEY = 'Bearer ' + os.getenv('SPARKED')
        
        header = {"Authorization" : API_KEY}
        r = requests.post('https://control.sparkedhost.us/api/client/servers/92aeea52/power', json={"signal": "restart"}, headers=header)
        print(r.status_code)
        return
    
    await ctx.send('You cannot use this command.', ephemeral = True)


bot.start()