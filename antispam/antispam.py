from redbot.core import commands, Config
from discord.utils import get
from discord import Embed 
from datetime import datetime
from asyncio import sleep as a_sleep, all_tasks
import random
import re

# This whole section was copied from another mute cog project written by user XuaTheGrate
time_regex = re.compile(r"(?:(\d{1,5})(h|s|m|d))+?")
time_dict = {"h":3600, "s":1, "m":60, "d":86400}

class TimeConverter(commands.Converter):
    async def convert(self, ctx, argument):
        args = argument.lower()
        matches = re.findall(time_regex, args)
        time = 0
        for v, k in matches:
            try:
                time += time_dict[k]*float(v)
            except KeyError:
                raise commands.BadArgument("{} is an invalid time-key! h/m/s/d are valid!".format(k))
            except ValueError:
                raise commands.BadArgument("{} is not a number!".format(v))
        return int(time)
# End of copy, thanks again ;)

class Antispam(commands.Cog):
    """Automatically hands out a single role that you can setup beforehand when people are found spamming."""
    def __init__(self, bot):
        self.bot = bot
        self.config = Config.get_conf(self, identifier = 99108971151153265110116105115112)
        default_global = {
                            "role": None,
                            "channel": None,
                            "messages": ["has been muted."]
                         }
        self.config.register_global(**default_global)
        self.config.register_member(timePrevious = None, previousMessageHash = None, messageList = [], roles = [], secondsOfMute = 0)
        self.cache_role = None
        self.cache_channel = None
        self.cache_messages = []
        self.bot.loop.create_task(self.validate_cache())

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

    async def represent_time(self, time):
        m, s = divmod(time, 60)
        h, m = divmod(m, 60)
        d, h = divmod(h, 24)
        days = " Day" + "" if d == 1 else "s"
        string = str(d) + days if d else ""
        if h or m or s: string += "and {}:{:02d}:{:02d}".format(h,m,s)
        return string

    @commands.command(name = "simmerdown")
    @commands.has_permissions(manage_messages = True)
    async def manual_mute(self, ctx, *, timeSeconds :TimeConverter = None):
        """Manually mutes someone."""
        if not self.cache_role or not self.cache_channel:
            await ctx.send("I have not been set up yet!")
            return
        msgChannel, user, role, modChannel = await self.get_context_data(ctx)
        if not user:
            await ctx.send("I need either a reply or mention to mute someone.")
        elif user.bot:
            await ctx.send("I can't edit the roles of a bot!")
        elif role in user.roles:
            await ctx.send("The user is already muted.")
        else:   
            await self.mute(msgChannel, user, role, modChannel, True, timeSeconds)
            muteInfo = (msgChannel, user, role, modChannel)
            if timeSeconds > 0:
                self.bot.loop.create_task(self.unmute_timer(timeSeconds, muteInfo), name = user.id)

    async def unmute_timer(self, time, info):
        while time > 1:
            await a_sleep(time // 2)
            await self.config.member(info[1]).secondsOfMute.set(time // 2)
            time -= time // 2 
        await self.unmute(info[0], info[1], info[2], info[3])   

    @commands.command(name = "speakup")
    @commands.has_permissions(manage_messages = True)
    async def manual_unmute(self, ctx):
        """Manually unmutes someone."""
        if not self.cache_role or not self.cache_channel:
            await ctx.send("I have not been set up yet!")
            return
        msgChannel, user, role, modChannel = await self.get_context_data(ctx)
        if not user:
            await ctx.send("I need either a reply or mention to unmute someone.")    
        elif user.bot:
            await ctx.send("I can't edit the roles of a bot!")  
        elif role in user.roles:
            await self.unmute(msgChannel, user, role, modChannel)
        else:
            await ctx.send("The user isn't muted.")

    @commands.command(name = "checkup")
    @commands.has_permissions(manage_messages = True)
    async def timed_mute_info(self, ctx):
        """Checks how much time is left in the muted status."""
        if not self.cache_role or not self.cache_channel:
            await ctx.send("I have not been set up yet!")
            return
        notUsed, user, role = await self.get_context_data(ctx)
        if not user:
            await ctx.send("I need either a reply or mention to check up on someone's jail time.")    
        elif user.bot:
            await ctx.send("Bots can't be muted so why should I even check up on them?!?")
        elif role in user.roles:
            time = self.config.member(user).secondsOfMute()
            if time == 0:
                await ctx.send("The mute is indefinite.")
            else:
                data =  {
                    "author": {"name": "TIMED MUTE", "icon_url": str(user.avatar_url)},
                    "footer": {"text": datetime.now().strftime("%d/%m/%Y, at %H:%M:%S")}
                }
                msgEmbed = Embed.from_dict(data)
                msgEmbed.add_field(name = "TIME IN JAIL LEFT:", value = await self.represent_time(time))
                await ctx.send(embed = msgEmbed)
        else:
            await ctx.send("The user isn't muted.")     
    
    async def get_context_data(self, ctx):
        msgChannel, user = await self.try_get_user_and_channel(ctx.message)
        if not user:
            return None, None, None, None
        role = get(user.guild.roles, id = self.cache_role)
        modChannel = user.guild.get_channel(self.cache_channel)
        return msgChannel, user, role, modChannel

    async def try_get_user_and_channel(self, msg):
        msgChannel = msg.channel
        try:
            id = msg.reference.message_id
            msg = await msgChannel.fetch_message(id)
            user = msg.author
        except AttributeError:
            if msg.mentions:
                user = msg.mentions[0]
            else:
                user = None
        return msgChannel, user

    @commands.group()
    @commands.has_permissions(manage_messages = True)
    async def antispam(self, ctx):
        """Base command. Check the subcommands."""
        pass

    async def generic_add(self, type, content):
        await self.config.set_raw(type, value = content)
        await self.update_cache(type, content)

    @antispam.command(name = "addMuteMessage")
    async def add_mute(self, ctx, *, msg):
        """Adds a message that randomly gets sent when muting someone."""
        list = self.cache_messages
        list.append(msg)
        await self.config.messages.set(list)
        await self.update_cache("messages", list)
        await ctx.send("Successfully added the new mute message.")

    @antispam.command(name = "delMuteMessage")
    async def del_mute(self, ctx, *, msg):
        """Removes a message from the list of messages."""
        list = self.cache_messages
        if msg not in list:
            await ctx.send("There's no such message in that list!")
            return
        list.remove(msg)
        await self.config.messages.set(list)
        await self.update_cache("messages", list)
        await ctx.send("Successfully removed the mute message.")

    @antispam.command(name = "listMuteMessage")
    async def list_mute(self, ctx):
        """Sends the list of messages through DMs"""
        list = self.cache_messages
        await ctx.send("```" + str(list) +  "```") 
       
    @antispam.command(name = "setup")
    async def setup(self, ctx, roleID, channelID):
        """Insert the ID of the role that mutes people and the ID of the mod channel that you'd want to use for the notifications."""
        await self.generic_add("role", int(roleID))
        await self.generic_add("channel", int(channelID))
        await ctx.send("Setup complete.") 

    @antispam.group(name = "edit")
    async def edit(self, ctx):
        """Edit the ID of the role or the ID of the mod channel."""
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
    async def on_message(self, message):
        ctx = await self.bot.get_context(message)
        user = message.author
        if user.bot or ctx.valid or not self.cache_role or not self.cache_channel:
            return
        msgList = await self.config.member(user).messageList()
        format = "%m/%d/%Y, %H:%M:%S"
        role = get(user.guild.roles, id = self.cache_role)
        modChannel = message.guild.get_channel(self.cache_channel) 
        timePrevious = await self.config.member(user).timePrevious() 
        timePrevious = datetime.strptime(timePrevious, format) if timePrevious else None
        previousMessageHash = await self.config.member(user).previousMessageHash()
        timeCurrent = message.created_at  
        timeSaved = timeCurrent.strftime(format)
        currentMessageHash = hash(message.clean_content) if message.clean_content else hash( message.attachments[0].filename + str(message.attachments[0].size) )
        if not timePrevious:
            timePrevious = timeCurrent
            previousMessageHash = currentMessageHash
        deltaTime = (timeCurrent - timePrevious).seconds
        differentHash = currentMessageHash - previousMessageHash
        await self.config.member(user).timePrevious.set(timeSaved)
        await self.config.member(user).previousMessageHash.set(currentMessageHash)
        if deltaTime < 1 or not differentHash:
            msgList.append( (message.channel.id, message.id) )
            await self.config.member(user).messageList.set(msgList)    
            messages = len(msgList)
            if messages == 3:
                await message.channel.send(user.mention + " stop spamming or you'll be muted.")
            elif messages == 5:
                await self.mute(message.channel, user, role, modChannel, False)
                return
        else:
            await self.config.member(user).messageList.set( [ (message.channel.id, message.id) ] )

    async def mute(self, msgChannel, user, role, modChannel, manual, mutedTime = 0):
        reason = " for spamming" if not manual else ""
        random.seed(random.random())
        selected = random.choice(self.cache_messages)
        data =  {
                    "author": {"name": "MUTED" if mutedTime == 0 else "TIMED MUTE", "icon_url": str(user.avatar_url)},
                    "footer": {"text": datetime.now().strftime("%d/%m/%Y, at %H:%M:%S")}
                }
        msgDict = data.copy()
        modDict = data.copy()
        msgDict["description"] = user.mention + " " + selected
        modDict["description"] = "I have muted the user " + user.mention + reason
        msgEmbed = Embed.from_dict(msgDict)
        modEmbed = Embed.from_dict(modDict)
        if mutedTime:
            await self.config.member(user).secondsOfMute.set(mutedTime)
            msgEmbed.add_field(name = "TIME IN JAIL:", value = await self.represent_time(mutedTime))
        await msgChannel.send(embed = msgEmbed)
        await modChannel.send(embed = modEmbed)
        await self.config.member(user).roles.set([role.id for role in user.roles])
        for userRole in user.roles:
            try:
                await user.remove_roles(userRole)
            except:
                pass
        await user.add_roles(role)
        if manual:
            return
        toDelete = await self.config.member(user).messageList()
        for pair in toDelete:
            channel = user.guild.get_channel(pair[0])
            message = await channel.fetch_message(pair[1])
            await message.delete()

    async def unmute(self, msgChannel, user, role, modChannel):
        msgDict =   {
                        "author": {"name": "UNMUTED", "icon_url": str(user.avatar_url)},
                        "footer": {"text": datetime.now().strftime("%d/%m/%Y, at %H:%M:%S")},
                        "description" : user.mention + " has been unmuted"
                    }
        msgEmbed = Embed.from_dict(msgDict)
        await modChannel.send(embed = msgEmbed)
        roles = await self.config.member(user).roles()
        roles = [get(user.guild.roles, id = roleID) for roleID in roles]
        await user.remove_roles(role)
        for userRole in roles:
            try:
                await user.add_roles(userRole)
            except:
                pass
        await msgChannel.send(user.mention + " you've been unmuted!")
        await self.config.member(user).clear()
        try:    
            timer, = [task for task in all_tasks() if task.get_name() == str(user.id)]
            timer.cancel()
        except:
            pass

    @commands.Cog.listener()
    async def on_member_ban(self, guild, user):
        await self.config.member(user).clear()  