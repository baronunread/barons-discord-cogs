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

        # footer = { "text": ctx.message.created_at.strftime("Posted on the %d/%m/%Y, at %H:%M:%S") }
        # video = { "url": msg }
        # author = { "name": ctx.message.author.display_name, "icon_url": ctx.message.author.avatar_url }
        # data =  {
        #             "title": "Click to jump to message!",
        #             "type": "video",
        #             "description": "test",
        #             "url": ctx.message.jump_url,
        #             "footer": discord.Embed.from_dict(footer),
        #             "video": discord.Embed.from_dict(video),
        #             "author": discord.Embed.from_dict(author)
        #         }
        data =  {
                    "footer": {"text": "Posted on the 04/08/2021, at 14:32:06"},
                    "author": {"name": "Baron Unread", "icon_url": "https://cdn.discordapp.com/avatars/282971889062772747/0a535cbc3b664762d116615af2179ebe.webp?size=1024"},
                    "type": "rich", 
                    "description": "!test https://www.youtube.com/watch?v=rudSWhe_KD0",
                    "url": "https://discord.com/channels/347702375068467200/769609039977512960/872487066796187679",
                    "title": "Click to jump to message!"
                }
        embed = discord.Embed.from_dict(data)
        await ctx.send(embed = embed)
        
    async def video_or_image(self, msg):
        pass

    async def video_embed(self, msg):
        pass

    async def image_embed(self, msg):
        pass