from interactions import *
import bot_data.command_manager as command_manager
import bot_data.load_data as load_data
import Badges.stamp_system as stamps

TOKEN = load_data.load_config('token')

client = Client(TOKEN, intents = Intents.DEFAULT | Intents.GUILD_MESSAGE_CONTENT)

command_manager.load_commands(client=client)

stamps.setup(client)

@client.event()
async def on_start():
    print("Starting up...")
    
    await client.change_presence(
        ClientPresence(
            status=StatusType.ONLINE,
            activities=[
                PresenceActivity(name="Oneshot 💡", type=PresenceActivityType.GAME)
            ]
        )
    )
    
    print("Bot is ready.")
    
    
@client.event()
async def on_message_create(message : Message):
    
    if not message.author.bot:
        await stamps.IncrementValue(message, 'times_messaged', int(message.author.id))
    
client.start()