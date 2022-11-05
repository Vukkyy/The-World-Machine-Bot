import interactions
import os
from pathlib import Path
import json
import asyncio
from interactions.ext.lavalink import VoiceClient
from interactions.ext.wait_for import wait_for_component
from humanfriendly import format_timespan

class Transmissions(interactions.Extension):
    def __init__(self, client):
        self.client: VoiceClient = client
        print("Loaded Transmissions")
        with open('Transmissions/connected.userphone', 'w') as f:
            f.write(json.dumps({"connection_one" : 0, "connection_two" : 0, "hidden" : False}))
        with open('Transmissions/transmissions.userphone', 'w') as f:
            f.write('')
        with open('Transmissions/update.userphone', 'w') as f:
            f.write('0')
        
    @interactions.extension_command(
        name = 'transmit',
        description = 'Transmit (talk to) other servers using The World Machine!',
        options = [
            interactions.Option(
                type = interactions.OptionType.STRING,
                name = 'hide',
                description = 'Enabling this allows you to hide your name and profile picture from the other server.',
                required=True,
                choices = [
                    interactions.Choice(
                        name = 'Do not Hide',
                        value = 'f'
                    ),
                    interactions.Choice(
                        name = 'Hide',
                        value= 'there are imposters among us 🗿'
                    )
                ]
            )
        ]
    )
    async def transmit(self, ctx : interactions.CommandContext, hide : str = 'f'):
        
        if hide == 'f':
            hide = False
        else:
            hide = True
        
        channel_ids = []
        
        can_send = []
        
        with open('Transmissions/transmissions.userphone', 'r') as f:
            channel_ids = f.readlines()
        
        with open('Transmissions/update.userphone', 'r') as f:
            can_send = f.read().split('>')
        
        if str(ctx.guild_id) in can_send:
            await ctx.send('This server is already transmitting to/finding another server!', ephemeral=True)
            return
        
        can_send = []
        
        with open('Transmissions/update.userphone', 'r') as f:
            can_send = f.read().split('>')
            
        can_send.append(str(ctx.guild_id))
        
        with open('Transmissions/update.userphone', 'w') as f:
            f.write('>'.join(can_send))
        
        if (len(channel_ids) == 0):
            channel_ids.append(str(ctx.channel.id) + f'>{str(hide)}')
            
            with open('Transmissions/transmissions.userphone', 'w') as f:
                f.write('\n'.join(channel_ids))
                
            msg = await ctx.send('Waiting for someone to connect... <a:loading:1026539890382483576>')
            
            await self.client.change_presence(
                interactions.ClientPresence(
                        status=interactions.StatusType.ONLINE,
                        activities=[
                            interactions.PresenceActivity(
                                name="a server transmitting!",
                                type=interactions.PresenceActivityType.WATCHING)
                        ]
                    )
                )
            
            tries = 0
            limit = 20
            
            while True:
                
                if tries >= limit:
                    
                    can_send = []
        
                    with open('Transmissions/update.userphone', 'r') as f:
                        can_send = f.read().split('>')
                
                    can_send.remove(str(ctx.guild.id))
                    
                    with open('Transmissions/update.userphone', 'w') as f:
                        f.write('>'.join(can_send))
                    
                    await msg.edit('Looks like no one wants to talk... <:twmcrying:1023573454307463338>')
                    
                    await self.client.change_presence(
                    interactions.ClientPresence(
                        status=interactions.StatusType.ONLINE,
                        activities=[
                            interactions.PresenceActivity(
                                name="On Little Cat Feet",
                                type=interactions.PresenceActivityType.LISTENING)
                        ]))
                    
                    del channel_ids[0]
                    with open('Transmissions/transmissions.userphone', 'w') as f:
                        f.write('\n'.join(channel_ids))
                    return
                
                with open('Transmissions/connected.userphone', 'r') as f:
                    channel_ids = f.read().split('>')
                    
                update = False
                hidden = False
                
                for channel_id in channel_ids:
                    channel_id = json.loads(channel_id)
                    if (int(channel_id['connection_one']) == int(ctx.channel_id)):
                        hidden = channel_id['hidden']
                        update = True
                        break
                        
                if (update == True):
                    break
                    
                await asyncio.sleep(1)
                tries += 1
                
            await self.client.change_presence(
                    interactions.ClientPresence(
                        status=interactions.StatusType.ONLINE,
                        activities=[
                            interactions.PresenceActivity(
                                name="On Little Cat Feet",
                                type=interactions.PresenceActivityType.LISTENING)
                        ]))
            
            if hidden and not hide:
                await get_call(self, ctx, msg, True)
            else:
                await get_call(self, ctx, msg)
                
            return

        json_list = []
        
        with open('Transmissions/connected.userphone', 'r') as f:
            json_list = f.read().split('>')
        
        connection_ = channel_ids[0].split('>')
        
        connection_one = int(connection_[0]) # Converts user id to an integer
        
        hidden = eval(connection_[1])  # Converts string boolean to a python bool
        
        del channel_ids[0]
        
        json_list.append(json.dumps({'connection_one': connection_one, 'connection_two' : int(ctx.channel.id), "hidden" : hidden}))
        
        with open('Transmissions/transmissions.userphone', 'w') as f:
            f.write('\n'.join(channel_ids))
            
            
        with open('Transmissions/connected.userphone', 'w') as f:
            f.write('>'.join(json_list))
            
        msg = await ctx.send('Connecting... <a:loading:1026539890382483576>')
        
        
        if hidden:
            await get_call(self, ctx, msg, True)
        else:
            await get_call(self, ctx, msg)
        

async def get_call(self, ctx : interactions.CommandContext, message : interactions.Message, hidden : bool = False):
    
    button = interactions.Button(
                label = 'Disconnect',
                style = interactions.ButtonStyle.PRIMARY,
                custom_id= f'disconnect {int(ctx.guild_id)}'
            )
    print('connected')
    
    msg = await message.edit('Connection established! Say hello! <:twmpancakes:1023573458296246333>', components = button)
    
    if (hidden):
        await msg.reply('Other server has opted to stay hidden, both servers will not have their name or profile picture shown.')

    current_connection = []
    json_list = []
        
    with open('Transmissions/connected.userphone', 'r') as f:
        current_connection = f.read().split('>')
        
    for connection in current_connection:
        json_list.append(json.loads(connection))
        
    
    async def check(ctx):
        return True
    
    timer = 180
    
    can_send = []
        
    with open('Transmissions/update.userphone', 'r') as f:
        can_send = f.read().split('>')
    
    while True:
        task = asyncio.create_task(wait_for_component(self.client, components=button, check=check))
        while True:
            done, pending = await asyncio.wait({task}, timeout=1)
            
            if (timer == 0):
                i = 0
                current = {}
                for data in json_list:
                    if int(data['connection_one']) == int(ctx.channel.id):
                        current = 'connection_one'
                        break
                    elif int(data['connection_two']) == int(ctx.channel.id):
                        current = 'connection_two'
                        break
                    i += 1
                
                await disconnect(self, ctx, current, i, 0)
                return
            
            if not done:
                timer -= 1
                if (timer % 5 == 0):
                    await message.edit(f'Connection established! Say hello! *({format_timespan(timer)} left before disconnect!)* <:twmpancakes:1023573458296246333>', components = button)
                
                if (timer == 30):
                    await ctx.send('Only 30 seconds left for this transmission! <:twmclosedeyes:1023573452944322560>')
                
                with open('Transmissions/connected.userphone', 'r') as f:
                    channel_ids = f.read().split('>')
                is_connected = False
                
                for channel_id in channel_ids:
                    channel_id = json.loads(channel_id)
                    if (int(channel_id['connection_one']) == int(ctx.channel_id)):
                        is_connected = True
                    elif(int(channel_id['connection_two']) == int(ctx.channel_id)):
                        is_connected = True
                
                if is_connected:
                    continue
                else:
                    with open('Transmissions/update.userphone', 'r') as f:
                        can_send = f.read().split('>')
            
                    can_send.remove(str(ctx.guild.id))
                    
                    with open('Transmissions/update.userphone', 'w') as f:
                        f.write('>'.join(can_send))
                        
                    print('connection broken')
                    return # Automatically disconnect if connection isn't in list.
                
            button_ctx = task.result()
            if (button_ctx.data.custom_id == f'disconnect {int(ctx.guild_id)}'):
                i = 0
                current = {}
                for data in json_list:
                    if int(data['connection_one']) == int(ctx.channel.id):
                        current = 'connection_one'
                        break
                    elif int(data['connection_two']) == int(ctx.channel.id):
                        current = 'connection_two'
                        break
                    i += 1
                
                await disconnect(self, button_ctx, current, i, 1)
                return
            break
        
async def disconnect(self, ctx : interactions.CommandContext, connection : str, index : int, reason : int):
    
    current_connection = []
    
    try:
        with open('Transmissions/connected.userphone', 'r') as f:
            current_connection = f.read().split('>')
            
        json_ = json.loads(current_connection[index])
        
        other_connection = 0
        
        if connection == 'connection_one':
            other_connection = int(json_['connection_two'])
        else:
            other_connection = int(json_['connection_one'])
            
        del current_connection[index]
        
        with open('Transmissions/connected.userphone', 'w') as f:
            f.write('>'.join(current_connection))
        
        channel = await interactions.get(self.client, interactions.Channel, object_id = other_connection)
        
        print(other_connection)
        print(ctx.channel.id)
        
        can_send = []
        
        with open('Transmissions/update.userphone', 'r') as f:
            can_send = f.read().split('>')

        can_send = list(filter((str(ctx.guild.id)).__ne__, can_send))
        
        with open('Transmissions/update.userphone', 'w') as f:
            f.write('>'.join(can_send))
        
        if reason == 1:
            await channel.send('The other server you\'re transmitting to disconnected... Sorry! <:twmcrying:1023573454307463338>')
            await ctx.send('Successfully disconnected from the other server.')
        else:
            await channel.send('Your transmission time is up... Sorry! <:twmcrying:1023573454307463338>')
            await ctx.send('Your transmission time is up... Sorry! <:twmcrying:1023573454307463338>')
    except:
        pass
        # I don't know how to handle this exception
    
    
    
def setup(client):
    Transmissions(client)