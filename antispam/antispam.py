from redbot.core import commands, Config
from discord.utils import get
from datetime import datetime
import discord
import random

class Antispam(commands.Cog):
    """Automatically hands out a single role that you can setup beforehand when people are found spamming."""
    def __init__(self):
        self.config = Config.get_conf(self, identifier = 99108971151153265110116105115112)
        default_global = {
                            "role": None,
                            "channel": None,
                            "messages": ["has been muted."]
                         }
        self.config.register_global(**default_global)
        self.config.register_member(messages = 0, timePrevious = None, previousMessageHash = None)
        self.cache_role = None
        self.cache_channel = None
        self.cache_messages = []
        

    async def update_cache(self, type: str, content = None):
        value = content if content else await self.config.get_raw(type)
        if type == "role":
            self.cache_role = value
        elif type == "channel":
            self.cache_channel = value
        elif type == "messages":
            self.cache_messages = value
        
    async def validate_cache(self):
        if self.cache_role == None: 
            await self.update_cache("role")
        if self.cache_channel == None:
            await self.update_cache("channel")
        if self.cache_messages == []:
            await self.update_cache("messages")    

    @commands.command(name = "simmerdown")
    @commands.has_permissions(manage_messages = True)
    async def manual_mute(self, ctx):
        await self.validate_cache()
        try:
            id = ctx.message.reference.message_id
            msg = await ctx.fetch_message(id)
            user = msg.author
            msgChannel = msg.channel
        except AttributeError:
            if ctx.message.mentions:
                user = ctx.message.mentions[0]
                msgChannel = ctx.message.channel
            else:
                await ctx.send("I need either a reply or mention to mute someone.")
                return
        if user.bot or not self.cache_role or not self.cache_channel:
            return 
        role = get(user.guild.roles, id = self.cache_role)
        modChannel = ctx.message.guild.get_channel(self.cache_channel)
        await self.mute(msgChannel, user, role, modChannel, True)

    @commands.group()
    @commands.has_permissions(manage_messages = True)
    async def antispam(self, ctx):
        """Base command. Check the subcommands."""
        pass

    async def generic_add(self, type, content):
        await self.config.set_raw(type, value = content)
        await self.update_cache(type, content)

    @antispam.command(name = "add mute message")
    async def add_mute(self, ctx, *, msg):
        await self.validate_cache()
        list = self.cache_messages
        list.append(msg)
        await self.generic_add("messages", list)
        await ctx.send("Successfully added the new mute message.")

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
        await self.generic_add("channel", int(channelID))
        await ctx.send("Edited the channel successfully.")
    
    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        await self.validate_cache() 
        user = message.author
        if user.bot or not self.cache_role or not self.cache_channel:
            return
        format = "%m/%d/%Y, %H:%M:%S"
        role = get(user.guild.roles, id = self.cache_role)
        modChannel = message.guild.get_channel(self.cache_channel) 
        messages = await self.config.member(user).messages()
        timePrevious = await self.config.member(user).timePrevious() 
        timePrevious = datetime.strptime(timePrevious, format) if timePrevious else None
        previousMessageHash = await self.config.member(user).previousMessageHash()
        timeCurrent = message.created_at  
        timeSaved = timeCurrent.strftime(format)
        currentMessageHash = hash(message.clean_content) if message.clean_content else hash(message.attachments[0].filename)
        if not timePrevious:
            await self.config.member(user).timePrevious.set(timeSaved)
            await self.config.member(user).previousMessageHash.set(currentMessageHash)
            return
        deltaTime = (timeCurrent - timePrevious).seconds
        differentHash = currentMessageHash - previousMessageHash
        await self.config.member(user).timePrevious.set(timeSaved)
        await self.config.member(user).previousMessageHash.set(currentMessageHash)
        if deltaTime < 2 or not differentHash:
            messages += 1
            if messages == 3:
                await message.channel.send(user.mention + " stop spamming or you'll be muted.")
            elif messages >= 6:
                await self.mute(message.channel, user, role, modChannel, False)
            else:
                await self.config.member(user).messages.set(messages)
        else:
            await self.config.member(user).messages.set(0)

    async def mute(self, msgChannel, user, role, modChannel, manual):
        reason = " for spamming." if not manual else ""
        await user.add_roles(role)
        await self.config.member(user).messages.set(0)
        random.seed(random.random())
        selected = random.choice(self.cache_messages)
        await msgChannel.send(user.mention + " " + selected)
        await modChannel.send("I have muted the user: " + user.mention + reason)

    @commands.Cog.listener()
    async def on_member_ban(self, guild, user):
        await self.config.member(user).clear()  