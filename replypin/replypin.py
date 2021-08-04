from redbot.core import commands
import discord
import json

class Replypin(commands.Cog):
    """When called 'pins' the message that was replied to. """

    @commands.command()
    @commands.has_permissions(manage_messages = True)
    async def pinthatshit(self, ctx):
        """'Pins' the post by posting it to another channel."""
        try:
            channel = ctx.guild.get_channel(846357308060991558) #Tojo
            id = ctx.message.reference.message_id
            msg = await ctx.fetch_message(id)
            embed = discord.Embed(title = "Click to jump to message!", url = msg.jump_url, description = msg.clean_content)
            embed.set_author(name = msg.author.display_name, icon_url = msg.author.avatar_url)
            if ( len(msg.attachments) > 0 ):
                embed.add_field(name = "Content attached", value = msg.attachments[0].url)
                embed.set_image(url = msg.attachments[0].url)
            embed.set_footer(text = msg.created_at.strftime("Posted on the %d/%m/%Y, at %H:%M:%S"))
            await channel.send(embed = embed)
        except:
            await ctx.send("Please reply to a post.")

    @commands.command()
    async def test(self, ctx):
        # data =  {
        #             "footer": {"text": ctx.message.created_at.strftime("Posted on the %d/%m/%Y, at %H:%M:%S")},
        #             "author": {"name": ctx.message.author.display_name, "icon_url": str(ctx.message.author.avatar_url)},
        #             "description": "test",
        #             "url": ctx.message.jump_url,
        #             "title": "Click to jump to message!"
        #         }
        data2 = {
                    "video" : {"url" : "https://www.youtube.com/watch?v=rudSWhe_KD0", "height": 300, "width": 700},
                }
        # embed = discord.Embed.from_dict(data)
        video = discord.Embed.from_dict(data2)
        # await ctx.send(embed = embed)
        await ctx.send(embed = video)
        
    async def video_or_image(self, msg):
        pass

    async def video_embed(self, msg):
        pass

    async def image_embed(self, msg):
        pass