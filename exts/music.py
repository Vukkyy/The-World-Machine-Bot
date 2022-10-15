import interactions
import lavalink
from interactions.ext.lavalink import VoiceClient, VoiceState, listener, Player
import music_utilities as music_
import custom_source

class Music(interactions.Extension):
    def __init__(self, client):
        self.client: VoiceClient = client
        music_.setup_(client)

    @listener()
    async def on_track_start(self, event: lavalink.TrackStartEvent):
        is_quiet = event.player.fetch(f'isquiet {event.player.guild_id}')
        
        if (not is_quiet):
            event.player.set_repeat(False)
            
            ctx = event.player.fetch(f'channel {event.player.guild_id}')

            event.player.store(f'currently quiet {event.player.guild_id}', False)

            index = 0
            
            for song in event.player.queue:
                if song.title == 'OneShot OST - Library Nap Extended':
                    del event.player.queue[index]
                index += 1
                          
            await music_.ShowPlayer(ctx, event.player, False)

    @listener()
    async def on_queue_end(self, event: lavalink.QueueEndEvent):
        ctx = event.player.fetch(f'channel {event.player.guild_id}')
        embed = interactions.Embed(
            title = 'End of Queue',
            description = 'Add more songs using /music play.',
            footer = interactions.EmbedFooter(text = 'Playing some quiet OneShot music in the meantime :)')
        )
        await ctx.channel.send("", embeds= embed)

        results = await event.player.node.get_tracks(f"https://www.youtube.com/watch?v=TqMo9HwiNOo")
        track = lavalink.AudioTrack(results["tracks"][0], int(ctx.author.id))

        event.player.set_repeat(True)

        event.player.store(f'isquiet {event.player.guild_id}', True)
        event.player.store(f'currently quiet {ctx.guild_id}', True)

        print('Playing ambeiance (i cannot spell)')


        await event.player.play(track, volume = 8)

    @listener()
    async def disconnected(self, event : lavalink.NodeDisconnectedEvent):
        self.client.lavalink_client.add_node(
            host = '51.161.130.134',
            port = 10333,
            password = 'youshallnotpass',
            region = "eu"
        )

        ctx = event.player.fetch(f'channel {event.player.guild_id}')

        await ctx.send("An Unexpected error occurred. Skipping to the next track.")
        await event.player.play()

        

    @interactions.extension_listener()
    async def on_start(self):
        print('Loading Music Module')
        self.client.lavalink_client.add_node(
            host = '51.161.130.134',
            port = 10333,
            password = 'youshallnotpass',
            region = "eu"
        ) # Woah, neat! Free Lavalink!
        

    @interactions.extension_listener()
    async def on_voice_state_update(self, before: VoiceState, after: VoiceState):
        """
        Disconnect if bot is alone
        """
        if before and not after.joined:
            voice_states = self.client.get_channel_voice_states(before.channel_id)
            if len(voice_states) == 1 and voice_states[0].user_id == self.client.me.id:
                await self.client.disconnect(before.guild_id)

    @interactions.extension_command(
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
            ),

            interactions.Option(
                name = "stop",
                description = "Stop the music player.",
                type = interactions.OptionType.SUB_COMMAND
            ),
        ]
    )   
    async def music_(self, ctx: interactions.CommandContext, sub_command: str, search: str = "", fromindex: int = 0):

        voice: VoiceState = ctx.author.voice
        
        if (not voice or not voice.joined):
            await ctx.send("Sorry! You need to be in a voice channel to use this command.", ephemeral = True)
            return
    
        if (voice.guild_id != ctx.guild_id):
            await ctx.send("Sorry! You need to be in a voice channel to use this command.", ephemeral = True)
            return
        
        #await ctx.defer()

        player: Player  # Typehint player variable to see their methods

        if (player := ctx.guild.player) is None:
            player = await voice.connect()
        
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
                        tracks = await player.search_youtube(video)
                        track = tracks[0]
                        player.add(requester=int(ctx.author.id), track=track)

                        successful += 1
                    except:
                        pass
                    if (successful % 2 == 0):
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
                cool = interactions.Embed(
                    title = f"**Added:** [{track.title}] to queue.",
                    thumbnail = interactions.EmbedImageStruct( url = f"https://i3.ytimg.com/vi/{track.identifier}/maxresdefault.jpg", height = 720, width = 1280),
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

def setup(client):
    Music(client)