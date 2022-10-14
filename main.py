import interactions
import os
import random
import uuid
import aiohttp        
import aiofiles
import json
import datetime
from dotenv import load_dotenv
load_dotenv()

# Other Scripts
import custom_source
import dialogue_generator
import profile_icons as icons
import generate_text
import music_utilities as music
import Badges.stamp_system as stamps
import Badges.stamp_list as stamp_list
import Badges.stamp_viewer as view

# Extension Libraries
from interactions.ext.wait_for import wait_for_component, setup, wait_for
from interactions.ext.lavalink import VoiceClient
import interactions.ext.files
from interactions.ext.enhanced import cooldown
import exts.music


TOKEN = os.getenv('BOT-TOKEN')

bot = VoiceClient(token=TOKEN, intents=interactions.Intents.DEFAULT)
    
bot.load('interactions.ext.files')
bot.load('exts.music') # AttributeError: module 'exts.music' has no attribute 'setup'

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
                    name="Testing, nearly finished!",
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
        await bot.modify(avatar=image, username="The World Machine")
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
    if '@everyone' in text:
        text = text.replace('@everyone', '@‎everyone')

    if '@here' in text:
        text = text.replace('@here', '@‎here')
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

    print(user.id)
    
    with open ('databases/loveletters.db', 'r') as db:
        lllist = db.read.split('\n')

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
    
    lllist = db.read.split('\n')
    
    if (ctx.author.id in lllist):
        lllist.remove(str(ctx.author.id))

        result = '\n'.join(lllist)
        
        db.write(result)

        await ctx.send('You have opted out from recieving (and sending!) letters. If you wish to recieve or send letters again, run this command again', ephemeral=True)
    else:
        await ctx.send('Are you sure you want to recieve (and send) letters?', components=button, ephemeral=True)

        button_ctx = await wait_for_component(bot, components = button)
        
        db.write(db.read() + f'\n{str(ctx.author.id)}')
        await button_ctx.send('You will now recieve letters. To opt out of this, run this command again.', ephemeral=True)
        
    db.close()

@bot.user_command(name="Send Letter")
async def send_letter(ctx : interactions.CommandContext):
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
    
    with open('explosions.count', 'r+') as db:
        db.write(str(int(db.read()) + 1))

        sun = db.read()

    img = icons.lightbulbs[random.randint(0, len(icons.lightbulbs) - 1)]
    
    embed = interactions.Embed(
        title = 'oh no you have doomed us ALL',
        image = interactions.EmbedImageStruct(url = img),
        footer = interactions.EmbedFooter(
            text = f'The Sun has been shattered {sun} times!'
        )
    )

    if (db['sun'] == '69'):
        embed = interactions.Embed(
            title = 'Nice.',
            image = interactions.EmbedImageStruct(url = img),
            footer = interactions.EmbedFooter(
                text = f'The Sun has been shattered {sun} times!'
            )
        )

    if (db['sun'] == '100'):
        embed = interactions.Embed(
            title = 'A little too much.',
            image = interactions.EmbedImageStruct(url = img),
            footer = interactions.EmbedFooter(
                text = f'The Sun has been shattered {sun} times!'
            )
        )

    if (db['sun'] == '420'):
        embed = interactions.Embed(
            title = 'Nice. x2',
            image = interactions.EmbedImageStruct(url = img),
            footer = interactions.EmbedFooter(
                text = f'The Sun has been shattered {sun} times!'
            )
        )

    if (db['sun'] == '1000'):
        embed = interactions.Embed(
            title = 'Definitely too much.',
            image = interactions.EmbedImageStruct(url = 'https://empire-s3-production.bobvila.com/articles/wp-content/uploads/2018/07/broken-light-bulb.jpg'),
            footer = interactions.EmbedFooter(
                text = f'The Sun has been shattered {sun} times!'
            )
        )

    if (db['sun'] == '69420'):
        embed = interactions.Embed(
            title = 'Nice. x3',
            image = interactions.EmbedImageStruct(url = 'https://empire-s3-production.bobvila.com/articles/wp-content/uploads/2018/07/broken-light-bulb.jpg'),
            footer = interactions.EmbedFooter(
                text = f'The Sun has been shattered {sun} times!'
            )
        )

    await ctx.send(embeds=embed)

@bot.command(
    name = 'generate-battle',
    description = 'Generate a battle using GPT-3 from OpenAI.',
    options = [
        interactions.Option(
            name = 'fighter_one',
            description = 'The first Fighter.',
            type = interactions.OptionType.STRING,
            required = True
        ),

        interactions.Option(
            name = 'wielding_an',
            description = 'The first Fighter\'s weapon or tool.',
            type = interactions.OptionType.STRING,
            required = True
        ),

        interactions.Option(
            name = 'fighter_two',
            description = 'The second Fighter.',
            type = interactions.OptionType.STRING,
            required = True
        ),

        interactions.Option(
            name = 'wielding_a',
            description = 'The second Fighter\'s weapon or tool.',
            type = interactions.OptionType.STRING,
            required = True
        )
    ]
)
async def fight(ctx : interactions.CommandContext, fighter_one, wielding_an, fighter_two, wielding_a):
    msg = await ctx.send('Generating text... <a:loading:1026539890382483576>')
    
    battle = await generate_text.GenerateBattle(fighter_one, wielding_an, fighter_two, wielding_a)

    print(len(battle))

    if (len(battle) < 2):
        embed = interactions.Embed(
            title = 'Result',
            description = battle[0]
        )

        await msg.edit('',embeds=embed)
    else:
        for btl in battle:
            embed = interactions.Embed(
                title = 'Result',
                description = btl
            )

        await msg.send('',embeds=embed)

            

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
        await stamps.EarnBadge(ctx, stamp_id, name, id_, 'You recieved this stamp from the owner of the bot, congrats!', int(ctx.user.id))
    else:
        await ctx.send('Sorry, you cannot use this command!', ephemeral=True)

@bot.event
async def on_command_error(ctx, error):
    await ctx.send(f'Whoops. An error occurred. Please report to Axiinyaa#3813```diff\n- {error} -```')

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
    with open('message_blacklist.db', 'r+') as db:
        blacklist = db.read().split('\n')
        blacklist.append(str(ctx.guild_id))

        db.write('\n'.join(blacklist))

    await ctx.send('This server has been added to the blacklist.', ephemeral = True)
    
@bot.event
async def on_message_create(message: interactions.Message):
    blacklist = []
    
    with open('message_blacklist', 'r') as f:
        blacklist = f.read().split('\n')

    if (message.guild_id in blacklist): # If a server owner has blocked message achievements then do nothing.
        return
        
    await stamps.IncrementValue(message, "times_messaged", int(message.author.id)) # Increment the times messaged by 1.

    '''f = open('userphone.json')
    connection_data = json.load(f)
    f.close()
    
    for cc in connection_data['connections']:
        if (cc['guild_id'] == message.guild_id):
            await UpdateMessage(message, message.guild_id)'''

bot.start()