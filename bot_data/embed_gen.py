from interactions import *

async def fancy_send(ctx : CommandContext, content : str, ephemeral = False, color = 0x8b00cc, components = []):
    e = Embed(
        description = content,
        color = color
    )
    
    return await ctx.send(embeds = e, ephemeral = ephemeral, components = components)