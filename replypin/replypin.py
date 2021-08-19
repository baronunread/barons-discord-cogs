from redbot.core import commands
import discord
import aiohttp
import re

class Replypin(commands.Cog):
    """When called 'pins' the message that was replied to. """
    def __init__(self):
        self.imageTypesRegex =  {
                                    r"(?i)tenor\.com",
                                    r"(?i)\.png\b",
                                    r"(?i)\.gif\b",
                                    r"(?i)\.jpe?g\b",
                                    r"(?i)\.webp\b" 
                                }
        self.videoTypesRegex =  {
                                    r"(?i)youtube\.com",
                                    r"(?i)\.mp4\b",
                                    r"(?i)\.mov\b",
                                    r"(?i)\.webm\b" 
                                }

    @commands.command()
    @commands.has_permissions(manage_messages = True)
    async def pinthatshit(self, ctx):
        """'Pins' the post by posting it to another channel. It supports one link and one attachment."""
        try:
            id = ctx.message.reference.message_id
        except AttributeError:
            await ctx.send("Please reply to a post.")
            return
        # channel = ctx.guild.get_channel(846357308060991558) #Tojo, sorry for hardcoding!!
        channel = ctx.guild.get_channel(876484551977893908) 
        msg = await ctx.fetch_message(id)
        links = await self.find_links(msg.clean_content)
        link = links[0] if links else None
        linkImage = None if not link else await self.check_type(link, self.imageTypesRegex) 
        linkVideo = None if not link else await self.check_type(link, self.videoTypesRegex)
        attachment = msg.attachments[0].url if msg.attachments else None
        attachImage = None if not attachment else await self.check_type(attachment, self.imageTypesRegex) 
        attachVideo = None if not attachment else await self.check_type(attachment, self.videoTypesRegex)
        video = link if linkVideo else attachment if attachVideo else None
        content = msg.clean_content.replace(video, "") if video else msg.clean_content
        content = content.replace(link, "") if linkImage or linkVideo else content
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
        if linkImage:
            embed.set_image(url = link)    
        if attachImage:
            embed.set_image(url = attachment)
        await channel.send(embed = embed)
        if video:
            await channel.send(video)
       
    async def get_tenor(self, url):
        async with aiohttp.ClientSession() as session:
            tenorUrl = url + ".gif"
            async with session.get(tenorUrl) as resp:
                tenorGif = None
                if resp.status == 200 or resp.status == 202:
                    tenorGif = resp.url.human_repr()
        return tenorGif       
    
    async def find_links(self, msg):
        links = re.findall(r"(?i)\bhttp[^' ']*", msg)
        for i, link in enumerate(links):
            if "tenor" in link:
                links.append(link)
                links[i] = await self.get_tenor(link)
                return links  

    async def remove_links(self, msg, links):
        for link in links:
            msg = msg.replace(link, "")
        return msg

    async def check_type(self, link, regexs):
        if not link:
            return None
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