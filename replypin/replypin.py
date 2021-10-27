from redbot.core import commands
import discord
import aiohttp
import re

class Replypin(commands.Cog):
    """When called 'pins' the message that was replied to. """
    def __init__(self):
        self.session = aiohttp.ClientSession()
        self.imageTypesList =   [
                                    "png",
                                    "gif",
                                    "jpg",
                                    "jpeg",
                                    "webp" 
                                ]
        self.videoTypesList =   [
                                    "mp4",
                                    "mov",
                                    "webm" 
                                ]
        self.mediaTypesList = self.imageTypesList + self.videoTypesList

    def cog_unload(self):
        self.session.detach()

    @commands.command()
    @commands.has_permissions(manage_messages = True)
    async def pinthatshit(self, ctx):
        """'Pins' the post by posting it to another channel. It supports one link and one attachment."""
        try:
            id = ctx.message.reference.message_id
        except AttributeError:
            await ctx.send("Please reply to a post.")
            return
        channel = ctx.guild.get_channel(846357308060991558) #Tojo, sorry for hardcoding!!
        channel = ctx.guild.get_channel(876484551977893908)
        msg = await ctx.fetch_message(id)
        links = await self.find_media_links(msg.clean_content)
        content = await self.remove_links(msg.clean_content, links)
        link = await self.check_if_tenor_and_maybe_get_link(links[0]) if links else None
        linkImage = None if not link else await self.check_type(link, self.imageTypesList) 
        linkVideo = None if not link else await self.check_type(link, self.videoTypesList)
        attachment = msg.attachments[0].url if msg.attachments else None
        attachImage = None if not attachment else await self.check_type(attachment, self.imageTypesList) 
        attachVideo = None if not attachment else await self.check_type(attachment, self.videoTypesList)
        video = link if linkVideo else attachment if attachVideo else None
        data =  {
                    "title": "Click to jump to message!",
                    "url": msg.jump_url,
                    "description": content,
                    "footer": {"text": "Posted on the <t:{}>".format( int( msg.created_at.timestamp() ) )},
                    "author": {"name": msg.author.display_name, "icon_url": str(msg.author.avatar_url)},
                    "timestamp" : str(msg.created_at)
                }
        embed = discord.Embed.from_dict(data)
        embed.add_field(name = "Posted on the:", value = "<t:{}>".format( int( msg.created_at.timestamp() ) ) )
        if video:
            embed.add_field(name = "Quentin's thought:", value = "There must be a video in that message so I've posted it below this embed!")
        if linkImage:
            embed.set_image(url = link)    
        if attachImage:
            embed.set_image(url = attachment)
        await channel.send(embed = embed)
        if video:
            await channel.send(video)

    async def check_if_tenor_and_maybe_get_link(self, link):
        toReturn = link
        if "tenor" in link.lower():
            if "gif" in self.get_linkType(link).lower():
                toReturn = await self.get_tenor(toReturn)
            toReturn = await self.get_tenor(toReturn + ".gif")
        return toReturn
            
    async def remove_links(self, content, links):
        for link in links:
            content = content.replace(link, "")
        return content
       
    async def get_tenor(self, url):                     
        async with self.session.get(url) as resp:   
            tenorGif = None
            if resp.status == 200 or resp.status == 202:
                tenorGif = resp.url.human_repr()
        return tenorGif       
    
    async def find_media_links(self, msg):
        links = re.findall(r"\bhttp[^' ']*", msg)
        return [link for link in links if self.get_linkType(link).lower() in self.mediaTypesList]  

    def get_linkType(self, link):
        return link.split('/')[-1].split('.')[-1] if "tenor" not in link.lower() else "gif"
    
    async def check_type(self, link, typeList):
        linkType = self.get_linkType(link)
        return linkType in typeList