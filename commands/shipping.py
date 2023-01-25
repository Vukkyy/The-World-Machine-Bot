from interactions import *
from bot_data.error_handler import on_error
import random

class Command(Extension):
    
    @extension_command(description = 'Ship two people together.')
    @option(description='The first person.')
    @option(description='And the second.')
    async def ship(self, ctx : CommandContext, first : str, second : str):
        
        first_raw = first
        second_raw = second
        
        if '<@' in first:
            a = first.split('@')
            b = a[1].split('>')
            
            first = await get(self.client, User, object_id= int(b[0]))
            first = first.username
        if '<@' in second:
            a = second.split('@')
            b = a[1].split('>')
            
            second = await get(self.client, User, object_id= int(b[0]))
            second = second.username
        
        first_name = first[0:len(first)//2]
        second_name = second[len(second)//2 if len(second)%2 == 0 else ((len(second)//2)+1):]
        
        name = first_name + second_name
        
        random.seed(first+second)
        
        number = random.uniform(1, 10)
        
        percentage = round((number / 10) * 100, 2)
        
        emoji = '💖'
        
        if percentage == 100:
            emoji = '💛'
        if percentage < 100:
            emoji = '💖'
        if percentage < 70:
            emoji = '❤'
        if percentage < 50:
            emoji = '❣'
        if percentage < 30:
            emoji = '❓'
        if percentage < 10:
            emoji = '💔'
        
        l_length = list("🤍🤍🤍🤍🤍")
            
        calc_length = round((percentage / 100) * len(l_length))
        
        print(calc_length)
        
        i=0
        for heart in l_length:
            if i < calc_length:
                l_length[i] = '❤'
            i += 1
            
        length = "".join(l_length)
        
        embed = Embed(
            title = name,
            description=f'~ **{first_raw}** 💞 **{second_raw}** ~\n\n**Compatibility:** *{percentage}%* {emoji}\n{length}',
            color=0xd72d42
        )
        
        await ctx.send(embeds=embed)
        pass
    
    @ship.error
    async def error(self, ctx : CommandContext, error):
        
        embed = await on_error(error)
        
        await ctx.send(embeds=embed)
        
def setup(client):
    Command(client)