from interactions import *
from error_handler import on_error
import asyncio
import humanfriendly
import uuid

class Command(Extension):
    
    initial_connected_server = None
    
    next_connected_server = None
    
    @extension_command()
    async def transmit(self, ctx : CommandContext):
        pass
    
    @transmit.subcommand(description= 'Transmit to another server.')
    async def connect(self, ctx: CommandContext):
        
        if Command.initial_connected_server == None:
            Command.initial_connected_server = {"server_id" : int(ctx.guild.id), "channel_id" : int(ctx.channel_id)}
            
            embed = await Command.embed_manager(self, 'initial_connection')
            
            cancel = Button(
                style=ButtonStyle.DANGER,
                label='Cancel',
                custom_id='haha cancel go brrr'
            )
            
            msg = await ctx.send(embeds = embed, components = cancel)
            
            cancel_timer = 50
            
            async def check(ctx_):
                if ctx.author.id == ctx_.author.id:
                    return True
                else:
                    await ctx_.send(f'[ Only the initiator of this transmission (<@{int(ctx.author.id)}>) can cancel it! ]', ephemeral = True)
                    return False
            
            task = asyncio.create_task(self.client.wait_for_component(cancel, check=check))
            
            while (Command.next_connected_server == None):
                done, result = await asyncio.wait({task}, timeout=1)
                
                if not done:
                    cancel_timer -= 1
                    
                    embed.set_footer(text = f'[ This transmission will be automatically cancelled in {cancel_timer} seconds. ]')
                    
                    await msg.edit(embeds=embed, components = cancel)
                    
                    if cancel_timer == 0:
                        Command.initial_connected_server = None
                        Command.next_connected_server = None
                        
                        embed = Command.cancel_embed_manager(self, 'timeout', ctx)
                        
                        await msg.edit(embeds=embed, components = [])
                        return
                    
                    continue
                
                Command.initial_connected_server = None
                Command.next_connected_server = None
                
                button_ctx = task.result()
                
                embed = Command.cancel_embed_manager(self, 'manual', int(button_ctx.author.id))
                        
                await msg.edit(embeds=embed, components = [])
                return
            
            print('poggers')
            
            await Command.on_connection_first(self, int(ctx.author.id), msg)
            return
        
        if Command.initial_connected_server['server_id'] == int(ctx.guild_id):
            await ctx.send('[ You are already transmitting! ]', ephemeral = True)
            return
            
        if Command.next_connected_server == None:
            
            Command.next_connected_server = {"server_id" : int(ctx.guild.id), "channel_id" : int(ctx.channel_id)}
            
            embed = await Command.embed_manager(self, 'initial_connection')
        
            msg = await ctx.send(embeds = embed)
            
            await Command.on_connection_second(self, int(ctx.author.id), msg)
            return
        
        if Command.next_connected_server['server_id'] == int(ctx.guild_id):
            await ctx.send('[ You are already transmitting! ]', ephemeral = True)
            return
        
        await ctx.send('[ Two servers are already transmitting! ]', ephemeral=True)
        return
            
    async def on_connection_first(self, id_, msg : Message):
        
        btn_id = uuid.uuid4()
        
        disconnect = Button(
            style=ButtonStyle.DANGER,
            label='Disconnect',
            custom_id=str(btn_id)
        )
        
        server_name = await get(self.client, Guild, object_id=Command.next_connected_server['server_id'])
        
        async def check(ctx_):
            if id_ == int(ctx_.author.id):
                return True
            else:
                await ctx_.send(f'[ Only the initiator of this transmission (<@{id_}>) can cancel it! ]', ephemeral = True)
                return False
        
        task = asyncio.create_task(self.client.wait_for_component(disconnect, check=check))       
        
        disconnect_timer = 600
        
        embed = await Command.embed_manager(self, 'connected')
        embed.description = f'[ Currently connected to **{server_name.name}**! ]'
        
        while Command.initial_connected_server != None:
            done, _ = await asyncio.wait({task}, timeout=1)
            
            if not done:
                
                time = humanfriendly.format_timespan(disconnect_timer)
                
                embed.set_footer(text=f'Transmission will end in {time}.')
                
                await msg.edit(embeds=embed, components=disconnect)
                
                disconnect_timer -= 1
                
                if disconnect_timer == 30:
                    await msg.reply('[ Transmission will end in 30 seconds. ]')
                
                if disconnect_timer == 0:
                    embed = Command.cancel_embed_manager(self, 'transmittime')
                    
                    Command.initial_connected_server = None
                    Command.next_connected_server = None
                    
                    await msg.edit(embeds = embed, components=[])
                    await msg.reply(embeds = embed)
                    return
                
                continue # * Important
            
            embed = Command.cancel_embed_manager(self, 'manual', id_)
            
            await msg.edit(embeds = embed, components=[])
            await msg.reply(embeds= embed)
            
            Command.initial_connected_server = None
            Command.next_connected_server = None
            
            return

        embed = Command.cancel_embed_manager(self, 'server')
            
        await msg.edit(embeds = embed, components=[])
        await msg.reply(embeds= embed)
        
        return
    
    async def on_connection_second(self, id_, msg : Message):
        
        btn_id = uuid.uuid4()
        
        disconnect = Button(
            style=ButtonStyle.DANGER,
            label='Disconnect',
            custom_id=str(btn_id)
        )
        
        server_name = await get(self.client, Guild, object_id=Command.initial_connected_server['server_id'])
        
        async def check(ctx_):
            if id_ == int(ctx_.author.id):
                return True
            else:
                await ctx_.send(f'[ Only the initiator of this transmission (<@{id_}>) can cancel it! ]', ephemeral = True)
                return False
        
        task = asyncio.create_task(self.client.wait_for_component(disconnect, check=check))       
        
        disconnect_timer = 600
        
        embed = await Command.embed_manager(self, 'connected')
        embed.description = f'[ Currently connected to **{server_name.name}**! ]'
        
        await msg.edit(embeds=embed, components=disconnect)
        
        while Command.next_connected_server != None:
            done, _ = await asyncio.wait({task}, timeout=1)
            
            if not done:
                
                time = humanfriendly.format_timespan(disconnect_timer)
                
                embed.set_footer(text=f'[Transmission will end in {time}.')
                
                await msg.edit(embeds=embed, components=disconnect)
                
                disconnect_timer -= 1
                
                if disconnect_timer == 30:
                    await msg.reply('[ Transmission will end in 30 seconds. ]')
                
                if disconnect_timer == 0:
                    embed = Command.cancel_embed_manager(self, 'transmittime')
                    
                    Command.initial_connected_server = None
                    Command.next_connected_server = None
                    
                    await msg.edit(embeds = embed, components=[])
                    await msg.reply(embeds = embed)
                    return
                
                continue # * Important
            
            embed = Command.cancel_embed_manager(self, 'manual', id_)
            
            await msg.edit(embeds = embed, components=[])
            await msg.reply(embeds= embed)
            
            Command.initial_connected_server = None
            Command.next_connected_server = None
            
            return
        
        embed = Command.cancel_embed_manager(self, 'server')
            
        await msg.edit(embeds = embed, components=[])
        await msg.reply(embeds= embed)
        
        return
            
    @extension_listener
    async def on_message_create(self, message : Message):
        if message.author.id == 1015629604536463421 or message.author.id == 1028058097383641118:
            return
        
        if Command.next_connected_server != None:
            
            first_server = Command.initial_connected_server
            second_server = Command.next_connected_server
            
            channel : Channel = await message.get_channel()
            
            can_pass = False
            other_connection = None

            if first_server['channel_id'] == channel.id:
                can_pass = True
                other_connection = await get(self.client, Channel, object_id = second_server['channel_id'])
                
            if second_server['channel_id'] == channel.id:
                can_pass = True
                other_connection = await get(self.client, Channel, object_id = first_server['channel_id'])
                
            if can_pass:
                
                embed = Command.message_manager(self, message)
                
                async with other_connection.typing:

                    await asyncio.sleep(1)
                    
                    await other_connection.send(embeds = embed)
    
    def message_manager(self, message : Message):
        author = message.author
        
        embed = Embed(
            color=0x36393f,
            description=message.content,
        )
        
        if len(message.attachments) > 0:
            image = message.attachments[0].url
            embed.image = EmbedImageStruct(url=image)
            
            if '.mp4' in image or '.mov' in image:
                embed.description = f'{message.content}\n**[Video]({image})**'
        
        embed.set_author(name = author.username, icon_url = author.avatar_url)
        
        return embed
                
    @transmit.error
    async def error(self, ctx : CommandContext, error):
        
        embed = await on_error(error)
        
        await ctx.send(embeds=embed)
        
    def cancel_embed_manager(self, cancel_reason, button_ctx = None):
        if cancel_reason == 'timeout':
            return Embed(
                title = 'Transmission Cancelled.',
                description = '[ Looks like no one wants to talk... ] <:twmcrying:1023573454307463338>',
                color= 0xff1a1a
            )
            
        if cancel_reason == 'manual':
            return Embed(
                title = 'Transmission Cancelled.',
                description = f'<@{button_ctx}> cancelled the transmission.',
                color= 0xff1a1a
            )
            
        if cancel_reason == 'server':
            return Embed(
                title = 'Transmission Cancelled.',
                description = '[ The other server cancelled the transmission. ] <:twmcrying:1023573454307463338>',
                color= 0xff1a1a
            )
            
        if cancel_reason == 'transmittime':
            return Embed(
                title = 'Transmission Ended.',
                description = '[ You ran out of transmission time. ]',
                color= 0xff1a1a
            )
        
    async def embed_manager(self, embed_type : str):
        if embed_type == 'initial_connection':
            return Embed(
                title = 'Transmission Starting!',
                description = 'Waiting for a connection... <a:loading:1026539890382483576>',
                color= 0x933397
            )
            
        if embed_type == 'connected':
            
            return Embed(
                title = 'Connected!',
                color= 0x47ff1a
            )
        
def setup(client):
    Command(client)