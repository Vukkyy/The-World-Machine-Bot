import interactions

guild_id = 1017479547664482444

async def EarnBadge(bot : interactions.Client, ctx : interactions.CommandContext, badge_id : str, badge_name : str, badge_emoji : int, badge_description : str):
    await ctx.send(f'**You unlocked a stamp!**\n\'{badge_name}\' <:badge_name:{str(badge_emoji)} ({badge_description})', ephemeral = True)