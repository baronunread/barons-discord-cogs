from redbot.core import commands, Config
from discord.utils import get
from math import floor
import discord

class Autorole(commands.Cog):
    """Automatically hands out a single role that you can setup beforehand."""
    def __init__(self):
        self.config = Config.get_conf(self, identifier = 343434651171161111099711610599971)
        default_global = {
                            "role": None,
                            "messages": 0,
                            "users": {},
                            "remembered": {}
                         }
        self.config.register_global(**default_global)
        self.cache_role = None
        self.cache_messages = 0
        self.cache_users = {}
        self.cache_remembered = {}

    async def update_cache(self, type: str, content = None):
        value = content if content else await self.config.get_raw(type)
        if type == "role":
            self.cache_role = value
        elif type == "messages":
            self.cache_messages = value
        elif type == "users":
            self.cache_users = value
        elif type == "remembered":
            self.cache_remembered = value
        
    async def validate_cache(self):
        if self.cache_role == None: 
            await self.update_cache("role")
        if self.cache_messages == 0:
            await self.update_cache("messages")    
        if not self.cache_users:
            await self.update_cache("users")
        if not self.cache_remembered:
            await self.update_cache("remembered")

    @commands.command()
    async def iamrole(self, ctx):
        user = ctx.message.author
        await self.validate_cache()
        role = get(user.guild.roles, id = self.cache_role)
        userRoles = user.roles
        if role in userRoles:
            await ctx.send("You already have that role.")
            return
        try:
            if self.cache_remembered[user]:
                await user.add_roles(role)
                await ctx.send("Here you go!")
        except KeyError:
            try:
                percentage = self.cache_users[user] / self.cache_messages
                await ctx.send( "You're level: " + str(floor(percentage * 10)) )
            except KeyError or ZeroDivisionError:
                await ctx.send("Please send more messages.")

    @commands.group()
    @commands.has_permissions(manage_messages = True)
    async def autorole(self, ctx):
        """Base command. Check the subcommands."""
        pass

    @autorole.command()
    async def reset(self, ctx):
        await self.config.clear_all()
        await self.update_cache("role")
        await self.update_cache("messages")
        await self.update_cache("users")
        await self.update_cache("remembered")
        await ctx.send("Done!")

    async def generic_add(self, type, content):
        await self.config.set_raw(type, value = content)
        await self.update_cache(type, content)

    @autorole.command(name = "setup")
    async def setup(self, ctx, roleID, messages):
        """Insert the ID of the role and the amount of messages that you'd want for it to be given."""
        await self.generic_add("role", int(roleID))
        await self.generic_add("messages", int(messages))
        await ctx.send("Setup complete.") 

    @autorole.group(name = "edit")
    async def edit(self, ctx):
        """Edit the ID of the role or the amount of messages."""
        pass

    @edit.command(name = "role")
    async def role(self, ctx, roleID):
        await self.generic_add("role", int(roleID))

    @edit.command(name = "messages")
    async def messages(self, ctx, messages):
        await self.generic_add("messages", int(messages))

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        user = message.author
        if user.bot:
            return
        await self.validate_cache()
        try:
            remembered = self.cache_remembered[user] 
        except KeyError:
            remembered = False        
        userRoles = user.roles
        role = get(user.guild.roles, id = self.cache_role)
        if role in userRoles or not role or remembered:
            return
        try:
            self.cache_users[user] += 1 
        except KeyError:
            self.cache_users[user] = 1
        if self.cache_users[user] >= self.cache_messages:
            self.cache_users.pop(user)
            await user.add_roles(role)
            self.cache_remembered[user] = True
            await self.generic_add("remembered", self.cache_remembered)
        await self.generic_add("users", self.cache_users)
   
    @commands.Cog.listener()
    async def on_member_ban(self, guild, user):
        await self.validate_cache()
        try:
            self.cache_users.pop(user)
            await self.config.set_raw("users", value = self.cache_users)
        except KeyError:
            pass
        try:
            self.cache_remembered.pop(user)
            await self.config.set_raw("remembered", value = self.cache_remembered)
        except KeyError:
            pass