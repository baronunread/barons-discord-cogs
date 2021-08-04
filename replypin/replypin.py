from redbot.core import commands
import discord
import re

class Replypin(commands.Cog):
    """When called 'pins' the message that was replied to. """

    # OLD VERSION
    # @commands.command()
    # @commands.has_permissions(manage_messages = True)
    # async def pinthatshit(self, ctx):
    #     """'Pins' the post by posting it to another channel."""
    #     try:
    #         channel = ctx.guild.get_channel(846357308060991558) #Tojo
    #         id = ctx.message.reference.message_id
    #         msg = await ctx.fetch_message(id)
    #         embed = discord.Embed(title = "Click to jump to message!", url = msg.jump_url, description = msg.clean_content)
    #         embed.set_author(name = msg.author.display_name, icon_url = msg.author.avatar_url)
    #         if ( len(msg.attachments) > 0 ):
    #             embed.add_field(name = "Content attached", value = msg.attachments[0].url)
    #             embed.set_image(url = msg.attachments[0].url)
    #         embed.set_footer(text = msg.created_at.strftime("Posted on the %d/%m/%Y, at %H:%M:%S"))
    #         await channel.send(embed = embed)
    #     except:
    #         await ctx.send("Please reply to a post.")

    @commands.command()
    @commands.has_permissions(manage_messages = True)
    async def pinthatshit(self, ctx):
        """'Pins' the post by posting it to another channel."""
        try:
            #channel = ctx.guild.get_channel(846357308060991558) #Tojo
            channel = ctx.guild.get_channel(769609039977512960) #Baron
            id = ctx.message.reference.message_id
            msg = await ctx.fetch_message(id)
            links = await self.find_links(msg.clean_content)
            content = msg.clean_content if not links else await self.remove_links(msg.clean_content, links)
            if not content:
                content = msg.author.display_name + " has sent a video. Please look below this embed to watch it!"
            data =  {
                        "title": "Click to jump to message!",
                        "url": msg.jump_url,
                        "description": content,
                        "footer": {"text": msg.created_at.strftime("Posted on the %d/%m/%Y, at %H:%M:%S")},
                        "author": {"name": msg.author.display_name, "icon_url": str(msg.author.avatar_url)}
                    }
            embed = discord.Embed.from_dict(data)
            if ( len(msg.attachments) > 0 ):
                embed.set_image(url = msg.attachments[0].url)
            await channel.send(embed = embed)
            if links:
                await ctx.send(links[0])
        except:
            await ctx.send("Please reply to a post.")

    async def find_links(self, msg):
        links = re.findall(r"(?i)\bhttp[^' ']*", msg)
        return links

    async def remove_links(self, msg, links):
        for link in links:
            msg = msg.replace(link, "")
        return msg

    async def is_link_image(self, link):
        pass