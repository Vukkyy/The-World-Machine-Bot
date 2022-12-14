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
        print('loaded music')

    @extension_component('play')
    async def play(self, ctx : CommandContext):
        print('play')
        await ctx.send('play')
        await Database.set_item(ctx, 'Music', 'is_paused', True)
        
    @extension_component('skip')
    async def play(self, ctx : CommandContext):
        await ctx.send('skip')
        await Database.set_item(ctx, 'Music', 'music_stopped', True)
        
    @extension_component('stop')
    async def play(self, ctx : CommandContext):
        await ctx.send('stop')
        await Database.set_item(ctx, 'Music', 'music_skipped', True)

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
                          
            await self.ShowPlayer(ctx, event.player, False)

    @extension_listener()
    async def on_start(self):
        
        self.lavalink: Lavalink = Lavalink(self.client)
        
        self.lavalink.add_node(
            host = '162.248.100.61',
            port = 10333,
            password = 'youshallnotpass',
            region = "us"
        )
        
        d = {
            'is_paused' : False,
            'music_stopped' : False,
            'music_skipped' : False,
            
            'stop_votes' : 0,
            'st_voted': [],
            
            'skip_votes' : 0,
            'sk_voted': [],
            
            'player_id': 0,
            'message' : '',
            'niko' : ''
        }
        
        await Database.create_database('Music', Database.DatabaseType.GUILD, d)
        
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

    @extension_command() 
    async def music(self, ctx: CommandContext):
        pass
    
    async def check(self, ctx : CommandContext = None):
        
        voice : VoiceState = ctx.author.voice_state
        
        await ctx.defer()
        
        if not voice or not voice.joined:
            await ctx.send("Sorry! You need to be in a voice channel to use this command.", ephemeral = True)
            return False
    
        if (voice.guild_id != ctx.guild_id):
            await ctx.send("Sorry! You need to be in a voice channel to use this command.", ephemeral = True)
            return False
        
        return True
    
    @music.subcommand(description='Play a song.')
    @option(description = 'A song to search for.', required = True, autocomplete=True)
    async def search(self, ctx: CommandContext, query : str):
        
        if not await self.check(ctx):
            return
        
        voice : VoiceState = ctx.author.voice_state
        
        #await ctx.defer()

        player = await self.lavalink.connect(voice.guild_id, voice.channel_id)

        player.store(f'channel {ctx.guild_id}', ctx)

        if (query.startswith("https://open.spotify.com/")):
            query = await custom_source.SearchSpotify(query)

        if ('playlist' in query or 'list=PL' in query):
            playlist = await custom_source.GetPlaylist(query)

            msg_ = await ctx.send(f'Adding **{len(playlist)}** songs to the queue. This might take a while. <a:loading:1026539890382483576>')

            print(playlist)

            successful = 0
            
            for video in playlist:
                try:
                    query = await custom_source.SearchSpotify(video, False)
                    tracks = await player.search_youtube(query)
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
            tracks = await player.search_youtube(query)

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
            
    @search.autocomplete('query')
    async def search_(self, ctx : CommandContext, search_):
        
        print(search_)
        
        items = await custom_source.SearchAll(search_)
        # add item to the choices list only if the user_input is in the item name
        choices = [
            interactions.Choice(name=item, value=item) for item in items
        ] 
        await ctx.populate(choices)
        
    @music.subcommand()
    async def get_player(self, ctx : CommandContext):
        
        if not await self.check(ctx):
            return
        
        voice : VoiceState = ctx.author.voice_state
        player = await self.lavalink.connect(voice.guild_id, voice.channel_id)
        
        player.store(f'channel {ctx.guild_id}', ctx)
        await self.ShowPlayer(ctx, player, True)
    
    @music.subcommand()
    async def stop(self, ctx : CommandContext):
        
        if not await self.check(ctx):
            return
        
        await ctx.send('Stopping music...', ephemeral = True)
        await Database.set_item(ctx, 'Music', 'music_stopped', True)
        
    @music.subcommand()
    async def skip(self, ctx : CommandContext):
        
        if not await self.check(ctx):
            return
        
        await ctx.send('Skipping music...', ephemeral = True)
        await Database.set_item(ctx, 'Music', 'music_skipped', True)
        
    @music.subcommand()
    async def pause(self, ctx : CommandContext):
        
        if not await self.check(ctx):
            return
        
        await ctx.send('Playing/Pausing music...', ephemeral = True)
        await Database.set_item(ctx, 'Music', 'is_paused', True)
            
    async def GenerateEmbed(self, id : str, player__ : lavalink.DefaultPlayer, player, show_lyrics = False, spotifydata : dict = {}):
        
        spotify = spotifydata
        
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
            
            if (player):
                return interactions.Embed(
                    title = f"Now Playing: ***{spotify['name']}***",
                    thumbnail = interactions.EmbedImageStruct( url = spotify['art'], height = 720, width = 1280),
                    description = f"{length} \n\n *{new_c_length} / {new_length}*",
                    footer = interactions.EmbedFooter( text = 'Do /music get_player if you\'ve lost the player.'),
                )
            else:
                return interactions.Embed(
                    title = f"Now Playing: ***{spotify['name']}***",
                    thumbnail = interactions.EmbedImageStruct( url = spotify['art'], height = 720, width = 1280),
                    description = f"Loading Player... <a:loading:1026539890382483576> \n\n *00:00 / {new_length}*",
                    footer = interactions.EmbedFooter( text = 'Do /music get_player if you\'ve lost the player.'),
                )

    async def GenerateQueue(self, page_number, player : lavalink.DefaultPlayer, controls = False, forward = False):
        
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
                    q = await self.GenerateQueue(page_number, player)
                    return q
                else:
                    page_number += 1
                    q = await self.GenerateQueue(page_number, player)
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

    async def ShowPlayer(self, ctx : interactions.CommandContext, player : lavalink.DefaultPlayer, player__ : bool, updating : bool = False):
        
        buttons = []
        
        voice = ctx.author.voice_state
        
        player = await self.lavalink.connect(voice.guild_id, voice.channel_id)
        
        spotify = await custom_source.SearchSpotify(f'{player.current.title} {player.current.author}', False)
        
        if updating:
            return
        
        message = ""
        
        player_id = uuid.uuid4()
        
        button_id = uuid.uuid4()
        
        await Database.set_item(ctx, 'Music', 'player_id', str(player_id))

        msg = await ctx.send('Loading Player... <a:loading:1026539890382483576>')
        niko = '<a:vibe:1027325436360929300>'
        
        await Database.set_item(ctx, 'Music', 'niko', niko)
        
        if (player.is_playing):
            embed = await self.GenerateEmbed(self, player.current.identifier, player, spotifydata=spotify)
            msg = await msg.edit(niko, embeds=embed, components=buttons)
        else:
            embed = interactions.Embed(
                    title = "Not Currently Playing Anything",
                    thumbnail = interactions.EmbedImageStruct( url = "https://shortcut-test2.s3.amazonaws.com/uploads/role/attachment/346765/default_Enlarged_sunicon.png"),
                    description = "Use </music_play:69420> to add music."
                )
            
            await msg.edit(niko, embeds=embed)
            return

        song_ = player.current
        
        while True:
            
            player = await self.lavalink.connect(voice.guild_id, voice.channel_id)
            
            await asyncio.sleep(2)
                    
            db = await Database.get_item(ctx, 'Music')
            
            is_paused = db['is_paused']
            music_stopped = db['music_stopped']
            music_skipped = db['music_skipped']
            niko = db['niko']
            
            if is_paused:
                
                paused = not player.paused
                
                await player.set_pause(paused)
                
                if player.paused:
                    edb = await Database.set_item(ctx, 'Music', 'message', 'Player is currently paused.')
                    
                    funny_embed = await self.GenerateEmbed(self, player.current.identifier, player, True, spotifydata=spotify)
                    funny_embed.set_author(name = edb['message'])
                    
                    await Database.set_item(ctx, 'Music', 'niko', '<:nikosleepy:1027492467337080872>')
                    
                    await ctx.edit('<:nikosleepy:1027492467337080872>', embeds = funny_embed)
                    await Database.set_item(ctx, 'Music', 'is_paused', False)
                    
                    continue
                else:
                    await Database.set_item(ctx, 'Music', 'niko', '<a:vibe:1027325436360929300>')
                    await Database.set_item(ctx, 'Music', 'is_paused', False)
            
            if music_stopped:
                
                voice_states = ctx.channel.voice_states
                channel_members = len(voice_states) - 1
                
                votes_needed = round((channel_members / 2))
                
                stop_votes = db['stop_votes']
                voted = db['st_voted']
                
                if(channel_members > 1):
                    if not int(ctx.author.id) in voted:
                        voted.append(int(ctx.author.id))
                        stop_votes += 1
                        
                        if((votes_needed - stop_votes) == 0):
                            await self.lavalink.disconnect(ctx.guild_id)
                            await ctx.edit('<:nikosleepy:1027492467337080872> `Song Stopped.`', embeds = [], components = [])
                            
                            await Database.delete_item(ctx, 'Music')
                            break
                        
                        await Database.set_item(ctx, 'Music', 'st_voted', voted)
                        await Database.set_item(ctx, 'Music', 'stop_votes', stop_votes)
                        
                        edb = await Database.set_item(ctx, 'Music', 'message', f'Not enough votes to stop music! Need {votes_needed - stop_votes} more.')
                
                        funny_embed = await self.GenerateEmbed(self, player.current.identifier, player, True, spotifydata=spotify)
                        funny_embed.set_author(name = edb['message'])
                        
                        await ctx.edit(edb['niko'], embeds = funny_embed)
                        
                        await Database.set_item(ctx, 'Music', 'music_stopped', False)
                        
                        continue
                    else:
                        await ctx.send('You have already voted!', ephemeral = True)
                else:
                    await self.lavalink.disconnect(ctx.guild_id)
                    await ctx.edit('<:nikosleepy:1027492467337080872> `Song Stopped.`', embeds = [], components = [])
                    
                    await Database.delete_item(ctx, 'Music')
                    break
                
            if music_skipped:
                
                channel : Channel = await get(self.client, Channel, object_id = player.channel_id)
                
                voice_states = channel.voice_states
                
                channel_members = len(voice_states) - 1
                
                votes_needed = round((channel_members / 2))
                
                stop_votes = db['skip_votes']
                voted = db['sk_voted']
                
                if(channel_members > 1):
                    if not int(ctx.author.id) in voted:
                        voted.append(int(ctx.author.id))
                        stop_votes += 1
                        
                        if((votes_needed - stop_votes) == 0):
                            await player.skip()
                            await ctx.edit('<:nikosleepy:1027492467337080872> `Song Skipped.`', embeds = [], components = [])
                            
                            await Database.delete_item(ctx, 'Music')
                            break
                        
                        await Database.set_item(ctx, 'Music', 'sk_voted', voted)
                        await Database.set_item(ctx, 'Music', 'skip_votes', stop_votes)
                        
                        edb = await Database.set_item(ctx, 'Music', 'message', f'Not enough votes to skip track! Need {votes_needed - stop_votes} more.')
                
                        funny_embed = await self.GenerateEmbed(self, player.current.identifier, player, True, spotifydata=spotify)
                        funny_embed.set_author(name = edb['message'])
                        
                        await ctx.edit(edb['niko'], embeds = funny_embed)
                        
                        await Database.set_item(ctx, 'Music', 'music_skipped', False)
                        
                        continue
                    else:
                        await ctx.send('You have already voted!', ephemeral = True)
                else:
                    await player.skip()
                    await ctx.edit('<:nikosleepy:1027492467337080872> `Song Skipped.`', embeds = [], components = [])
                    
                    await Database.delete_item(ctx, 'Music')
                    break
            
            if player.current != song_ or music_stopped:
                await ctx.edit('<:nikosleepy:1027492467337080872> `Song Ended.`', embeds = [], components = [])
                return
            
            if db['player_id'] != str(player_id):
                await ctx.edit('<:nikosleepy:1027492467337080872> `Player Moved.`', embeds = [], components = [])
                return
            
            if not player.paused and player.is_playing:
                try:
                    funny_embed = await self.GenerateEmbed(self, player.current.identifier, player, False, spotifydata=spotify)
                    funny_embed.set_author(name = message)
                    await ctx.edit(db['niko'], embeds = funny_embed, components = buttons)
                except:
                    pass
                
        return
    
def setup(client):
    Music(client)