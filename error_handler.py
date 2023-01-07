from interactions import Embed, EmbedFooter
import traceback

async def on_error(error):
    
    embed = Embed(
        description= 'Sorry! An error occurred. Please try running this command later.',
        footer= EmbedFooter(text=str(error)),
        color= 0xff2025
    )
    
    traceback.print_exception(type(error), error, error.__traceback__)
    
    return embed