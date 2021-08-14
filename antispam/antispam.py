from redbot.core import commands, Config
from discord.utils import get
import discord

class Antispam(commands.Cog):
    """Automatically hands out a single role that you can setup beforehand when people are found spamming."""
    def __init__(self):
        self.config = Config.get_conf(self, identifier = 99108971151153265110116105115112)
        default_global = {
                            "role": None,
                            "channel": None
                         }
        self.config.register_global(**default_global)
        self.config.register_member(messages = 0, timePrevious = None, previousMessageHash = None)
        self.cache_role = None
        self.cache_channel = None

    async def update_cache(self, type: str, content = None):
        value = content if content else await self.config.get_raw(type)
        if type == "role":
            self.cache_role = value
        elif type == "messages":
            self.cache_messages = value
        
    async def validate_cache(self):
        if self.cache_role == None: 
            await self.update_cache("role")
        if self.cache_messages == None:
            await self.update_cache("channel")    

    @commands.command()
    async def test(self, ctx):
        pass

    @commands.group()
    @commands.has_permissions(manage_messages = True)
    async def antispam(self, ctx):
        """Base command. Check the subcommands."""
        pass

    async def generic_add(self, type, content):
        await self.config.set_raw(type, value = content)
        await self.update_cache(type, content)

    @antispam.command(name = "setup")
    async def setup(self, ctx, roleID, channelID):
        """Insert the ID of the role and the amount of messages that you'd want for it to be given."""
        await self.generic_add("role", int(roleID))
        await self.generic_add("channel", int(channelID))
        await ctx.send("Setup complete.") 

    @antispam.group(name = "edit")
    async def edit(self, ctx):
        """Edit the ID of the role or the amount of messages."""
        pass

    @edit.command(name = "role")
    async def role(self, ctx, roleID):
        await self.generic_add("role", int(roleID))
        await ctx.send("Edited the role successfully.")

    @edit.command(name = "channel")
    async def channel(self, ctx, channelID):
        await self.generic_add("messages", int(messages))
        await ctx.send("Edited the channel successfully.")
    
    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        await self.validate_cache() 
        user = message.author
        if user.bot or not self.cache_role or not self.cache_channel:
            return
        role = get(user.guild.roles, id = self.cache_role)
        channel = ctx.guild.get_channel(self.cache_channel) 
        messages = await self.config.member(user).messages()
        timePrevious = await self.config.member(user).timePrevious() 
        previousMessageHash = await self.config.member(user).previousMessageHash()
        timeCurrent = message.created_at
        currentMessageHash = hash(message.clean_content) if message.clean_content else hash(message.attachments[0].url)
        if not timePrevious:
            await self.config.member(user).timePrevious.set(timeCurrent)
            await self.config.member(user).previousMessageHash.set(currentMessageHash)
            return
        deltaTime = (timeCurrent - timePrevious).seconds
        differentHash = currentMessageHash - previousMessageHash
        await self.config.member(user).timePrevious.set(timeCurrent)
        await self.config.member(user).previousMessageHash.set(currentMessageHash)
        if deltaTime < 1 or not differentHash:
            messages += 1
            if messages >= 3:
                await user.add_roles(role)
                await self.config.member(user).messages.set(0)
                await channel.send("I have muted the user: " + user.mention + "for spamming.")
            else
                await self.config.member(user).messages.set(messages)
        else:
            await self.config.member(user).messages.set(0)

    @commands.Cog.listener()
    async def on_member_ban(self, guild, user):
        await self.config.member(user).clear()  