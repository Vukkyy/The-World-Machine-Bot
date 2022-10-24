import exts.music as music

async def update(ctx, player):
    await music.update_player(ctx, player)