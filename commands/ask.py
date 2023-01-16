from interactions import *
import generate_text
import dialogue_generator
import aiohttp
import aiofiles
from error_handler import on_error
from interactions.ext.database.database import Database

import textwrap

import nltk
nltk.download('punkt')

import pandas as pd
from nltk import word_tokenize
from nltk.stem.snowball import SnowballStemmer
import requests

from LeXmo import LeXmo

class Command(Extension):
    
    @extension_listener
    async def on_start(self):
        await Database.create_database('the bot remembers', Database.DatabaseType.USER, {'last_thing_said' : 'Hello.'}, True)
    
    @extension_command(description = 'Ask The World Machine a question.')
    @option(description='The question to ask!')
    async def ask(self, ctx : CommandContext, question : str):
        
        c = question[len(question) - 1]
        
        q = question + '?'
        
        embed = Embed(color=0x7d00b8)
        
        embed.set_author(
            name = f'"{question}"',
            icon_url= ctx.author.user.avatar_url
        )
        
        # * first stage...
        embed.description = '[ Thinking about what you have asked... <a:loading:1026539890382483576> ]'
        
        msg = await ctx.send(embeds = embed)
        
        result_ : str = await generate_text.GenerateText(q, ctx.author.user.username, 'gay gay homosexual gay')
        result_ = result_.strip()
        
        # * second stage...
        embed.description = '[ Judging your decisions... <a:loading:1026539890382483576> ]'
        
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
        embed.description = '[ Final decisions... <a:loading:1026539890382483576> ]'
        
        await msg.edit(embeds=embed)
        
        result_ = result_.replace('\n', ' ')
        
        n = 160
        r = "#".join(textwrap.wrap(result_, n))
        finalresult_ = r.split('#')
        
        embed.description = ''
        
        await msg.edit(embeds=embed)
        
        for text in finalresult_:
        
            await dialogue_generator.test(f'[ {text} ]', twm)
            
            file = File('Images/pil_text.png', description=text)
            
            await ctx.channel.send(files = file)
        
    @ask.error
    async def you_fucked_up_gpt_three(self, ctx : CommandContext, error):
        
        embed = await on_error(error)
        
        await ctx.send(embeds= embed)
        
def setup(client):
    Command(client)