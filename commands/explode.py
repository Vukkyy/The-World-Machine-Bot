from interactions import *
from bot_data.error_handler import on_error
import Badges.stamp_system as stamps
import random
import datetime

class Command(Extension):
    
    # ! Needs to be changed. !
    
    explosion_image = [
        'https://st.depositphotos.com/1001877/4912/i/600/depositphotos_49123283-stock-photo-light-bulb-exploding-concept-of.jpg',
        'https://st4.depositphotos.com/6588418/39209/i/600/depositphotos_392090278-stock-photo-exploding-light-bulb-dark-blue.jpg',
        'https://st.depositphotos.com/1864689/1538/i/600/depositphotos_15388723-stock-photo-light-bulb.jpg',
        'https://st2.depositphotos.com/1001877/5180/i/600/depositphotos_51808361-stock-photo-light-bulb-exploding-concept-of.jpg',
        'https://static7.depositphotos.com/1206476/749/i/600/depositphotos_7492923-stock-photo-broken-light-bulb.jpg',
    ]
    
    random_message = [
        "oh no",
        "whoops",
        "nice",
        "good job",
        "we're doomed",
    ]
    
    sad_image = 'https://images-ext-1.discordapp.net/external/47E2RmeY6Ro21ig0pkcd3HaYDPel0K8CWf6jumdJzr8/https/i.ibb.co/bKG17c2/image.png'

    last_called = {}

    @extension_command(description = '💥')
    async def explode(self, ctx : CommandContext):
        user_id = ctx.author.id

        if user_id in self.last_called:
            elapsed_time = datetime.datetime.utcnow() - self.last_called[user_id]
            if elapsed_time.total_seconds() < 20:
                await ctx.send(f"Please do not spam this command. `{round(20 - elapsed_time.total_seconds(), ndigits=0)} seconds left.`", ephemeral = True)
                return
        
        self.last_called[user_id] = datetime.datetime.utcnow()
        
        explosion_amount = 0
        
        with open('databases/explosions.count', 'r') as f:
            explosion_amount = int(f.read())
        
        random_number = random.randint(1, len(Command.explosion_image)) - 1
        random_sadness = random.randint(1, 20)
        
        sad = False
        
        if random_sadness == 15:
            sad = True
        
        if not sad:
            embed = Embed(description = ' ')
            
            embed.set_author(name = f'{self.random_message[random.randint(0, len(self.random_message) - 1)]}')
            
            if explosion_amount == 69:
                embed.set_author(name = 'nice')
            if explosion_amount == 420:
                embed.set_author(name = 'nice')
            if explosion_amount == 42069:
                embed.set_author(name = 'nice')
            if explosion_amount == 69420:
                embed.set_author(name = 'nice')
            
            embed.set_image(url = Command.explosion_image[random_number])
            embed.set_footer(f'The Sun has been exploded {explosion_amount} times.')
        else:
            embed = Embed(title = '...')
            embed.set_image(url = Command.sad_image)
            embed.set_footer(f'[ You killed niko. ]')
        
        with open('databases/explosions.count', 'w') as f:
            f.write(str(explosion_amount + 1))
        
        if not sad:   
            await stamps.IncrementValue(ctx, 'suns_shattered', int(ctx.author.id))
        
        await ctx.send(embeds=embed)
    
    @explode.error
    async def error(self, ctx : CommandContext, error):
        
        embed = await on_error(error)
        
        await ctx.send(embeds=embed)
        
def setup(client):
    Command(client)