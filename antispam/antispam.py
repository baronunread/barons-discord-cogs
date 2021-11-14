from redbot.core import commands, Config
from discord.utils import get
from discord import Embed 
from asyncio import sleep as a_sleep, all_tasks
from datetime import datetime, timezone
import discord
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
                            "messages": ["has been muted."],
                            "mutes": [],
                            "whitelist": []
                         }
        self.config.register_global(**default_global)
        self.config.register_member(warned = False, spamValue = 0, timePrevious = None, previousMessageHash = None, messageList = [], roles = [], secondsOfMute = 0, timeOfMute = None)
        self.cache_role = None
        self.cache_channel = None
        self.cache_messages = []
        self.cache_whitelist = []

    @commands.Cog.listener()    
    async def on_ready(self):
        self.bot.loop.create_task(self.validate_cache())
        self.bot.loop.create_task(self.start_mute_timers())
    
    async def return_cache(self, type: str):
        if type == "role":
            return self.cache_role
        elif type == "channel":
            return self.cache_channel
        elif type == "messages":
            return self.cache_messages
        elif type == "whitelist":
            return self.cache_whitelist

    async def update_cache(self, type: str, content = None):
        value = content if content else await self.config.get_raw(type)
        guild = self.bot.guilds[0]
        if type == "role":
            self.cache_role = get(guild.roles, id = value)
        elif type == "channel":
            self.cache_channel = guild.get_channel(value)
        elif type == "messages":
            self.cache_messages = value
        elif type == "whitelist":
            self.cache_whitelist = value
        
    async def validate_cache(self):
        if self.cache_role == None: 
            await self.update_cache("role")
        if self.cache_channel == None:
            await self.update_cache("channel")
        if self.cache_messages == []:
            await self.update_cache("messages")
        if self.cache_whitelist == []:
            await self.update_cache("whitelist")

    async def start_mute_timers(self):
        listOfMutes = await self.config.mutes()
        if not listOfMutes: return
        guild = self.bot.guilds[0]
        role = self.cache_role
        modChannel = self.cache_channel
        currentTime = datetime.now(tz = timezone.utc).timestamp()
        realListOfMutes = [user for user in listOfMutes if role in user.roles]
        await self.config.mutes.set(realListOfMutes)
        for user in listOfMutes:
            user = await guild.fetch_member(user)
            time = await self.config.member(user).secondsOfMute()
            timeOfMute = await self.config.member(user).timeOfMute()
            remainingTime = max(0, time - int(currentTime - timeOfMute))
            await user.send("Current time: {} \n Seconds of mute: {} \n Time of mute: {} \n Remaining time: {}".format(currentTime, time, timeOfMute, remainingTime))
            self.bot.loop.create_task(self.unmute_timer(remainingTime, user, role, modChannel), name = user.id) 

    async def represent_time(self, time):
        m, s = divmod(time, 60)
        h, m = divmod(m, 60)
        d, h = divmod(h, 24)
        days = str(d) + " Day" + ("" if d == 1 else "s")
        string = days if d else ""
        if h or m or s:
            if string: string += " and "
            string += "{}:{:02d}:{:02d}".format(h,m,s)
        return string

    @commands.command(name = "simmerdown")
    @commands.has_permissions(manage_messages = True)
    async def manual_mute(self, ctx, *, timeSeconds :TimeConverter = None):
        """Manually mutes someone."""
        msgChannel, user = await self.get_context_data(ctx)
        role = self.cache_role
        modChannel = self.cache_channel
        if user.bot:
            await ctx.send("I can't edit the roles of a bot!")
        elif role in user.roles:
            await ctx.send("The user is already muted.")
        else:
            await self.mute(msgChannel, user, role, modChannel, True, timeSeconds)
            if not timeSeconds: return
            listOfMutes = await self.config.mutes()
            listOfMutes.append(user.id)
            await self.config.mutes.set(listOfMutes)
            timeOfMute = ctx.message.created_at.timestamp()
            await self.config.member(user).timeOfMute.set(timeOfMute) 
            self.bot.loop.create_task(self.unmute_timer(timeSeconds, user, role, modChannel, msgChannel), name = user.id)

    async def unmute_timer(self, time, user, role, modChannel, msgChannel = None):
        while time > 1:
            await a_sleep(time // 2)
            time -= time // 2 
        listOfMutes = await self.config.mutes()
        listOfMutes.remove(user.id)
        await self.config.mutes.set(listOfMutes)
        await self.unmute(user, role, modChannel, msgChannel)   

    @commands.command(name = "speakup")
    @commands.has_permissions(manage_messages = True)
    async def manual_unmute(self, ctx):
        """Manually unmutes someone."""
        msgChannel, user = await self.get_context_data(ctx)
        role = self.cache_role
        modChannel = self.cache_channel
        if user.bot:
            await ctx.send("I can't edit the roles of a bot!")  
        elif role in user.roles:
            listOfMutes = await self.config.mutes()
            listOfMutes.delete(user.id)
            await self.config.mutes.set(listOfMutes)
            await self.unmute(user, role, modChannel, msgChannel)
        else:
            await ctx.send("The user isn't muted.")

    @commands.command(name = "checkup")
    @commands.has_permissions(manage_messages = True)
    async def timed_mute_info(self, ctx):
        """Checks how much time is left in the muted status."""
        notUsed, user = await self.get_context_data(ctx)
        role = get(user.guild.roles, id = self.cache_role)
        if user.bot:
            await ctx.send("Bots can't be muted so why should I even check up on them?!?")
        elif role in user.roles:
            time = await self.config.member(user).secondsOfMute()
            if not time:
                await ctx.send("The mute is indefinite.")
            else:
                currentTime = ctx.message.created_at.timestamp()
                timeOfMute = await self.config.member(user).timeOfMute()
                remainingTime = time - int(currentTime - timeOfMute)
                if remainingTime <= 0: return
                data =  {
                            "author": {"name": "TIMED MUTE", "icon_url": str(user.avatar_url)}                        }
                msgEmbed = Embed.from_dict(data)
                msgEmbed.timestamp = datetime.now(tz = timezone.utc)
                msgEmbed.add_field(name = "TIME IN JAIL LEFT:", value = await self.represent_time(remainingTime))
                await ctx.send(embed = msgEmbed)
        else:
            await ctx.send("The user isn't muted.")   

    async def get_context_data(self, ctx):
        msgChannel, user = await self.try_get_user_and_channel(ctx.message)
        if not user:
            return None, None
        return msgChannel, user

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

    async def add_something(self, type: str, content):
        list = await self.return_cache(type)
        list.append(content)
        await self.config.set_raw(type, value = list)
        await self.update_cache(type, list)
    
    @antispam.command(name = "addWhitelist")
    async def add_whitelist(self, ctx, msg):
        """Adds a channel to the list of whitelisted channels."""
        await self.add_something("whitelist", msg)
        await ctx.send("Successfully added the new ignored channel.")

    @antispam.command(name = "addMuteMessage")
    async def add_mute(self, ctx, *, msg):
        """Adds a message that randomly gets sent when muting someone."""
        await self.add_something("messages", msg)
        await ctx.send("Successfully added the new mute message.")

    async def del_something(self, ctx, type: str, content):
        list = await self.return_cache(type)
        if content not in list:
            await ctx.send("There's nothing like that in the list!")
            return
        list.remove(content)
        await self.config.set_raw(type, value = list)
        await self.update_cache(type, list)   
        await ctx.send("Successfully removed the item.")
    
    @antispam.command(name = "delWhitelist")
    async def del_whitelist(self, ctx, *, msg):
        """Removes a channel from the list of whitelisted channels."""
        await self.del_something(ctx, "whitelist", msg)
    
    @antispam.command(name = "delMuteMessage")
    async def del_mute(self, ctx, *, msg):
        """Removes a message from the list of messages."""
        await self.del_something(ctx, "messages", msg)

    @antispam.command(name = "listWhitelist")
    async def list_whitelist(self, ctx):
        """Sends the list of whitelisted channels through DMs"""
        list = self.cache_whitelist
        await ctx.message.author.send("```" + str(list) +  "```") 

    @antispam.command(name = "listMuteMessage")
    async def list_mute(self, ctx):
        """Sends the list of messages through DMs"""
        list = self.cache_messages
        await ctx.message.author.send("```" + str(list) +  "```")
       
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
        whitelist = await self.return_cache("whitelist")
        user = message.author
        if user.bot or ctx.valid or str(ctx.channel.id) in whitelist:
            return
        try:
            role = get(user.guild.roles, id = self.cache_role)
        except:
            await ctx.send("I haven't been setup yet.")
            return
        if role in user.roles: return    
        msgList = await self.config.member(user).messageList()
        modChannel = message.guild.get_channel(self.cache_channel) 
        timePrevious = await self.config.member(user).timePrevious() 
        previousMessageHash = await self.config.member(user).previousMessageHash()
        timeCurrent = message.created_at.timestamp()
        currentMessageHash = hash(message.clean_content) if message.clean_content else hash( message.attachments[0].filename + str(message.attachments[0].size) )
        if not timePrevious or type(timePrevious) is not float:
            timePrevious = timeCurrent
            previousMessageHash = currentMessageHash
        deltaTime = timeCurrent - timePrevious
        differentHash = currentMessageHash - previousMessageHash
        await self.config.member(user).timePrevious.set(timeCurrent)
        await self.config.member(user).previousMessageHash.set(currentMessageHash)
        if deltaTime > 300:
            await self.config.member(user).clear()
            return
        warned = await self.config.member(user).warned()
        spamValue = await self.config.member(user).spamValue()
        fastSpam = deltaTime < 1
        sameSpam = not differentHash
        if fastSpam or sameSpam:
            spamValue += 2 if sameSpam else 1
            msgList.append( (message.channel.id, message.id) )
            await self.config.member(user).messageList.set(msgList)
            await self.config.member(user).spamValue.set(spamValue)    
            if spamValue >= 6 and not warned:
                await self.config.member(user).warned.set(True)
                await message.channel.send(user.mention + " stop spamming or you'll be muted.")
            if warned:
                try:
                    alreadyMuting, = [task for task in all_tasks() if task.get_name() == str(user.id) + "Mute"]
                except ValueError:
                    self.bot.loop.create_task(self.mute(message.channel, user, role, modChannel, False), name = str(user.id) + "Mute")            
        else:
            await self.config.member(user).messageList.set( [ (message.channel.id, message.id) ] )
            await self.config.member(user).spamValue.set(0)
            await self.config.member(user).warned.set(False)  

    async def mute(self, msgChannel, user, role, modChannel, manual, mutedTime = 0):
        await self.remove_roles_and_mute(user, role)
        reason = " for spamming" if not manual else ""
        random.seed(random.random())
        selected = random.choice(self.cache_messages)
        data =  {
                    "author": {"name": "MUTED" if not mutedTime else "TIMED MUTE", "icon_url": str(user.avatar_url)}
                }
        msgEmbed = Embed.from_dict(data)
        msgEmbed.timestamp = datetime.now(tz = timezone.utc)
        modEmbed = msgEmbed.copy()
        msgEmbed.description = user.mention + " " + selected
        modEmbed.description = "I have muted the user " + user.mention + reason
        if mutedTime:
            await self.config.member(user).secondsOfMute.set(mutedTime)
            msgEmbed.add_field(name = "TIME IN JAIL:", value = await self.represent_time(mutedTime))
        await msgChannel.send(embed = msgEmbed)
        await modChannel.send(embed = modEmbed)
        if manual:
            return
        toDelete = await self.config.member(user).messageList()
        for pair in toDelete:
            channel = user.guild.get_channel(pair[0])
            message = await channel.fetch_message(pair[1])
            await message.delete()

    async def remove_roles_and_mute(self, user, role):
        await self.config.member(user).roles.set([role.id for role in user.roles])
        for userRole in user.roles:
            try:
                await user.remove_roles(userRole)
            except:
                pass
        await user.add_roles(role)

    async def unmute(self, user, role, modChannel, msgChannel = None):
        await self.add_roles_and_unmute(user, role)
        msgDict =   {
                        "author": {"name": "UNMUTED", "icon_url": str(user.avatar_url)},
                        "description" : user.mention + " has been unmuted"                    }
        msgEmbed = Embed.from_dict(msgDict)
        msgEmbed.timestamp = datetime.now(tz = timezone.utc)
        await modChannel.send(embed = msgEmbed)
        if msgChannel:
            await msgChannel.send(user.mention + " you've been unmuted!")
        else: 
            try:
                await user.send("You've been unmuted!")
            except discord.HTTPException:
                await modChannel.send("I've tried to send a DM to {} to tell them they've been unmuted but their DMs are closed.".format(user.mention))   
        await self.config.member(user).clear()
        try:    
            timer, = [task for task in all_tasks() if task.get_name() == str(user.id)]
            timer.cancel()
        except:
            pass

    async def add_roles_and_unmute(self, user, role):
        roles = await self.config.member(user).roles()
        roles = [get(user.guild.roles, id = roleID) for roleID in roles]
        await user.remove_roles(role)
        for userRole in roles:
            try:
                await user.add_roles(userRole)
            except:
                pass

    @commands.command()
    @commands.has_permissions(manage_messages = True)
    async def purge(self, ctx):
        msg = ctx.message
        msgChannel = ctx.channel
        stop = msg.created_at
        id = msg.reference.message_id
        toDelete = await msgChannel.fetch_message(id)
        await toDelete.delete()
        time = toDelete.created_at
        list = [1]
        while list:    
            list = await msgChannel.purge(after = time, before = stop)
        await ctx.send("https://tenor.com/view/mib-men-in-black-will-smith-flash-gif-7529438")
        
    @commands.Cog.listener()
    async def on_member_ban(self, guild, user):
        await self.config.member(user).clear()  

    @manual_mute.error
    @manual_unmute.error
    @timed_mute_info.error
    @purge.error
    async def check_error(self, ctx, error):
        if not self.cache_role or not self.cache_channel:
            await ctx.send("I haven't been setup yet.")
        elif isinstance(error.__cause__, AttributeError):
            await ctx.send("I need a reply or a mention to work. For purge I need only the reply.")
        elif isinstance(error, commands.CheckFailure):
            return
        else:
            await ctx.send("Something unexpected happened so send this to Baron Unread: {}".format(error))