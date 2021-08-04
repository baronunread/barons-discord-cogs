from typing import overload
from redbot.core import commands
import discord
import re

class Replypin(commands.Cog):
    """When called 'pins' the message that was replied to. """
    def __init__(self):
        self.imageTypesRegex =  {
                                    r"tenor\.com",
                                    r"\.png",
                                    r"\.gif",
                                    r"\.jpe?g" 
                                }
        self.videoTypesRegex =  {
                                    r"youtube\.com",
                                    r"\.mp4",
                                    r"\.mov",
                                    r"\.webm" 
                                }
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
        # try:
            #channel = ctx.guild.get_channel(846357308060991558) #Tojo
        channel = ctx.guild.get_channel(769609039977512960) #Baron
        id = ctx.message.reference.message_id
        msg = await ctx.fetch_message(id)
        links = await self.find_links(msg.clean_content)
        link = links[0] if links else None
        tenor = re.findall(r"tenor\.com", link) if link else None
        try:
            video = await self.return_video(links[0], msg.attachments[0].url)
        except:
            video = await self.check_type(links[0], self.videoTypesRegex) if links else await self.check_type(msg.attachments[0].url, self.videoTypesRegex) if msg.attachments else None
        finally:
            content = msg.clean_content.replace(video, "") if video else msg.clean_content
        content = msg.clean_content.replace(link, "") if link else content
        data =  {
                    "title": "Click to jump to message!",
                    "url": msg.jump_url,
                    "description": content,
                    "footer": {"text": msg.created_at.strftime("Posted on the %d/%m/%Y, at %H:%M:%S")},
                    "author": {"name": msg.author.display_name, "icon_url": str(msg.author.avatar_url)}
                }
        embed = discord.Embed.from_dict(data)
        if video:
            embed.add_field(name = "Quentin's thought:", value = "There must be a video in that message so I've posted it below this embed!")
        if tenor:
            embed.add_field(name = "Quentin's thought:", value = "Tenor gifs don't work inside embeds so I've posted it below this embed!")
        if link and await self.check_type(link, self.imageTypesRegex) and not tenor:
            embed.set_image(url = link)    
        if msg.attachments:
            embed.set_image(url = msg.attachments[0].url)
        await channel.send(embed = embed)
        if video or tenor:
            await ctx.send(video if video else link)
        # except:
        #     await ctx.send("Please reply to a post.")

    async def find_links(self, msg):
        links = re.findall(r"\bhttp[^' ']*", msg)
        return links

    async def remove_links(self, msg, links):
        for link in links:
            msg = msg.replace(link, "")
        return msg

    async def check_type(self, link, regexs):
        list = []
        for regex in regexs:
            list = list + re.findall(regex, link)
            if list:
                return link
        return None

    async def return_video(self, link1, link2):
        list1 = []
        list2 = []
        for regex in self.videoTypesRegex:
            list1 = list1 + re.findall(regex, link1)
            if list1:
                return link1
            list2 = list2 + re.findall(regex, link2)
            if list2:
                return link2
        return None