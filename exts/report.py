import interactions
import validators

async def Report(bot : interactions.Client, ctx : interactions.ComponentContext, user_id : int):    
    @bot.modal('report')
    async def reportation(ctx : interactions.ComponentContext, report_content : str, image_url : str):
        if not validators.url(image_url):
            await ctx.send('Invalid URL. Must be of scheme \'http\' or \'https\'')
            return 'Invalid URL'
        await ctx.send("Successfully sent report.", ephemeral=True)
        
        c = await interactions.get(bot, interactions.Channel, object_id=1025158352549982299)
        
        embed = interactions.Embed(title='Report', description=report_content)
        embed.set_image(url = image_url)
        embed.set_footer(text = f'User ID: {user_id}')
        
        await c.send(
            embeds = embed
        )
        
        return None
    
    user : interactions.User = await interactions.get(bot, interactions.User, object_id=user_id)
    
    modal = interactions.Modal(
        custom_id='report',
        title= f'Reporting {user.username}',
        components = [
            interactions.TextInput(
                style=interactions.TextStyleType.PARAGRAPH,
                custom_id="text_inpusdfsdft_response",
                type = interactions.ComponentType.INPUT_TEXT,
                placeholder='What is this report about?',
                label='About'
            ),
            interactions.TextInput(
                style=interactions.TextStyleType.SHORT,
                custom_id="text_input_resposdfsdfnse",
                type = interactions.ComponentType.INPUT_TEXT,
                placeholder='https://...',
                label='Image Evidence'
            ),
        ]
    )
    
    await ctx.popup(modal)