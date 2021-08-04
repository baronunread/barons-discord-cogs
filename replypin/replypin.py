from redbot.core import commands
import discord
import re

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

    async def find_link(self, msg):
        links = re.findall(r"(?i)\bhttp[^' ']*", msg)
        return links

    async def remove_links(self, msg, links):
        for link in links:
            msg.replace(link, "")
        return msg
        
    @commands.command()
    async def test(self, ctx):
        links = await self.find_link(ctx.message.clean_content)
        data =  {
                    "title": "Click to jump to message!",
                    "url": ctx.message.jump_url,
                    "description": await self.remove_links(ctx.message.clean_content, links),
                    "footer": {"text": ctx.message.created_at.strftime("Posted on the %d/%m/%Y, at %H:%M:%S")},
                    "author": {"name": ctx.message.author.display_name, "icon_url": str(ctx.message.author.avatar_url)},
                }
        embed = discord.Embed.from_dict(data)
        if links:
            await ctx.send(content = links[0], embed = embed)
        else:
            await ctx.send(embed = embed)
        
    async def video_or_image(self, msg):
        pass

    async def video_embed(self, msg):
        pass

    async def image_embed(self, msg):
        pass