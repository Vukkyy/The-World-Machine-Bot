from interactions import *
import lavalink
from interactions.ext.lavalink import Lavalink
import custom_source
import lyricsgenius
import os
import random
import music_utilities as music_

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
        music_.setup_(client)

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
    async def on_voice_state_update(self, before: VoiceState, after: VoiceState):
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
        
        await ctx.send('Unfortunately this command is a work in progress. Please try again in the future.', ephemeral = True)
        return

        voice: VoiceState = ctx.author.voice_state
        
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
            
async def update_player(ctx, player):
    await music_.ShowPlayer(ctx, player, True, True)

def setup(client):
    Music(client)