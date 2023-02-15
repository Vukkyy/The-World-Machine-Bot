from interactions import *

async def fancy_send(ctx : CommandContext, content : str, ephemeral = False, color = 0x8b00cc, components = [], channel = False):
    e = Embed(
        description = content,
        color = color
    )
    
    if channel:
        return await ctx.channel.send(embeds = e, components = components)
    else:
        return await ctx.send(embeds = e, ephemeral = ephemeral, components = components)