from interactions import *
from bot_data.error_handler import on_error
from bot_data.load_data import load_config
from pytube import YouTube
from uuid import uuid4

from interactions.ext.lavalink import Lavalink
from interactions.ext.database.database import Database

from spotipy import *

import asyncio
import lavalink
import random

credentials = SpotifyClientCredentials(
    client_id=load_config('CLIENTID'),
    client_secret=load_config('CLIENT-SECRET')
)

spotify = Spotify(client_credentials_manager=credentials)

class Command(Extension):
    
    def get_music_queue(self,page,  queue : list[lavalink.AudioTrack], server : Guild, song_title : str, song_artist : str, song_cover : str):
        
        queue_list = ''
        
        queue = queue[(page * 10) - 10 : (page * 10)]
        i = (page * 10) - 9
        
        
        for song in queue:
            
            title = song.title.replace('*', '\\*')
            author = song.author.replace('*', '\\*')
            
            queue_list = f'{queue_list}**{i}**. ***[{title}]({song.identifier})*** *-* ***{author}***\n'
            
            i += 1
        
        description = f'**{song_title}** by **{song_artist}** <:Sun:1026207773559619644>\n\n**Next Up...**\n{queue_list}'
        
        queue_embed = Embed(title='**Currently Playing:**', description = description, color = 0x8b00cc)
        
        queue_embed.set_author(name = f'Queue for {server.name}', icon_url=server.icon_url)
        queue_embed.set_thumbnail(url = song_cover)
        
        return queue_embed
    
    music_queue_buttons = [
        Button(
            emoji = Emoji(id=1031309497706225814),
            custom_id = 'shuffle',
            style = ButtonStyle.SECONDARY
        ),
        Button(
            emoji = Emoji(id=1031309493457399829),
            custom_id = 'delete',
            style = ButtonStyle.DANGER
        ),
        Button(
            emoji = Emoji(id=1031309498557681717),
            custom_id = 'jump',
            style = ButtonStyle.SUCCESS
        )
    ]
    
    @extension_component('shuffle')
    async def on_shuffle(self, ctx : CommandContext):
        player : lavalink.DefaultPlayer = self.lavalink.get_player(int(ctx.guild_id))
        
        if len(player.queue) == 0:
            await ctx.send(' [ Cannot shuffle anything. ]', ephemeral = True)
            return
        
        if not await self.check(player.current.requester, ctx.author):
            await ctx.send('[ You cannot edit the queue. ]', ephemeral = True)
            return
        
        random.shuffle(player.queue)
        
        await ctx.send('[ Successfully shuffled queue. ]', ephemeral = True)
        await ctx.channel.send(f'[ <@{int(ctx.author.id)}> shuffled the queue. ]')
    
    @extension_component('jump')
    async def on_jump(self, ctx : CommandContext):
        player : lavalink.DefaultPlayer = self.lavalink.get_player(int(ctx.guild_id))
        
        if len(player.queue) == 0:
            await ctx.send(' [ Cannot jump to anything. ]', ephemeral = True)
            return
        
        if not await self.check(player.current.requester, ctx.author):
            await ctx.send('[ You cannot edit the queue. ]', ephemeral = True)
            return
        
        song_list = []
        
        i = 1
        for song in player.queue:
            song_list.append(
                SelectOption(
                    label = f'{i}. {song.title}',
                    value = i - 1
                )
            )
            i += 1
            
        select_list : list[SelectMenu] = []
        
        i = 0
        index = 1
        
        if len(song_list) > 25:
            
            page_list = []
            
            for song in song_list:
                if i % 25 == 0:
                    page_list.append(
                        SelectOption(
                            label=f'Page {index}.',
                            value = index
                        )
                    )
                    index += 1
                
                i += 1
            
            select_page_list = SelectMenu(
                              custom_id=f'SelectMenu1',
                              placeholder=f'What page?',
                              options=page_list
                          )
                
            await ctx.send(components = select_page_list, ephemeral = True)
            
            s_ctx = await self.client.wait_for_component(select_page_list)
        
            data = int(s_ctx.data.values[0])
            
            select_list = []
            
            number = 25 * data
            starting_index = number - 25
            
            select_list.append(
                SelectMenu(
                    custom_id=f'SelectMenu1',
                    placeholder=f'Where to jump?',
                    options=song_list[starting_index : number]
                )
            )
            
            ctx = s_ctx
        else:        
            select_list.append(
                SelectMenu(
                    custom_id=f'SelectMenu1',
                    placeholder=f'Where to jump?',
                    options=song_list[0 : 26]
                )
            )
            
        await ctx.send(components = select_list, ephemeral = True)
        
        s_ctx = await self.client.wait_for_component(select_list)
        
        data = int(s_ctx.data.values[0])
        
        song = player.queue[data]
        
        del player.queue[0 : data]
        
        await s_ctx.send('[ Successfully jumped to song. ]', ephemeral = True)
        await s_ctx.channel.send(f'[ <@{int(ctx.author.id)}> jumped to **{song.title}** on the queue. ]')
        
        await player.skip()
    
    @extension_component('delete')
    async def on_delete(self, ctx : CommandContext):
        player : lavalink.DefaultPlayer = self.lavalink.get_player(int(ctx.guild_id))
        
        if len(player.queue) == 0:
            await ctx.send(' [ Cannot remove anything. ]', ephemeral = True)
            return
        
        if not await self.check(player.current.requester, ctx.author):
            await ctx.send('[ You cannot edit the queue. ]', ephemeral = True)
            return
        
        song_list = []
        
        i = 1
        for song in player.queue:
            song_list.append(
                SelectOption(
                    label = f'{i}. {song.title}',
                    value = i - 1
                )
            )
            i += 1
            
        select_list : list[SelectMenu] = []
        
        i = 0
        index = 1
        
        if len(song_list) > 25:
            
            page_list = []
            
            for song in song_list:
                if i % 25 == 0:
                    page_list.append(
                        SelectOption(
                            label=f'Page {index}.',
                            value = index
                        )
                    )
                    index += 1
                
                i += 1
            
            select_page_list = SelectMenu(
                              custom_id=f'SelectMenu1',
                              placeholder=f'What page?',
                              options=page_list
                          )
                
            await ctx.send(components = select_page_list, ephemeral = True)
            
            s_ctx = await self.client.wait_for_component(select_page_list)
        
            data = int(s_ctx.data.values[0])
            
            select_list = []
            
            number = 25 * data
            starting_index = number - 25
            
            select_list.append(
                SelectMenu(
                    custom_id=f'SelectMenu1',
                    placeholder=f'What to delete?',
                    options=song_list[starting_index : number]
                )
            )
            
            ctx = s_ctx
        else:        
            select_list.append(
                SelectMenu(
                    custom_id=f'SelectMenu1',
                    placeholder=f'What to delete?',
                    options=song_list[0 : 26]
                )
            )
            
        await ctx.send(components = select_list, ephemeral = True)
        
        s_ctx = await self.client.wait_for_component(select_list)
        
        data = int(s_ctx.data.values[0])
        
        song = player.queue[data]
        
        del player.queue[data]
        
        await s_ctx.send('[ Successfully removed song. ]', ephemeral = True)
        await s_ctx.channel.send(f'[ <@{int(ctx.author.id)}> removed **{song.title}** from the queue. ]')  
    
    def get_music_stopped_embed(self, song_title : str, song_artist : str, song_cover : str, song_url : str):
        description = f'By **{song_artist}** <:spotify:1066028282623037541>'
        
        embed = Embed(title = song_title, description=description, url=song_url, color=0x40444b)

        embed.set_author(name='Stopped Playing...')
            
        embed.set_thumbnail(song_cover)
        
        return embed
    
    def get_music_playing_embed(self, text : str, song_title : str, song_artist : str, song_cover : str, song_url : str,  song_time : int, song_dur : int, author : User):
        
        end_emoji_empty = '<:End2:1066466225321947177>'
        end_emoji_filled = '<:End2_filled:1066466227519766648>'
        middle_emoji_empty = '<:middle:1066466230246064128>'
        middle_emoji_filled = '<:Middle_filled:1066466232376766494>'
        end2_emoji_empty = '<:End:1066466220532043938>'
        end2_emoji_filled = '<:End_filled:1066466223572910161>'
                
        progress_bar = f'▱▱▱▱▱▱▱▱▱▱▱'
        progress_bar_l = list(progress_bar)
        
        current_time = round((song_time / song_dur) * len(progress_bar), 0)
        
        i = 0
        for _ in progress_bar:
            if i < current_time:
        
                progress_bar_l[i] = middle_emoji_filled
                
                if i == 0:
                    progress_bar_l[i] = end_emoji_filled
                
                if i == len(progress_bar_l) - 1:
                    progress_bar_l[i] = end2_emoji_filled
            else:
                
                progress_bar_l[i] = middle_emoji_empty
                
                if i == 0:
                    progress_bar_l[i] = end_emoji_empty
                
                if i == len(progress_bar_l) - 1:
                    progress_bar_l[i] = end2_emoji_empty
                
            i += 1
            
        progress_bar = ''.join(progress_bar_l)
        
        current = lavalink.format_time(song_time)
        total = lavalink.format_time(song_dur)
            
        description = f'By **{song_artist}** <:spotify:1066028282623037541>\n\n{progress_bar}\n{current} <:Sun:1026207773559619644> {total}'
        
        embed = Embed(title = song_title, description=description, url=song_url, color=0x8b00cc)
        
        embed.set_author(name=text)
            
        embed.set_thumbnail(song_cover)
        
        embed.set_footer(f'Requested by {author.username}', icon_url=author.avatar_url)
        
        return embed
    
    
    async def load_spotify_search(self, content):
        search_ : dict = spotify.search(content, limit=25, type = 'track')
        
        tracks = []
        
        for result in search_['tracks']['items']:
                song_name = result['name']
                artists = result['artists'][0]
                url = result['id']
                
                if len(f'"{song_name}"\n - {artists["name"]}') > 99:
                    continue
            
                tracks.append({"Text" : f'"{song_name}"\n by {artists["name"]}', "URL" : f'http://open.spotify.com/track/{url}'})
        
        return tracks
    
    async def load_spotify_result(self, track):        
        
        if 'http://open.spotify.com/track/' in track or 'https://open.spotify.com/track/' in track:
            result = spotify.track(track)
        else:
            search_ : dict = spotify.search(track, type = 'track')
            result = search_['tracks']['items'][0]
        
        song_name = result['name']
        artists = result['artists'][0]['name']
        url = result['id']
        
        cover = result['album']['images'][0]['url']
        
        return {'name' : song_name, 'artists' : artists, 'cover' : cover, 'url' : f'http://open.spotify.com/track/{url}'}
    
    async def load_spotify_playlist(self, track, album = False):        
        
        if album:
            search_ = spotify.album(track)
        else:
            search_ = spotify.playlist(track)
            
        tracks = []
        
        for result in search_['tracks']['items']:
            
            if not album:
                result = result['track']
            
            song_name = result['name']
            artists = result['artists'][0]
            url = result['id']
            
            if len(f'"{song_name}"\n - {artists["name"]}') > 99:
                continue
        
            tracks.append(f'http://open.spotify.com/track/{url}')
        
        return tracks
    
    def __init__(self, client):
        self.client = client
        self.lavalink: Lavalink = None

    # * ------------------------------------------------------------------------------ * #

    @extension_listener()
    async def on_start(self):
        # Initialize lavalink instance
        self.lavalink: Lavalink = Lavalink(self.client)

        # Connect to lavalink server
        self.lavalink.add_node(load_config('Music')['ip'], load_config('Music')['id'], "youshallnotpass", "us")
        
        # Initialize Database
        await Database.create_database('allowed_users', Database.DatabaseType.USER, {'users' : []})
        
        if int(self.client.me.id) == 1028058097383641118:
            channel = await get(self.client, Channel, object_id=850069038804631575)
            
            await channel.send('Bot has restarted.')
        
    @extension_command(description = 'Use the Music Module!')
    async def music(self, ctx : CommandContext):
        db = await Database.get_item(ctx, 'allowed_users')
        
        users = db['users']
        
        if not int(ctx.author.id) in users:
        
            users.append(int(ctx.author.id))
        
            await Database.set_item(ctx, 'allowed_users', {'users' : users})
    
    @music.subcommand(description = 'Allow users to control the player')
    @option(description='The user.')
    async def allow_control(self, ctx : CommandContext, user : User):
        
        db = await Database.get_item(ctx, 'allowed_users')
        
        users = db['users']
        
        users.append(int(user.id))
        
        await Database.set_item(ctx, 'allowed_users', {'users' : users})
        
        await ctx.send(f'[ Added {user.username}. ]', ephemeral = True)
        
    @music.subcommand(description = 'Remove a user from controlling the player')
    @option(description='The user.')
    async def remove_control(self, ctx : CommandContext, user : User):
        
        db = await Database.get_item(ctx, 'allowed_users')
        
        users = db['users']
        
        if int(user.id) in users:
            users.remove(int(user.id))
            
            await Database.set_item(ctx, 'allowed_users', {'users' : users})
            
            await ctx.send(f'[ Removed {user.username}. ]', ephemeral = True)
            
            return
        
        await ctx.send(f'[ Cannot remove {user.username}. ]', ephemeral = True)
    
    @music.subcommand(description='Plays a music track from Spotify.')
    @option(description = 'A song to search for.', autocomplete = True)
    async def play(self, ctx : CommandContext, search : str):
        
        await ctx.defer()
        
        print(search)
        
        # Getting user's voice state
        voice_state: VoiceState = ctx.author.voice_state
        if not voice_state or not voice_state.joined:
            return await ctx.send("[ You're not connected to the voice channel. Try rejoining. ]")

        # Connecting to voice channel and getting player instance
        player = await self.lavalink.connect(voice_state.guild_id, voice_state.channel_id)

        if 'https://youtu.be' in search or 'https://www.youtube.com' in search or 'https://m.youtube.com' in search or 'https://youtube.com' in search:
            try:
                yt = YouTube(search)
                song = await self.load_spotify_result(f'{yt.title}')
            except:
                await ctx.send('[ Could not find anything on Spotify for this Youtube URL. ]', ephemeral=True)
                return
                
                
            button = [
                Button(style = ButtonStyle.SECONDARY, label = 'Search', custom_id='search_for_this'),
                Button(style = ButtonStyle.DANGER, label = 'Cancel', custom_id='cancel_this')
            ]
            
            youtube_embed = Embed(description=f'[ Detected a Youtube link. Found **{song["name"]}** by **{song["artists"]}** on Spotify. Is this correct? ]', color=0xff1515)
            
            youtube_message = await ctx.send(embeds = youtube_embed, ephemeral = True, components = button)
            
            async def check_(ctx_):
                if ctx_.author.id == ctx.author.id:
                    return True
                else:
                    await ctx_.send('[ Only the requester of this track can search for this track. ]', ephemeral = True)
                    return False
            
            button_ctx = await self.client.wait_for_component(button, check = check_)
            
            data = button_ctx.data.custom_id
            
            if data == 'search_for_this':
                await button_ctx.defer(edit_origin = True)
                await youtube_message.delete()
            
                search = song['url']
            else:
                await button_ctx.send('[ Cancelled decision. ]', ephemeral = True)
                await youtube_message.delete()
                return
            
            
        if f'http://open.spotify.com/playlist/' in search or f'https://open.spotify.com/playlist/' in search or f'https://open.spotify.com/album/' in search:
            
            try:
                if 'album' in search:
                    playlist = await self.load_spotify_playlist(search, True)
                else:
                    playlist = await self.load_spotify_playlist(search)
            except:
                await ctx.send('[ This seems to be an invalid Spotify Playlist/Album URL. ]', ephemeral = True)
                return
                
            if len(playlist) == 0:
                await ctx.send('[ This seems to be an invalid Spotify Playlist/Album URL. ]', ephemeral = True)
                return
            
            msg = await ctx.send(f"[ Adding **{len(playlist)} songs** to the queue... <a:loading:1026539890382483576> ]")
            
            count = 0
            
            for song in playlist:
                
                try:
                    song = await self.load_spotify_result(song)
                    search_ = f'{song["name"]} by {song["artists"]}'
                
                    # Getting user's voice state
                    voice_state: VoiceState = ctx.author.voice_state
                    if not voice_state or not voice_state.joined:
                        return await ctx.send("You're not connected to the voice channel!")

                    # Connecting to voice channel and getting player instance
                    player = await self.lavalink.connect(voice_state.guild_id, voice_state.channel_id)

                    # Getting tracks from youtube
                    tracks = await player.search_youtube(f'{search_}')
                    # Selecting first founded track
            
                    track = None
            
                    for track_ in tracks[0 : 30]:
                        if 'extended' in track_.title.lower():
                            continue
                
                        track = track_
                        break
            
                    track.title = song["name"]
                    track.author = song["artists"]
                    track.identifier = song["url"]
                    track.source_name = song['cover']
            
                    # Adding track to the queue
                    player.add(requester=int(ctx.author.id), track=track)
                    
                except:
                    count += 1
                    
            player.store(f'playing {player.guild_id}', ctx)
            player.store(f'requestor {player.guild_id}', ctx.author.user)
                
            if not player.is_playing:
                await player.play()
                
            await msg.edit(f"[ Finished adding **{len(playlist) - count} songs** to the queue. ]")
            
            return
        
        try:
            song = await self.load_spotify_result(search)
        except:
            await ctx.send(f'[ No results for **{search}**. ]', ephemeral = True)
            return
        
        search = f'{song["name"]} by {song["artists"]}'

        # Selecting first founded track
         # Getting tracks from youtube
        tracks = await player.search_youtube(f'{search}')
        
        track = None
        
        for track_ in tracks[0 : 30]:
            if 'extended' in track_.title.lower(): # Prevents extended tracks from playing, unless it's a specified URL.
                continue
            
            track = track_
            break
        
        track.title = song["name"]
        track.author = song["artists"]
        track.identifier = song["url"]
        track.source_name = song['cover']
        
        # Adding track to the queue
        player.add(requester=int(ctx.author.id), track=track)
        
        player.store(f'playing {player.guild_id}', ctx)
        player.store(f'requestor {player.guild_id}', ctx.author.user)

        # Check if already playing
        if player.is_playing and not player.fetch(f'nothing_playing {player.guild_id}'):
            
            add_to_queue_embed = Embed(
                title="Added to Queue",
                description=f'[ Added **{song["name"]}** by **{song["artists"]}** to the music queue. ]',
                color=0x1fef2f
            )
            
            add_to_queue_embed.set_thumbnail(song['cover'])
            add_to_queue_embed.set_footer(text='Requested by: ' + ctx.author.user.username, icon_url=ctx.author.user.avatar_url)
            
            return await ctx.send(embeds = add_to_queue_embed)

        await ctx.send('[ Now playing selected track. ]', ephemeral = True)

        # Starting playing track
        await player.play()
        
    buttons = [
        Button(
            emoji = Emoji(id = 1019286929059086418),
            custom_id = 'queue',
            style = ButtonStyle.DANGER
        ),
        Button(
            emoji = Emoji(id = 1019286927888883802),
            custom_id = 'pause',
            style = ButtonStyle.DANGER
        ),
        Button(
            emoji = Emoji(id = 1019286931504386168),
            custom_id = 'stop',
            style = ButtonStyle.DANGER
        ),
        Button(
            emoji = Emoji(id = 1019286926404091914),
            custom_id = 'loop',
            style = ButtonStyle.DANGER
        ),
        Button(
            emoji = Emoji(id = 1019286930296410133),
            custom_id = 'skip',
            style = ButtonStyle.DANGER
        )
    ]
    
    async def check(self, requester : int, author : Member):
        
        db = await Database.get_item(requester, 'allowed_users')
        
        if Permissions.MANAGE_CHANNELS in author.permissions:
            return True
        
        if not author.voice_state or not author.voice_state.joined:
            return False
        
        requester_member : Member = await get(self.client, Member, object_id=requester, guild_id = author.guild_id)
        
        voice_state = requester_member.voice_state
        
        print(voice_state)
        
        if not voice_state or not voice_state.joined:
            return True
        
        if user in db['users']:
            return True
        else:
            return False
    
    @extension_component('pause')
    async def on_pause(self, ctx : CommandContext):    
        
        player : lavalink.DefaultPlayer = self.lavalink.get_player(int(ctx.guild_id))
        
        if not await self.check(player.current.requester, ctx.author):
            await ctx.send('[ You cannot control the player. ]', ephemeral = True)
            return
        
        paused = not player.paused
        
        await player.set_pause(paused)
        
        if paused:
            await ctx.send(f'[ <@{int(ctx.author.id)}> paused. ]')
        else:
            await ctx.send(f'[ <@{int(ctx.author.id)}> unpaused. ]')
            
    @extension_component('stop')
    async def on_stop(self, ctx : CommandContext):
        
        player : lavalink.DefaultPlayer = self.lavalink.get_player(int(ctx.guild_id))
        
        if not await self.check(player.current.requester, ctx.author):
            await ctx.send('[ You cannot control the player. ]', ephemeral = True)
            return
        
        await player.stop()
        
        await ctx.send(f'[ <@{int(ctx.author.id)}> stopped the current track playing. ]')
        
    @extension_component('skip')
    async def on_skip(self, ctx : CommandContext):
        
        player : lavalink.DefaultPlayer = self.lavalink.get_player(int(ctx.guild_id))
        
        if not await self.check(player.current.requester, ctx.author):
            await ctx.send('[ You cannot control the player. ]', ephemeral = True)
            return
        
        await ctx.defer(edit_origin = True)
        
        await ctx.channel.send(f'[ <@{int(ctx.author.id)}> skipped the current track playing. ]')
        
        await player.skip()
        
    @extension_component('loop')
    async def on_loop(self, ctx : CommandContext):
        
        player : lavalink.DefaultPlayer = self.lavalink.get_player(int(ctx.guild_id))
        
        if not await self.check(player.current.requester, ctx.author):
            await ctx.send('[ You cannot control the player. ]', ephemeral = True)
            return
        
        if player.loop == 0:
            player.set_loop(1)
            await ctx.send(f'[ <@{int(ctx.author.id)}> started looping the current track. ]')
        else:
            player.set_loop(0)
            await ctx.send(f'[ <@{int(ctx.author.id)}> stopped looping the current track. ]')
        
    @extension_component('queue')
    async def on_queue(self, ctx : CommandContext):
        
        player : lavalink.DefaultPlayer = self.lavalink.get_player(int(ctx.guild_id))
        
        if len(player.queue) == 0:
            await ctx.send('[ Queue is currently empty! ]', ephemeral = True)
            return

        page = 1
        
        queue_embed = self.get_music_queue(page, player.queue, ctx.guild, player.current.title, player.current.author, player.current.source_name)
        
        buttons = [
            Button(
                emoji = Emoji(id=1031309494946385920),
                custom_id = 'left',
                style = ButtonStyle.PRIMARY
            ),
            Button(
                emoji = Emoji(id=1031309496401793064),
                custom_id = 'right',
                style = ButtonStyle.PRIMARY
            ),
        ]
        
        buttons[0].disabled = True
        
        if len(player.queue) > 10:
            buttons[1].disabled = False
        else:
            buttons[1].disabled = True
            
        msg = await ctx.send(embeds=queue_embed, components = [buttons, self.music_queue_buttons])
        
        while True:
            
            button_ctx : ComponentContext = await self.client.wait_for_component(buttons)
            
            await button_ctx.defer(edit_origin=True)
            
            data = button_ctx.data.custom_id
            
            if data == 'left':
                page -= 1
            
            if data == 'right':
                page += 1
                
            if page > 1:
                buttons[0].disabled = False
            else:
                buttons[0].disabled = True
                
            if len(player.queue[(page * 10) - 10 : (page * 10)]) % 10 == 0:
                buttons[1].disabled = False
            else:
                buttons[1].disabled = True
                
            queue_embed = self.get_music_queue(page, player.queue, ctx.guild, player.current.title, player.current.author, player.current.source_name, player.current.identifier)
                
            await msg.edit(embeds=queue_embed, components = [buttons, self.music_queue_buttons])
    
    @extension_listener()
    async def on_track_start(self, event: lavalink.TrackStartEvent):
        """Fires when track starts"""
        await self.on_player(event)
        
    @music.subcommand(description='Opens the player.')
    async def open_player(self, ctx : CommandContext):
        
        player : lavalink.DefaultPlayer = self.lavalink.get_player(int(ctx.guild_id))
        
        if not player.is_playing:
            await ctx.send("[ Player needs to playing something in order to show! ]", ephemeral = True)
            return
            
        await ctx.send("[ Opened the player. ]", ephemeral = True)
        await self.on_player(ctx = ctx)
        
    async def on_player(self, event: lavalink.TrackStartEvent = None, ctx : CommandContext = None):
        
        if ctx != None:
            player : lavalink.DefaultPlayer = self.lavalink.get_player(int(ctx.guild_id))
        else:
            player : lavalink.DefaultPlayer = event.player
            ctx : CommandContext = player.fetch(f'playing {player.guild_id}')
        
        if player.loop == 1:
            return
        
        uid = str(uuid4())
        
        player.store(f'uid {player.guild_id}', uid)
        
        requester : User = await get(self.client, User, object_id=player.current.requester)
        
        if requester.bot:
            return
        
        if player.fetch(f'nothing_playing {player.guild_id}'):
            player.store(f'nothing_playing {player.guild_id}', False)
            
            await player.skip()
        
        song = await self.load_spotify_result(f'{player.current.identifier}')
        
        msg = await ctx.channel.send('<a:vibe:1027325436360929300>')
        
        while player.current != None and player.fetch(f'uid {player.guild_id}') == uid:
            
            paused = player.paused
            text = ''
                
            if paused:
                text = 'Paused...'
                niko = '<:nikosleepy:1027492467337080872>'
            elif player.loop == 1:
                text = 'Now Looping...'
                niko = '<a:vibe:1027325436360929300>'
            else:
                text = 'Now Playing...'
                niko = '<a:vibe:1027325436360929300>'
            
            music_playing_embed = self.get_music_playing_embed(text, song['name'], song['artists'], song['cover'], song['url'], song_time= player.position, song_dur= player.current.duration, author= requester)
            await msg.edit(niko, embeds = music_playing_embed, components = self.buttons)
            
            await asyncio.sleep(1)
            
        stopped_playing_embed = self.get_music_stopped_embed(song['name'], song['artists'], song['cover'], song['url'])
        niko = '<:nikosleepy:1027492467337080872>'

        await msg.edit(niko, embeds = stopped_playing_embed, components=[])
        
        return

    @extension_listener()
    async def on_queue_end(self, event: lavalink.QueueEndEvent):
        """Fires when queue ends"""
        
        embed = Embed(title = 'End of Queue.', description = '[ Play more songs using `/music play <args>` ]', color = 0xff2d32)
        
        player : lavalink.DefaultPlayer = event.player
        ctx : CommandContext = player.fetch(f'playing {player.guild_id}')
        
        await ctx.channel.send(embeds = embed)
    
    @play.autocomplete('search')
    async def autocomplete(self, ctx, text : str = 'nightmargin oneshot'): # teehee
        
        items = await self.load_spotify_search(text)
        
        if 'https://youtu.be' in text or 'https://www.youtube.com' in text or 'https://m.youtube.com' in text:
            choices = [
                Choice(name='🔗 Youtube URL', value=text)
            ]
        elif 'http://open.spotify.com/' in text or 'https://open.spotify.com/' in text:
            choices = [
                Choice(name='🔗 Spotify URL', value=text)
            ]
        else:
            choices = [
                Choice(name=item['Text'], value=item['URL']) for item in items
            ]
        
        try:
            await ctx.populate(choices)
        except:
            choices = [
                Choice(name=f'❌ [ Sorry, an error occurred within the search... Maybe try again later? ]', value='https://open.spotify.com/track/4cOdK2wGLETKBW3PvgPWqT?si=a1cc13ee4eca4be5')
            ]
            
            await ctx.populate(choices)
    
    @music.error
    async def error(self, ctx : CommandContext, error):
        
        embed = await on_error(error)
        
        await ctx.send(embeds=embed)
def setup(client):
    Command(client)