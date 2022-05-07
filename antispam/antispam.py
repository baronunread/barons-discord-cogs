import asyncio
from redbot.core import commands, Config
from discord.utils import get
from discord import Embed 
from asyncio import sleep as a_sleep, all_tasks
from datetime import datetime, timezone
import discord
import random
import re

# This whole section was modified from another mute cog project written by user XuaTheGrate
time_regex = re.compile(r"(?:(\d{1,5})(h|s|m|d))+?")
remove_time = re.compile(r"(?i)(\d{1,5}[hsmd])+?")
time_dict = {"h":3600, "s":1, "m":60, "d":86400}

class TimeConverter(commands.Converter):
    async def convert(self, ctx, argument):
        args = argument.lower()
        matches = re.findall(time_regex, args)
        text = re.sub(remove_time, "", argument)
        time = 0
        for v, k in matches:
            try:
                time += time_dict[k]*float(v)
            except KeyError:
                raise commands.BadArgument(f"{k} is an invalid time-key! h/m/s/d are valid!")
            except ValueError:
                raise commands.BadArgument(f"{v} is not a number!")
        return (int(time), text)
# End of copy, thanks again ;)

class Antispam(commands.Cog):
    """Automatically hands out a single role that you can setup beforehand when people are found spamming."""
    def __init__(self, bot):
        self.bot = bot
        self.config = Config.get_conf(self, identifier = 99108971151153265110116105115112)
        default_global = {
                            "spamRole": None,
                            "roles": {},
                            "channel": None,
                            "messages": ["has been muted."],
                            "mutes": [],
                            "whitelist": []
                         }
        self.config.register_global(**default_global)
        self.config.register_member(warned = False, spamValue = 0, timePrevious = None, previousMessageHash = None, messageList = [], roles = [], secondsOfMute = 0, timeOfMute = None)
        self.cache_roles = {}
        self.cache_channel = None
        self.cache_messages = []
        self.cache_whitelist = []
        self.cache_guild = None
        self.bot.loop.create_task(self.initialization_task())

    async def initialization_task(self):
        await self.bot.wait_until_ready()
        self.cache_guild = self.bot.guilds[0]
        await self.validate_cache()
        await self.start_mute_timers()
    
    async def return_cache(self, type: str):
        if type == "roles":
            return self.cache_roles
        elif type == "channel":
            return self.cache_channel
        elif type == "messages":
            return self.cache_messages
        elif type == "whitelist":
            return self.cache_whitelist

    async def update_cache(self, type: str, content = None):
        value = content if content else await self.config.get_raw(type)
        guild = self.cache_guild
        if type == "roles":
            self.cache_roles = {key: get(guild.roles, id = value[key]) for key in value}
        elif type == "channel":
            self.cache_channel = guild.get_channel(value)
        elif type == "messages":
            self.cache_messages = value
        elif type == "whitelist":
            self.cache_whitelist = value
        
    async def validate_cache(self):
        if not self.cache_roles: 
            await self.update_cache("roles")
        if not self.cache_channel:
            await self.update_cache("channel")
        if not self.cache_messages:
            await self.update_cache("messages")
        if not self.cache_whitelist:
            await self.update_cache("whitelist")

    async def start_mute_timers(self):
        listOfMutes = await self.config.mutes()
        if not listOfMutes: return
        guild = self.cache_guild
        roles = self.cache_roles.values()
        modChannel = self.cache_channel
        message = await modChannel.send("Grabbing local time to restart the muted timers...")
        currentTime = message.created_at.timestamp()
        listOfMutes = [*set(listOfMutes),] #duplicates from manual unmutes removal
        listOfActualMutes = []
        for user in listOfMutes:     
            try: 
                user = await guild.fetch_member(user)
            except:
                continue #if user fetching fails for any reason the user is probably gone
            check = [role for role in roles if role in user.roles]
            if not check: #removal of unmuted users from the list and clearing their data
                await self.config.member(user).clear()
                continue
            role = check[0] #if it's here there's at least one item in check
            listOfActualMutes.append(user.id)
            time = await self.config.member(user).secondsOfMute()
            timeOfMute = await self.config.member(user).timeOfMute()
            remainingTime = max(0, time - int(currentTime - timeOfMute))
            self.bot.loop.create_task(self.unmute_timer(remainingTime, user, role, modChannel), name = user.id) 
        await self.config.mutes.set(listOfActualMutes)
        await message.delete()

    async def represent_time(self, time):
        m, s = divmod(time, 60)
        h, m = divmod(m, 60)
        d, h = divmod(h, 24)
        x = "" if d == 1 else "s"
        string = f"{d} Day{x}" if d else ""
        if h or m or s:
            if string: string += " and "
            string += "{}:{:02d}:{:02d}".format(h,m,s)
        return string

    @commands.command(name = "simmerdown")
    @commands.has_permissions(manage_messages = True)
    async def manual_mute(self, ctx, roleName, *, textAndTime :TimeConverter = None):
        """Manually mutes someone. If you don't pick a role it will pick the default one"""
        spamRole = await self.config.spamRole()
        if not roleName:
            roleName = spamRole  
        try:
            timeSeconds = textAndTime[0]
            reason = re.sub(r"(?=<)(<...\d+>)|\s{2,}|^\s+", "", discord.utils.escape_mentions(textAndTime[1])).strip()
        except TypeError:
            timeSeconds = 0
            reason = None
        msgChannel, user = await self.get_context_data(ctx) 
        role = self.cache_roles[roleName]
        spamRole = self.cache_roles[spamRole]
        modChannel = self.cache_channel
        if user.bot:
            await ctx.send("I can't edit the roles of a bot!")
        elif role in user.roles or spamRole in user.roles:
            await ctx.send("The user is already muted.")
        else:
            await self.mute(msgChannel, user, role, modChannel, True, timeSeconds, reason, ctx.message.author)
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
        roles = self.cache_roles.values()
        modChannel = self.cache_channel
        check = [role for role in roles if role in user.roles]
        if user.bot:
            await ctx.send("I can't edit the roles of a bot!")  
        elif check:
            role = check[0]
            listOfMutes = await self.config.mutes()
            if user.id in listOfMutes:
                listOfMutes.remove(user.id)
                await self.config.mutes.set(listOfMutes)
            await self.unmute(user, role, modChannel, msgChannel)
        else:
            await ctx.send("The user isn't muted.")

    @commands.command(name = "checkup")
    @commands.has_permissions(manage_messages = True)
    async def timed_mute_info(self, ctx):
        """Checks how much time is left in the muted status."""
        notUsed, user = await self.get_context_data(ctx)
        roles = self.cache_roles.values()
        check = [role for role in roles if role in user.roles]
        if user.bot:
            await ctx.send("Bots can't be muted so why should I even check up on them?!?")
        elif check:
            time = await self.config.member(user).secondsOfMute()
            if not time:
                await ctx.send("The mute is indefinite.")
            else:
                currentTime = ctx.message.created_at.timestamp()
                timeOfMute = await self.config.member(user).timeOfMute()
                remainingTime = time - int(currentTime - timeOfMute)
                if remainingTime <= 0: return
                data =  {
                            "author": {"name": "TIMED MUTE", "icon_url": str(user.avatar_url)}                        
                        }
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

    async def add_variable(self, type: str, content):
        await self.config.set_raw(type, value = content)
        await self.update_cache(type, content)

    async def add_something(self, type: str, content):
        list = await self.return_cache(type)
        list.append(content)
        await self.config.set_raw(type, value = list)
        await self.update_cache(type, list)

    async def add_key(self, type: str, key, id):
        dict = await self.config.get_raw(type)
        dict[key] = id
        await self.config.set_raw(type, value = dict)
        await self.update_cache(type, dict)
    
    @antispam.group(name = "add")
    async def add(self, ctx):
        """Base command. Select what to add."""

    @add.command(name = "role")
    async def add_role(self, ctx, key, id):
        """Adds a role to the list of roles."""
        await self.add_key("roles", key, id)
        await ctx.send("Successfully added the new role.")

    @add.command(name = "whitelist")
    async def add_whitelist(self, ctx, msg):
        """Adds a channel to the list of whitelisted channels."""
        await self.add_something("whitelist", msg)
        await ctx.send("Successfully added the new ignored channel.")

    @add.command(name = "messages")
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

    async def del_key(self, ctx, type: str, key):
        dict = await self.config.get_raw(type)
        dict.pop(key, None)
        await self.config.set_raw(type, value = dict)
        await self.update_cache(type, dict)
    
    @antispam.group(name = "delete")
    async def delete(self, ctx):
        """Base command. Select what to delete."""

    @delete.command(name = "role")
    async def add_role(self, ctx, key, id):
        """Deletes a role from the list of roles."""
        await self.del_key("roles", key)
        await ctx.send("Successfully deleted the new role.")

    @delete.command(name = "whitelist")
    async def del_whitelist(self, ctx, *, msg):
        """Removes a channel from the list of whitelisted channels."""
        await self.del_something(ctx, "whitelist", msg)
    
    @delete.command(name = "messages")
    async def del_mute(self, ctx, *, msg):
        """Removes a message from the list of messages."""
        await self.del_something(ctx, "messages", msg)

    @antispam.group(name = "list")
    async def list_things(self, ctx):
        """Base command. Select what to list."""
        pass

    async def list_help(self, ctx, type):
        list = self.return_cache(type) if (type != "roles") else self.return_cache(type).values()
        await ctx.message.author.send(f"```{list}```")

    @antispam.command(name = "roles")
    async def list_whitelist(self, ctx):
        """Sends the list of roles through DMs"""
        await self.list_help("roles")
    
    @antispam.command(name = "whitelist")
    async def list_whitelist(self, ctx):
        """Sends the list of whitelisted channels through DMs"""
        await self.list_help("whitelist")

    @antispam.command(name = "messages")
    async def list_mute(self, ctx):
        """Sends the list of messages through DMs"""
        await self.list_help("messages")
       
    @antispam.command(name = "setup")
    async def setup(self, ctx):
        """Insert the ID of the role that mutes people by default and the ID of the mod channel that you'd want to use for the notifications."""
        author = ctx.message.author
        channel = ctx.message.channel
        def check(m, user):
            return m.channel == channel and user == author
        try:
            await ctx.send("Please send the name of the role that will mute the people with the command by default.")
            spamRole = await self.bot.wait_for('message', check = check, timeout = 120.0)
            await ctx.send("Please send the id of the role that will mute the people with the command by default.")
            spamRoleID = await self.bot.wait_for('message', check = check, timeout = 120.0)
            await ctx.send("Please send the id of the channel that will be used to notify the server of the mutes.")
            channelID = await self.bot.wait_for('message', check = check, timeout = 120.0)
        except asyncio.TimeoutError:
            await ctx.send("Too much time has passed, I'll be going to sleep...")
            return    
        await self.add_variable("spamRole", spamRole)
        await self.add_key("roles", spamRole, int(spamRoleID))
        await self.add_variable("channel", int(channelID))
        await ctx.send("Setup complete.")

    @commands.Cog.listener()
    async def on_message(self, message): 
        ctx = await self.bot.get_context(message)
        whitelist = await self.return_cache("whitelist")
        user = message.author
        if user.bot or ctx.valid or str(ctx.channel.id) in whitelist or not self.cache_roles:
            return
        spamRole = await self.config.spamRole()
        role = self.cache_roles[spamRole]   
        modChannel = self.cache_channel 
        msgList = await self.config.member(user).messageList()       
        timePrevious = await self.config.member(user).timePrevious() 
        previousMessageHash = await self.config.member(user).previousMessageHash()
        timeCurrent = message.created_at.timestamp()
        currentMessageHash = hash(message.clean_content)
        currentMessageHash += message.attachments[0].size + hash(message.attachments[0].filename) if message.attachments else 0
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
                await message.channel.send(f"{user.mention} stop spamming or you'll be muted.")
            if warned:
                try:
                    alreadyMuting, = [task for task in all_tasks() if task.get_name() == f"{user.id}Mute"]
                except ValueError:
                    self.bot.loop.create_task(self.mute(message.channel, user, role, modChannel, False, 0, None), name = f"{user.id}Mute")            
        else:
            await self.config.member(user).messageList.set( [ (message.channel.id, message.id) ] )
            await self.config.member(user).spamValue.set(0)
            await self.config.member(user).warned.set(False)  

    async def mute(self, msgChannel, user, role, modChannel, manual, mutedTime, selected, moderator = None):
        await self.remove_roles_and_mute(user, role)
        random.seed(random.random())
        if not selected:
            selected = random.choice(self.cache_messages)
        data =  {
                    "author": {"name": "PUNISHED" if not mutedTime else "TIMED PUNISHMENT", "icon_url": str(user.avatar_url)}
                }
        msgEmbed = Embed.from_dict(data)
        msgEmbed.timestamp = datetime.now(tz = timezone.utc)
        if mutedTime:
            await self.config.member(user).secondsOfMute.set(mutedTime)
            msgEmbed.add_field(name = "TIME IN JAIL:", value = await self.represent_time(mutedTime))
        modEmbed = msgEmbed.copy()
        msgEmbed.description = f"{user.mention} {selected}"
        mutedText = f"muted the user {user.mention}"
        modEmbed.description = f"I have {mutedText} for spamming" if not manual else f"{moderator.mention} has {mutedText}"
        await msgChannel.send(embed = msgEmbed)
        await modChannel.send(embed = modEmbed)
        if manual:
            return
        toDelete = await self.config.member(user).messageList()
        for channelID, messageID in toDelete:
            channel = user.guild.get_channel(channelID)
            message = await channel.fetch_message(messageID)
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
                        "author": {"name": "FREED", "icon_url": str(user.avatar_url)},
                        "description" : f"{user.mention} has been freed"                    }
        msgEmbed = Embed.from_dict(msgDict)
        msgEmbed.timestamp = datetime.now(tz = timezone.utc)
        await modChannel.send(embed = msgEmbed)
        if msgChannel:
            await msgChannel.send(f"{user.mention} you've been freed!")
        else: 
            try:
                await user.send("You've been freed!")
            except discord.HTTPException:
                await modChannel.send(f"I've tried to send a DM to {user.mention} to tell them they've been freed but their DMs are closed.")   
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
        if not self.cache_roles or not self.cache_channel:
            await ctx.send("I haven't been setup yet.")
        elif isinstance(error.__cause__, AttributeError):
            await ctx.send("I need a reply or a mention to work. For purge I need only the reply.")
        elif isinstance(error, commands.CheckFailure):
            return
        else:
            await ctx.send(f"Something unexpected happened so send this to Baron Unread: {error}")