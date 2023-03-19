from interactions import *
import bot_data.generate_text as generate_text
import bot_data.dialogue_generator as dialogue_generator
import aiohttp
import aiofiles
from bot_data.error_handler import on_error
from interactions.ext.database.database import Database
from uuid import uuid4
import os

import textwrap

import nltk

import pandas as pd
from nltk import word_tokenize
from nltk.stem.snowball import SnowballStemmer
import requests

from LeXmo import LeXmo
from datetime import datetime, timedelta

from bot_data.embed_gen import fancy_send

class Command(Extension):
    
    @extension_listener
    async def on_start(self):
        default_data = {"daily_limit_hit": False, "last_reset_time": "2023-02-08 00:00:00", "daily_limit_count" : self.current_limit}
        await Database.create_database(
                name = 'daily_limit',
                type = Database.DatabaseType.USER,
                default_data = default_data
            )
        
    current_limit = 15
    
    limit_message = "[ Daily limit reached. Please try asking questions tomorrow. ]"

    async def ask(self, ctx : CommandContext, question : str):
        
        limit = 0
        
        question = question.replace('<@1015629604536463421>', 'The World Machine')
        
        db = await Database.get_item(uid = ctx, database = 'daily_limit')
        last_reset_time = datetime.strptime(db.get("last_reset_time"), '%Y-%m-%d %H:%M:%S')
        limit_hit = db.get("daily_limit_hit", False)
        now = datetime.utcnow()
        reset_time = datetime.combine(now.date(), datetime.min.time()) + timedelta(days=1)
        reset_time = reset_time.replace(hour=0, minute=0, second=0, microsecond=0)

        if (last_reset_time is not None and last_reset_time > reset_time):
            return await fancy_send(ctx, self.limit_message, ephemeral = True, color = 0xff171d, message = True)

        # reset the limit if it is a new day
        if not last_reset_time or last_reset_time < reset_time:
            await Database.set_item(uid=ctx, database='daily_limit', data={"daily_limit_hit": False, "last_reset_time": reset_time.strftime("%Y-%m-%d %H:%M:%S"), "daily_limit_count": self.current_limit})
        else:
            limit = db.get("daily_limit_count", self.current_limit)
            if limit <= 0:
                await Database.set_item(uid=ctx, database='daily_limit', data={"daily_limit_hit": True})
                return await fancy_send(ctx, self.limit_message, ephemeral = True, color = 0xff171d, message = True)
            else:
                await Database.set_item(uid=ctx, database='daily_limit', data={"daily_limit_count": limit - 1})
        
        limit = db.get("daily_limit_count", self.current_limit)

        question = question.strip('?')
        
        q = question + '?'
        
        embed = Embed(color=0x7d00b8)
        
        # * first stage...
        embed.description = '[ Generating my thoughts... <a:loading:1026539890382483576> ]'
        embed.set_footer(text=f'[ You have {limit - 1} question(s) left to ask for today. ]')
        
        msg = await ctx.reply(embeds = embed)
        
        result_ : str = await generate_text.GenerateText(q, ctx.author.username, 'gay gay homosexual gay')
        result_ = result_.strip()
        result_ = result_.strip('"')
        
        print(result_)
        
        # * second stage...
        embed.description = '[ Thinking... <a:loading:1026539890382483576> ]'
        
        await msg.edit(embeds=embed)
        
        result = LeXmo.LeXmo(result_)
        result.pop('text', None)
        
        
        emotion = max(result, key=result.get)
        
        
        twm = ''
        
        if emotion == 'anger':
            twm = 'https://cdn.discordapp.com/emojis/1023573452944322560.webp?size=96&quality=lossless'
        if emotion == 'anticipation':
            twm = 'https://cdn.discordapp.com/emojis/1023573456664662066.webp?size=96&quality=lossless'
        if emotion == 'disgust':
            twm = 'https://cdn.discordapp.com/emojis/1023573452944322560.webp?size=96&quality=lossless'
        if emotion == 'fear':
            twm = 'https://cdn.discordapp.com/emojis/1023573454307463338.webp?size=96&quality=lossless'
        if emotion == 'joy':
            twm = 'https://cdn.discordapp.com/emojis/1023573458296246333.webp?size=96&quality=lossless'
        if emotion == 'negative':
            twm = 'https://cdn.discordapp.com/emojis/1023573456664662066.webp?size=96&quality=lossless'
        if emotion == 'positive':
            twm = 'https://cdn.discordapp.com/emojis/1023573459676172359.webp?size=96&quality=lossless'
        if emotion == 'sadness':
            twm = 'https://cdn.discordapp.com/emojis/1023573454307463338.webp?size=96&quality=lossless'
        if emotion == 'surprise':
            twm = 'https://cdn.discordapp.com/emojis/1023573458296246333.webp?size=96&quality=lossless'
        if emotion == 'trust':
            twm = 'https://cdn.discordapp.com/emojis/1023573459676172359.webp?size=96&quality=lossless'
        
        # * third stage...
        
        embed.description = f'```{result_}```'
        embed.set_thumbnail(url=twm)

        await msg.edit(embeds=embed)
        
def setup(client):
    Command(client)