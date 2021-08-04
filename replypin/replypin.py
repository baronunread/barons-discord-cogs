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
        video = await self.return_video(links[0], msg.attachments[0].url)
        data =  {
                    "title": "Click to jump to message!",
                    "url": msg.jump_url,
                    "description": msg.clean_content,
                    "footer": {"text": msg.created_at.strftime("Posted on the %d/%m/%Y, at %H:%M:%S")},
                    "author": {"name": msg.author.display_name, "icon_url": str(msg.author.avatar_url)}
                }
        embed = discord.Embed.from_dict(data)
        if video:
            embed.set_field(name = "Quentin's thought:", value = "There must be a video in that message so I've posted it below this embed!")
        if links:
            embed.set_image(url = links[0])    
        if ( len(msg.attachments) > 0 ):
            embed.set_image(url = msg.attachments[0].url)
        await channel.send(embed = embed)
        if video:
            await ctx.send(video)
        # except:
        #     await ctx.send("Please reply to a post.")

    async def find_links(self, msg):
        links = re.findall(r"(?i)\bhttp[^' ']*", msg)
        return links

    async def remove_links(self, msg, links):
        for link in links:
            msg = msg.replace(link, "")
        return msg

    async def return_video(self, link1, link2):
        list1 = []
        list2 = []
        for regex in self.imageTypesRegex:
            list1 = list1 + re.findall(regex, link1)
            list2 = list1 + re.findall(regex, list2)
        if not list1:
            return link1
        if not list2:
            return link2