import interactions
import os
import random
import lavalink
import uuid
import aiohttp        
import aiofiles
from replit import db
import json

# Other Scripts
import custom_source
import dialogue_generator
import profile_icons as icons
import generate_text
import music_utilities as music
import stamp_system as stamps

# Extension Libraries
from interactions.ext.wait_for import wait_for_component, setup, wait_for
from interactions.ext.lavalink import VoiceClient
from interactions.ext.files import command_send
from interactions.ext.enhanced import cooldown

TOKEN = os.environ['BOT-TOKEN']

try:
    bot = VoiceClient(token=TOKEN)
except:
    print('Restarting.')
    os.system('kill 1') # Prevents the bot from continously getting stuck on the same server.
    
bot.load('interactions.ext.files')

setup(bot)

responses = []

@bot.event()
async def on_start():
    global responses

    random.shuffle(responses)

    bot.lavalink_client.add_node(
        host = '51.161.130.134',
        port = 10333,
        password = 'youshallnotpass',
        region = "eu"
    ) # Woah, neat! Free Lavalink!
    
    bot.lavalink_client.add_event_hook(music.track_hook)

    await bot.change_presence(
        interactions.ClientPresence(
            status=interactions.StatusType.ONLINE,
            activities=[
                interactions.PresenceActivity(
                    name="over Niko",
                    type=interactions.PresenceActivityType.WATCHING)
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
    print(val_char)

    if (val_char == 0):
        text_ = await icons.GenerateModalNiko()
        
    elif (val_char == 1):
        print('lol')
        text_ = await icons.GenerateModalTWM()
        
    elif (val_char == 2):
        text_ = await icons.GenerateModalNiko()

    print(text_)

    await char_ctx.send(f"<@{ctx.author.id}>, select a text face!", components=text_[0], ephemeral=True)
    
    text_ctx : interactions.ComponentContext = await wait_for_component(bot, components=text_[0], check=check)
    
    val = int(text_ctx.data.values[0])

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

    msg = await text_ctx.send("Generating Image... <a:nikooneshot:1024961281628848169>")
    await dialogue_generator.test(text)
    await msg.delete()
    file = interactions.File(filename="Images/pil_text.png")
    await command_send(text_ctx, content=f"Generated by: {ctx.author.name}", files=file)



@bot.command(
    name="music",
    options=[
        interactions.Option(
            name="play",
            description="Add Music to the music queue to be played.",
            type=interactions.OptionType.SUB_COMMAND,
            options=[                
                interactions.Option(
                    name="search",
                    description=
                    "Search for the track you are looking for.",
                    required=True,
                    type=interactions.OptionType.STRING
                )
            ]
        ),

        interactions.Option(
            name = "get_player",
            description = "See what is playing now.",
            type = interactions.OptionType.SUB_COMMAND
        )
    ])   
async def music_(ctx: interactions.CommandContext, sub_command: str, search: str = "", fromindex: int = 0):
    if (not ctx.author.voice.joined):
        await ctx.send("Sorry! You need to be in a voice channel to use this command.", ephemeral = True)
        return

    if (ctx.author.voice.guild_id != ctx.guild_id):
        await ctx.send("Sorry! You need to be in a voice channel to use this command.", ephemeral = True)
        return
    
    await ctx.defer()
    if (sub_command == "play"):
        player = await bot.connect(ctx.guild_id, ctx.author.voice.channel_id, self_deaf = True)

        player.store(f'channel {ctx.guild_id}', ctx)

        if (search.startswith("https://open.spotify.com/")):
            search = await custom_source.SearchSpotify(search)

        if ('playlist' in search or 'list=PL' in search):
            playlist = await custom_source.GetPlaylist(search)

            msg = await ctx.send(f'Adding **{len(playlist)}** songs to the queue. This might take a while.')

            print(playlist)

            successful = 0
            
            for video in playlist:
                #try:
                results = await player.node.get_tracks(video)
                track = lavalink.AudioTrack(results["tracks"][0], int(ctx.author.id))
                player.add(requester=int(ctx.author.id), track=track)
                successful += 1
                if (successful % 10 == 0):
                    await msg.edit(f'Adding **{len(playlist)}** songs to the queue. This might take a while. ({successful}/{len(playlist)})')
               #@ except:
                    #pass
            
            await msg.edit(f'Added **{successful}** songs to the queue successfully!')
            
            if not player.is_playing:
                await player.play()

            return
        else:
            results = await player.node.get_tracks(f"ytsearch:{search}")
            track = lavalink.AudioTrack(results["tracks"][0], int(ctx.author.id))
            player.add(requester=int(ctx.author.id), track=track)
        

        if not player.is_playing:
            await player.play()
        else:
            cool = interactions.Embed(
                title = f"**Added:** [{track.title}] to queue.",
                thumbnail = interactions.EmbedImageStruct( url = f"https://i3.ytimg.com/vi/{track.identifier}/maxresdefault.jpg", height = 720, width = 1280),
                description = f"Current Position: {len(player.queue)}",
                url = player.queue[len(player.queue) - 1].uri
            )
            await ctx.send(embeds = cool)    
    elif (sub_command == "get_player"):
        player = await bot.connect(ctx.guild_id, ctx.channel_id)

        await music.ShowPlayer(ctx, player, True)

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
    msg = await ctx.send('Generating text... <a:nikooneshot:1024961281628848169>')
    
    result = await generate_text.GenerateText(prompt)

    embed = interactions.Embed(
        title = 'Result',
        description = prompt + result[0]
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
    
    lllist = db['loveletters'].split('\n')

    embed = interactions.Embed(
        title = 'You got a letter!',
        description = f'{message}\n\nFrom: **{ctx.author.user.username}**\nIn: **{ctx.guild.name}**',
        footer = interactions.EmbedFooter(text= f'If you wish to send a letter, do /send_letter!'),
        thumbnail = interactions.EmbedImageStruct(url = 'https://www.freepnglogos.com/uploads/letter-png/letter-png-transparent-letter-images-pluspng-17.png')
    )

    if (user.id in lllist and ctx.author.id in lllist):
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
        custom_id = str(ctx.author.id)
    )

    lllist = db['loveletters'].split('\n')
    
    if (ctx.author.id in lllist):
        lllist.remove(str(ctx.author.id))

        result = '\n'.join(lllist)

        db['loveletters']  = result

        await ctx.send('You have opted out from recieving (and sending!) letters. If you wish to recieve or send letters again, run this command again', ephemeral=True)
    else:
        await ctx.send('Are you sure you want to recieve (and send) letters?', components=button, ephemeral=True)

        button_ctx = await wait_for_component(bot, components = button)
    
        db['loveletters'] = db['loveletters'] + f'\n{str(ctx.author.id)}'
        await button_ctx.send('You will now recieve letters. To opt out of this, run this command again.', ephemeral=True)

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

    if(random.randint(0, 1000) > 950 or ctx.guild.id == 850069038804631572):
        embed = interactions.Embed(
            title = '???',
            image = interactions.EmbedImageStruct(url = 'https://i.ibb.co/bKG17c2/image.png'),
            footer = interactions.EmbedFooter(
                text = 'You killed Niko.'
            )
        )

        await ctx.send(embeds=embed)
        return

    db['sun'] = str(int(db['sun']) + 1)

    sun = db['sun']

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
            name = 'fighter_one_weapon',
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
            name = 'fighter_two_weapon',
            description = 'The second Fighter\'s weapon or tool.',
            type = interactions.OptionType.STRING,
            required = True
        )
    ]
)
async def fight(ctx : interactions.CommandContext, fighter_one, fighter_one_weapon, fighter_two, fighter_two_weapon):
    msg = await ctx.send('Generating text... <a:nikooneshot:1024961281628848169>')
    
    battle = await generate_text.GenerateBattle(fighter_one, fighter_one_weapon, fighter_two, fighter_two_weapon)

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

@bot.event
async def on_message_create(message: interactions.Message):
    blacklist = ['lol']  #db['achievementblacklist'].split('\n')

    if (message.guild_id in blacklist): # If a server owner has blocked message achievements then do nothing lol
        return
    
    if (message.guild_id == 1017479547664482444):
        db = ''
        
        with open('user_database.txt', 'r') as f:
            db = f.read()
        
        database = db.split('\n')

        print(database)

        id = message.member.id

        for data_ in database:

            print('data', data_)
            try:
                data_ = json.loads(data_)
                if (data_['user_id'] == id):
                    data_['times_messaged'] = data_['times_messaged'] + 1
                    return
            except:
                pass
                
            database.append(json.dumps({
                'user_id' : id,
                'times_messaged' : 1,
                'suns_shattered' : 0,
                'times_asked' : 0,
                'letters_sent' : 0
            }) + '\n')
            
        for data_ in database:
            with open('user_database.txt', 'rw') as f:
                f.write(f.read() + f'{data_}\n')

        print('message has been sent')

bot.start()