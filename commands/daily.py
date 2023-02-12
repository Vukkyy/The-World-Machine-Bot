from interactions import *
from bot_data.error_handler import on_error
from bot_data.embed_gen import fancy_send
import bot_data.database_manager as db_

from interactions.ext.database.database import Database

from datetime import datetime, timedelta

import random

class Command(Extension):
    
    @extension_listener
    async def on_start(self):
        default_data = {"daily_wool_hit": False, "last_reset_time": "2023-02-08 00:00:00", "daily_wool_count" : self.current_limit}
        await Database.create_database(
                name = 'daily_wool',
                type = Database.DatabaseType.USER,
                default_data = default_data
            )
        
        await Database.create_database(
            name = 'daily_wool',
            type = Database.DatabaseType.USER,
            default_data = default_data
        )
        
    current_limit = 0
    
    wool_finds = [
        'You sheared some sheep for wool.',
        'You dug around a trashcan and found some wool.',
        'You tore up your old bedsheets for some wool.',
        'You summoned the devil and asked for some wool.',
        'You won a videogame tournament and won wool.',
        'You got the world record speedrun for a game and won wool.',
        "You robbed a wool store and got caught by the cops, now you're serving time for wool.",
        "You sold your soul for wool, now you're cursed forever.",
        "You stole your neighbor's wool.",
        "You vandalized a museum for wool. You're a menace to society.",
        "You extorted a small business for wool. You should be ashamed."
    ]
    
    @extension_command(description = 'Grab your daily wool.')
    async def daily(self, ctx : CommandContext):
        
        db = await Database.get_item(uid = ctx, database = 'daily_wool')
        last_reset_time = datetime.strptime(db.get("last_reset_time"), '%Y-%m-%d %H:%M:%S')
        limit_hit = db.get("daily_wool_hit", False)
        now = datetime.utcnow()
        reset_time = datetime.combine(now.date(), datetime.min.time()) + timedelta(days=1)
        reset_time = reset_time.replace(hour=0, minute=0, second=0, microsecond=0)

        if (last_reset_time is not None and last_reset_time > reset_time):
            return await fancy_send(ctx, "[ You've already collected your daily wool for today. Don't be greedy. ]", ephemeral = True, color = 0xff171d)

        # reset the limit if it is a new day
        if not last_reset_time or last_reset_time < reset_time:
            await Database.set_item(uid=ctx, database='daily_wool', data={"daily_wool_hit": False, "last_reset_time": reset_time.strftime("%Y-%m-%d %H:%M:%S"), "daily_wool_count": self.current_limit})
        else:
            limit = db.get("daily_wool_count", self.current_limit)
            if limit <= 0:
                await Database.set_item(uid=ctx, database='daily_wool', data={"daily_wool_hit": True})
                return await fancy_send(ctx, "[ You've already collected your daily wool for today. Don't be greedy. ]", ephemeral = True, color = 0xff171d)
            else:
                await Database.set_item(uid=ctx, database='daily_wool', data={"daily_wool_count": limit - 1})
        
        random.shuffle(self.wool_finds)
        
        response = self.wool_finds[0]
        
        coins = await db_.GetDatabase(int(ctx.author.id), 'ram', {"uid" : int(ctx.author.id), "coins" : 0})
        
        amount = random.randint(10, 50)
        
        await db_.SetDatabase(int(ctx.author.id), 'ram', 'coins', coins['coins'] + amount)
        
        await fancy_send(ctx, f'*{response}* Found **{amount}** <:wool:1044668364422918176>.')
        pass
    
    @daily.error
    async def error(self, ctx : CommandContext, error):
        
        embed = await on_error(error)
        
        await ctx.send(embeds=embed)
        
def setup(client):
    Command(client)