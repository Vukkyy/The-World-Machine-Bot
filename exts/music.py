from interactions import *
import lavalink
from interactions.ext.lavalink import Lavalink
import custom_source
import lyricsgenius
import os
import random
import music_utilities as music_
import datetime
import uuid
from interactions.ext.database import Database

import interactions

default_songs = [
    "https://youtu.be/TqMo9HwiNOo",
    'https://youtu.be/eCq2HMFC_lU',
    "https://youtu.be/2M0mruW4WCs",
    "https://youtu.be/qJtrbm57-n4",
    "https://youtu.be/fSbYgB5tgkA",
    "https://youtu.be/EdCHU5IMy7E",
    "https://youtu.be/GXNhbkwUD9E"
]

genius = lyricsgenius.Genius(os.getenv('GENIUS'))

class Music(Extension):
    
    def __init__(self, client):
        self.client = client
        self.lavalink: Lavalink = None

    @extension_listener()
    async def on_track_start(self, event: lavalink.TrackStartEvent):
        
        is_quiet = event.player.fetch(f'isquiet {event.player.guild_id}')
        
        if (not is_quiet):
            event.player.set_repeat(False)
            
            ctx = event.player.fetch(f'channel {event.player.guild_id}')

            event.player.store(f'currently quiet {event.player.guild_id}', False)

            index = 0
            
            funny_track = await event.player.node.get_tracks(default_songs[0])
            
            if funny_track in event.player.queue:
                event.player.queue = []
                          
            await music_.ShowPlayer(ctx, event.player, False)

    @extension_listener()
    async def on_start(self):
        print('Loading Music Module')
        
        self.lavalink: Lavalink = Lavalink(self.client)
        
        self.lavalink.add_node(
            host = '162.248.100.61',
            port = 10333,
            password = 'youshallnotpass',
            region = "us"
        )
        
        await Database.create_database('Music', Database.DatabaseType.GUILD, {'is_paused' : False, 'music_stopped' : False, 'stop_votes' : 0, 'skip_votes' : 0})
        
    @extension_listener()
    async def on_queue_end(self, event: lavalink.QueueEndEvent):
        ctx = event.player.fetch(f'channel {event.player.guild_id}')
        embed = Embed(
            title = 'End of Queue',
            description = 'Add more songs using /music play.',
            footer = EmbedFooter(text = 'Playing some quiet OneShot music in the meantime :)')
        )
        await ctx.channel.send("", embeds= embed)

        random.shuffle(default_songs)
        
        results = await event.player.node.get_tracks(default_songs[0])
        track = lavalink.AudioTrack(results["tracks"][0], int(ctx.author.id))

        event.player.set_repeat(True)

        event.player.store(f'isquiet {event.player.guild_id}', True)
        event.player.store(f'currently quiet {ctx.guild_id}', True)
        await event.player.play(track, volume = 8)
        
        

    @extension_listener()
    async def on_voice_state_update(self, before, after):
        """
        Disconnect if bot is alone
        """
        if before and not after.joined:
            voice_states = self.client.get_channel_voice_states(before.channel_id)
            if len(voice_states) == 1 and voice_states[0].user_id == self.client.me.id:
                await self.client.disconnect(before.guild_id)

    @extension_command(
        name="music",
        options=[
            Option(
                name="play",
                description="Add Music to the music queue to be played.",
                type=OptionType.SUB_COMMAND,
                options=[                
                    Option(
                        name="search",
                        description=
                        "Search for the track you are looking for.",
                        required=True,
                        type=OptionType.STRING
                    )
                ]
            ),
    
            Option(
                name = "get_player",
                description = "See what is playing now.",
                type = OptionType.SUB_COMMAND
            ),
            Option(
                name = "stop",
                description = "Stop the music player.",
                type = OptionType.SUB_COMMAND
            ),
        ]
    )   
    async def music_(self, ctx: CommandContext, sub_command: str, search: str = "", fromindex: int = 0):

        voice : VoiceState = ctx.author.voice_state
        
        if (not voice or not voice.joined):
            await ctx.send("Sorry! You need to be in a voice channel to use this command.", ephemeral = True)
            return
    
        if (voice.guild_id != ctx.guild_id):
            await ctx.send("Sorry! You need to be in a voice channel to use this command.", ephemeral = True)
            return
        
        #await ctx.defer()

        player = await self.lavalink.connect(voice.guild_id, voice.channel_id)
        
        if (sub_command == "play"):
            player.store(f'channel {ctx.guild_id}', ctx)
    
            if (search.startswith("https://open.spotify.com/")):
                search = await custom_source.SearchSpotify(search)
    
            if ('playlist' in search or 'list=PL' in search):
                playlist = await custom_source.GetPlaylist(search)
    
                msg_ = await ctx.send(f'Adding **{len(playlist)}** songs to the queue. This might take a while. <a:loading:1026539890382483576>')
    
                print(playlist)
    
                successful = 0
                
                for video in playlist:
                    try:
                        search = await custom_source.SearchSpotify(video, False)
                        tracks = await player.search_youtube(search)
                        track = tracks[0]
                        player.add(requester=int(ctx.author.id), track=track)

                        successful += 1
                    except:
                        pass
                    if (successful % 10 == 0):
                        await msg_.edit(f'Adding **{len(playlist)}** songs to the queue. This might take a while. ({successful}/{len(playlist)}) <a:loading:1026539890382483576>')
                   #@ except:
                        #pass
                
                await msg_.edit(f'Added **{successful}** songs to the queue successfully!')
            else:
                tracks = await player.search_youtube(search)

                if (len(tracks) < 1):
                    await ctx.send("Sorry! Couldn't find a song with that search query.")
                    return
                
                track = tracks[0]
                player.add(requester=int(ctx.author.id), track=track)

    
            player.store(f'isquiet {ctx.guild_id}', False)

            is_quiet = player.fetch(f'currently quiet {ctx.guild_id}')
        
            if not player.is_playing or is_quiet:
                await player.play(volume = 10)
                return
            else:
                
                spotify = await custom_source.SearchSpotify(track.title, False)
                
                cool = Embed(
                    title = f"**Added:** {spotify['name']} to queue.",
                    thumbnail = EmbedImageStruct( url = spotify['art'], height = 720, width = 1280),
                    description = f"Current Position: {len(player.queue)}",
                    url = player.queue[len(player.queue) - 1].uri
                )
                
                await ctx.send(embeds = cool)    
                return
        elif (sub_command == "get_player"):
            player.store(f'channel {ctx.guild_id}', ctx)
            await music_.ShowPlayer(ctx, player, True)
            
        elif (sub_command == "stop"):
            await self.client.disconnect(ctx.guild_id)
            await ctx.send('<:nikosleepy:1027492467337080872> `Successfully stopped the player.`', embeds=[], components =[], ephemeral=True)
            
async def GetButtons(guild_id):
    play_emoji = interactions.Emoji(name="playorpause", id=1019286927888883802)
    stop_emoji = interactions.Emoji(name="stopmusic", id=1019286931504386168)
    queue_emoji = interactions.Emoji(name="openqueue", id = 1019286929059086418)
    loop_song_emoji = interactions.Emoji(name="loopsong", id=1042887337526444123)
    skip_emoji = interactions.Emoji(name="skipmusic", id=1019286930296410133)

    print(guild_id)
    
    return [
        # Queue Button
        interactions.Button(
            style=interactions.ButtonStyle.DANGER,
            emoji = queue_emoji,
            custom_id = f"queue {guild_id}",
        ),
        # Loop Button
        interactions.Button(
            style=interactions.ButtonStyle.DANGER,
            custom_id = f"loop {guild_id}",
            emoji = loop_song_emoji,
        ),

        # Play Button
        interactions.Button(
            style=interactions.ButtonStyle.DANGER,
            custom_id = f"play {guild_id}",
            emoji = play_emoji,
        ),
        # Skip Button
        interactions.Button(
            style=interactions.ButtonStyle.DANGER,
            custom_id = f"skip {guild_id}",
            emoji = skip_emoji
        ),
        # Stop Button
        interactions.Button(
            style=interactions.ButtonStyle.DANGER,
            custom_id = f"stop {guild_id}",
            emoji = stop_emoji
        ),
    ]

async def GenerateEmbed(id : str, player, show_timeline, show_lyrics = False, lyrics = ''):
    
    spotify = await custom_source.SearchSpotify(player.current.title, False)
    
    if (player.is_playing):
        current_length = player.position / 1000
        song_length = player.current.duration / 1000
    
        l_length = list("█░░░░░░░░░░░░░░░░░░░░")
        
        calc_length = round((current_length / song_length) * len(l_length))
    
        i = 0
    
        new_c_length = datetime.datetime.fromtimestamp(current_length).strftime('%M:%S')
        new_length = datetime.datetime.fromtimestamp(song_length).strftime('%M:%S')
        
        for char in l_length:
            if (i < calc_length):
                l_length[i] = "█"
            i += 1
        
        length = "".join(l_length)
        
        if show_lyrics:
            return interactions.Embed(
                title = f"Now Playing: ***{spotify['name']}***",
                thumbnail = interactions.EmbedImageStruct( url = spotify['art'], height = 720, width = 1280),
                description = f"**Lyrics:** {lyrics}",
                footer = interactions.EmbedFooter( text = 'Do /music get_player if the buttons don\'t work or if you\'ve lost the player.'),
            )
    
        if (show_timeline):
            return interactions.Embed(
                title = f"Now Playing: ***{spotify['name']}***",
                thumbnail = interactions.EmbedImageStruct( url = spotify['art'], height = 720, width = 1280),
                description = f"{length} \n\n *{new_c_length} / {new_length}*",
                footer = interactions.EmbedFooter( text = 'Do /music get_player if the buttons don\'t work or if you\'ve lost the player.'),
            )
        else:
            return interactions.Embed(
                title = f"Now Playing: ***{spotify['name']}***",
                thumbnail = interactions.EmbedImageStruct( url = spotify['art'], height = 720, width = 1280),
                description = f"Loading Player... <a:loading:1026539890382483576> \n\n *00:00 / {new_length}*",
                footer = interactions.EmbedFooter( text = 'Do /music get_player if the buttons don\'t work or if you\'ve lost the player.'),
            )

async def GenerateQueue(page_number, player, controls = False, forward = False):
    
    spotify = await custom_source.SearchSpotify(player.current.title, False)
    
    full_queue = player.queue
    list_ = ""

    items_pi = 10

    starting_index = (items_pi * (page_number + 1)) - items_pi
    queue = full_queue[starting_index : starting_index + items_pi] # From 0 to 20

    if controls:
        if len(queue) == 0:
            if forward:
                page_number -= 1
                q = await GenerateQueue(page_number, player)
                return q
            else:
                page_number += 1
                q = await GenerateQueue(page_number, player)
                return q
    
    try:
        for song in queue:
            spotify_ = await custom_source.SearchSpotify(song.title, False)
            time = datetime.datetime.fromtimestamp(song.duration / 1000).strftime('%M:%S')
            list_ = f"{list_}**{full_queue.index(song) + 1}.** `{spotify_['title']}` *({time})*\n"
    except:
        pass
    
    if (len(list_) > 0):
        return interactions.Embed(
            title = "Music Queue",
            description = f"\n**Currently Playing:** `{spotify['name']}`\n\n",
            thumbnail = interactions.EmbedImageStruct( url = "https://shortcut-test2.s3.amazonaws.com/uploads/role/attachment/346765/default_Enlarged_sunicon.png" ),
            fields = [
                interactions.EmbedField(
                    name = "Song List",
                    value = list_,
                    inline = True
                    )
                ],
            
            author = interactions.EmbedAuthor(text=f'Page ({page_number + 1} / {round(len(full_queue) / 10)})')
        )
    else:
        return interactions.Embed(
        title = "Music Queue",
        description = f"\n**Currently Playing:** `{player.current.title}`\n\n",
        thumbnail = interactions.EmbedImageStruct( url = "https://shortcut-test2.s3.amazonaws.com/uploads/role/attachment/346765/default_Enlarged_sunicon.png" ),
        fields = [
            interactions.EmbedField(
                name = "Song List",
                value = 'Queue is empty!',
                inline = True
                )
            ]
        )


async def ShowPlayer(ctx : interactions.CommandContext, player : lavalink.DefaultPlayer, show_timeline : bool, updating : bool = False):
    if updating:
        return
    
    message = ""
    
    player_id = uuid.uuid4()
    
    button_id = uuid.uuid4()
    
    default_data = {'uid' : int(ctx.guild_id), 'player_id' : str(player_id)}
    await db_manager.GetDatabase(int(ctx.guild_id), 'current_players', default_data)   
    db = await db_manager.SetDatabase(int(ctx.guild_id), 'current_players', 'player_id', str(player_id))

    msg = await ctx.send('Loading Player... <a:loading:1026539890382483576>')
    niko = '<a:vibe:1027325436360929300>'
    
    if (player.is_playing):
        embed = await GenerateEmbed(player.current.identifier, player, show_timeline)
        buttons = await GetButtons(button_id)
        msg = await msg.edit(niko, embeds=embed, components=buttons)
    else:
        embed = interactions.Embed(
                title = "Not Currently Playing Anything",
                thumbnail = interactions.EmbedImageStruct( url = "https://shortcut-test2.s3.amazonaws.com/uploads/role/attachment/346765/default_Enlarged_sunicon.png"),
                description = "Use </music_play:69420> to add music."
            )
        
        await msg.edit(niko, embeds=embed)
        return

    async def check(ctx):
        if (not ctx.author.voice.joined):
            await ctx.send('Sorry! But you need to be in the voice call in order to use these buttons!', ephemeral=True)
            return False
        else:
            return True

    song_ = player.current
    update_player = player.current
    
    message = {'niko' : niko, 'message' : '', 'stop_votes' : 0, 'voted' : [], 'lyrics' : [False, None]}
                
    voice = ctx.author.voice_state

    player = await self.lavalink.connect(voice.guild_id, voice.channel_id)
    
    while True:
        
        button_ctx = msg
        task = asyncio.create_task(wait_for_component(bot, components=buttons, check=check))
        
        while True:
            done, pending = await asyncio.wait({task}, timeout=2)
            
            if not done:
                
                db = await db_manager.GetDatabase(int(ctx.guild_id), 'current_players', default_data)   
                
                if player.current != song_:
                    await button_ctx.edit('<:nikosleepy:1027492467337080872> `Song Ended.`', embeds = [], components = [])
                    return
                
                if db['player_id'] != str(player_id):
                    await button_ctx.edit('<:nikosleepy:1027492467337080872> `Player Moved.`', embeds = [], components = [])
                    return
                
                if not player.paused and player.is_playing:
                    funny_embed = await GenerateEmbed(player.current.identifier, player, True, message['lyrics'][0], message['lyrics'][1])
                    funny_embed.set_author(name = message['message'])
                    await button_ctx.edit(message['niko'], embeds = funny_embed, components = buttons)
                continue  # very important!
                
            button_ctx = task.result()
            message = await ButtonManager(niko, msg, ctx, button_ctx, player, message['stop_votes'], message['voted'], button_id, message['lyrics'][0])
            

            if (message == 'ended'):
                print('stopping')
                return
            break
            
async def ButtonManager(niko, msg, ctx, button_ctx, player, music_votes, voted, button_id, lyrics):
    
    message = ''
    
    stop_music = False
    
    data = button_ctx.data.custom_id
            
    if (data == f"play {button_id}"):
        is_paused = player.fetch("is_paused")
        
        if not (is_paused):
            await player.set_pause(True)
            player.store("is_paused", True)
            message = "Paused the current track playing."
            niko = '<:nikosleepy:1027492467337080872>'
        elif (is_paused):
            await player.set_pause(False)
            player.store("is_paused", False)
            message = "Resumed the current track playing."
            niko = '<a:vibe:1027325436360929300>'
            
    elif (data == f"skip {button_id}"):
        await button_ctx.edit('<:nikosleepy:1027492467337080872> `Song Skipped.`', embeds=[], components =[])
        await player.skip()
        
    elif (data == f"queue {button_id}"):
        if (len(player.queue) > 0):
            
            await button_ctx.edit('Queue was opened, to get the player back, do </music get_player:1030977228885987419>.', components=[])
            id = uuid.uuid4()
            
            shuffle_emoji = interactions.Emoji(id=1031309497706225814)
            delete_emoji = interactions.Emoji(id=1031309493457399829)
            jump_emoji = interactions.Emoji(id=1031309498557681717)
            left_emoji = interactions.Emoji(id=1031309494946385920)
            right_emoji = interactions.Emoji(id=1031309496401793064)
            loop_song_emoji = interactions.Emoji(id=1019286926404091914)
            
            
            queue = await GenerateQueue(0, player)

            control_buttons = [
                interactions.Button(
                    style = interactions.ButtonStyle.PRIMARY,
                    custom_id = f"b {str(id)}",
                    emoji = left_emoji
                ),
                interactions.Button(
                    style = interactions.ButtonStyle.PRIMARY,
                    custom_id = f"n {str(id)}",
                    emoji = right_emoji
                ),
            ]

            button_ = [
                interactions.Button(
                    style = interactions.ButtonStyle.PRIMARY,
                    custom_id = f"shuffle {str(id)}",
                    emoji = shuffle_emoji,
                ),
                interactions.Button(
                    style=interactions.ButtonStyle.SECONDARY,
                    custom_id = f"l {str(id)}",
                    emoji = loop_song_emoji,
                ),
                interactions.Button(
                    style = interactions.ButtonStyle.DANGER,
                    custom_id = f"remove {str(id)}",
                    emoji = delete_emoji
                ),
                interactions.Button(
                    style = interactions.ButtonStyle.SUCCESS,
                    custom_id = f'jump {str(id)}',
                    emoji = jump_emoji
                ),
            ]
            
            control_buttons[0].disabled = True
            
            if len(player.queue) > 10:
                control_buttons[1].disabled = False
            else:
                control_buttons[1].disabled = True
                
            row1 = interactions.ActionRow(components=button_)
            row2 = interactions.ActionRow(components=control_buttons)
            
            funny_message = await button_ctx.send(embeds = queue, components=[row1, row2])

            async def checkers(ctx):
                return True
            
            page = 0
            
            while True:
                shuffle_ctx = await wait_for_component(bot, components = [row1, row2], check=checkers)

                if (shuffle_ctx.data.custom_id == f'shuffle {str(id)}'):
                    random.shuffle(player.queue)
                
                    queue = await GenerateQueue(page, player)
                    await shuffle_ctx.edit('`Shuffled Queue.`', embeds = queue, components=[row1, row2])
                if (shuffle_ctx.data.custom_id == f'remove {str(id)}'):
                    
                    options = []
                    i = 0
                
                    
                    for song in player.queue:
                        if (i < 20):
                            options.append(
                                interactions.SelectOption(
                                    label = f'{i + 1}. {song.title}',
                                    value = i
                                )
                            )

                        i += 1
                        
                    select = interactions.SelectMenu(
                        options=options,
                        placeholder= 'What Song?',
                        custom_id="woo",
                    )
                    
                    await shuffle_ctx.send(components=select, ephemeral = True)
                    
                    contexto : interactions.ComponentContext = await wait_for_component(bot, components = select, check=checkers)

                    song_ = player.queue.pop(int(contexto.data.values[0]))

                    queue_ = await GenerateQueue(page, player)
                    await funny_message.edit(f'<@{contexto.author.id}> removed {song_.title} from the queue.', embeds = queue_, components=[row1, row2])
                    await contexto.send(f'Successfully removed {song_.title} from the queue.', ephemeral = True)
                        
                if (shuffle_ctx.data.custom_id == f'jump {str(id)}'):
                    
                    options = []
                    i = 0

                    for song in player.queue:
                        if (i < 20):
                            options.append(
                                interactions.SelectOption(
                                    label = f'{i + 1}. {song.title}',
                                    value = i
                                )
                            )

                        i += 1
                        
                    select = interactions.SelectMenu(
                        options=options,
                        placeholder= 'What Song?',
                        custom_id="woo",
                    )
                    
                    await shuffle_ctx.send(components=select, ephemeral = True)

                    contexto : interactions.ComponentContext = await wait_for_component(bot, components = select, check=checkers)

                    song_ = player.queue[int(contexto.data.values[0])]
                    
                    queue_ = await GenerateQueue(page, player)
                    await funny_message.edit(f'<@{contexto.author.id}> jumped to {song_.title}.', embeds = queue_, components=[row1, row2])
                    await contexto.send(f'Successfully jumped to {song_.title}.', ephemeral = True)

                    del player.queue[0 : int(contexto.data.values[0])]
                    
                    await player.play(song_)
                
                if (shuffle_ctx.data.custom_id == f'l {str(id)}'): 
                    if not (player.repeat):
                        player.set_repeat(True)
                        await shuffle_ctx.edit('`Looping Queue.`', embeds = queue, components=[row1, row2])
                    else:
                        player.set_repeat(False)
                        await shuffle_ctx.edit('`Looping Stopped.`', embeds = queue, components=[row1, row2])
                
                if (shuffle_ctx.data.custom_id == f'b {str(id)}'):
                    page -= 1
                    
                    if len(player.queue) > 10:
                        control_buttons[1].disabled = False
                    else:
                        control_buttons[1].disabled = True
                        
                    if page > 0:
                        print('Awesome')
                        control_buttons[0].disabled = False
                    else:
                        control_buttons[0].disabled = True
                        
                    row1 = interactions.ActionRow(components=button_)
                    row2 = interactions.ActionRow(components=control_buttons)
                    
                    queue = await GenerateQueue(page, player, True, False)
                    await shuffle_ctx.edit('`Previous Page.`', embeds = queue, components=[row1, row2])
                    
                if (shuffle_ctx.data.custom_id == f'n {str(id)}'):
                    page += 1
                    
                    if len(player.queue) > 10:
                        control_buttons[1].disabled = False
                    else:
                        control_buttons[1].disabled = True
                        
                    if page > 0:
                        print('Awesome')
                        control_buttons[0].disabled = False
                    else:
                        control_buttons[0].disabled = True
                        
                    row1 = interactions.ActionRow(components=button_)
                    row2 = interactions.ActionRow(components=control_buttons)
                    
                    queue = await GenerateQueue(page, player, True, True)
                    await shuffle_ctx.edit('`Next Page.`', embeds = queue, components=[row1, row2])
        else:
            message = "Queue is currently empty :("
            
    elif (data == f"stop {button_id}"):
        
        async def StopSong():
            await button_ctx.edit('<:nikosleepy:1027492467337080872> `Song Stopped.`', embeds=[], components =[])
            await bot.disconnect(ctx.guild_id)
        
        voice_states = bot.get_channel_voice_states(player.channel_id)
        channel_members = len(voice_states) - 1
        
        votes_needed = round((channel_members / 2))
        
        if(channel_members > 1):
            if not int(button_ctx.author.id) in voted:
                music_votes += 1
                
                voted.append(int(button_ctx.author.id))
                
                if((votes_needed - music_votes) == 0):
                    await StopSong()
                    stop_music = True
                else:
                    message = f'Not enough votes to stop music! Need {votes_needed - music_votes} more.'
            else:
                message = f'Not enough votes to stop music! Need {votes_needed - music_votes} more.'
                await ctx.send('You have already voted!', ephemeral = True)
        else:
            await StopSong()
            stop_music = True
        
    elif (data == f"loop {button_id}"):
        if not lyrics:
            
            await button_ctx.defer()
            
            embed = interactions.Embed(
                title = 'Lyrics',
                description = 'Searching Genius for lyrics... <a:loading:1026539890382483576>'
            )
            
            msg = await button_ctx.send(embeds = embed)
            
            spotify = await custom_source.SearchSpotify(player.current.title, False)
            
            
            
            song = None
            
            song = genius.search_song(title = spotify['name'], artist= spotify['artist'])
            
            await msg.delete()
            
            final_song = song.lyrics
            
            lyrics = True
        else:
            lyrics = False
            final_song = None
    try:    
        funny_embed = await GenerateEmbed(player.current.identifier, player, True)
        funny_embed.set_author(name = message)
        await button_ctx.edit(niko, embeds = funny_embed)
    except:
        pass # This is kind of stupid but I don't know how to handle this exception when it occasionally happens
    
    if stop_music:
        print('wahoo')
        return 'ended'
    else:
        return {'niko' : niko, 'message' : message, 'stop_votes' : music_votes, 'voted' : voted, 'lyrics' : [lyrics, final_song]}

def setup(client):
    Music(client)