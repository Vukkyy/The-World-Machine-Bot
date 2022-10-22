import interactions

class EmbedMaker(interactions.Extension):
    @interactions.extension_command(
        title = "embed_creator",
        description = 'Create an Embed',
        options = [
            interactions.Option(
                name = 'title',
                description = 'description',
                type = interactions.OptionType.STRING
            ),
            
            interactions.Option(
                name = 'description',
                description = 'description',
                type = interactions.OptionType.STRING
            ),
            
            interactions.Option(
                name = 'footer',
                description = 'description',
                type = interactions.OptionType.STRING
            ),
            
            interactions.Option(
                name = 'footer_image',
                description = 'description',
                type = interactions.OptionType.STRING
            ),
            
            interactions.Option(
                name = 'attachment',
                description = 'description',
                type = interactions.OptionType.STRING
            ),
            
            interactions.Option(
                name = 'author',
                description = 'description',
                type = interactions.OptionType.STRING
            ),
            
            interactions.Option(
                name = 'author_image',
                description = 'description',
                type = interactions.OptionType.STRING
            ),
            
            interactions.Option(
                name = 'author_url',
                description = 'description',
                type = interactions.OptionType.STRING
            ),
        ]
    )
    async def create_embed(self, ctx, title : str, description : str, footer : str, footer_image : str, attachment : str, author : str, author_image : str, author_url : str):
        attachment_ = interactions.EmbedImageStruct(url=attachment)
        
        footer_ = interactions.EmbedFooter(
            text = footer,
            icon_url = footer_image,
        )
        author_ = interactions.EmbedAuthor(
            name=author,
            icon_url=author_image,
            url = author_url
        )
        
        embed = interactions.Embed(
            title = title,
            description = description,
            footer = footer_,
            image = attachment_,
            author=author_,
        )
        
        await ctx.send(embeds=embed)

def setup(client):
    EmbedMaker(client)