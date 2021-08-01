from redbot.core import commands, Config
import discord
from discord.utils import get
class Autorole(commands.Cog):
    """Automatically hands out a single role you can setup beforehand."""
    def __init__(self):
        self.config = Config.get_conf(self, identifier = 343434651171161111099711610599971)
        default_global = {
                            "role": None,
                            "messages": 100,
                            "users": {}
                         }
        self.config.register_global(**default_global)
        self.cache_role = None
        self.cache_messages = 0
        self.cache_users = {}

    async def return_cache(self, type: str):
        if type == "role":
            return self.cache_role
        elif type == "messages":
            return self.cache_messages
        elif type == "users":
            return self.cache_users

    async def update_cache(self, type: str, content = None):
        if type == "role":
            self.cache_role = content if content else await self.config.role()
        elif type == "messages":
            self.cache_messages = content if content else await self.config.messages()
        elif type == "users":
            self.cache_users = content if content else await self.config.users()
        elif type == "all":
            await self.update_cache("role")
            await self.update_cache("messages")
            await self.update_cache("users")

    async def validate_cache(self):
        if self.cache_role == []: 
            await self.update_cache("role")
        if self.cache_users == []:
            await self.update_cache("messages")    
        if self.cache_users == []:
            await self.update_cache("users")

    @commands.group()
    @commands.has_permissions(manage_messages = True)
    async def autorole(self, ctx):
        """Base command. Check the subcommands."""
        pass

    async def generic_add(self, type, content):
        await self.config.set_raw(type, content)
        await self.update_cache(type, content)

    @autorole.command(name = "setup")
    async def setup(self, ctx, roleID, messages):
        """Insert the ID of the role and the amount of messages that you'd want for it to be given."""
        await self.generic_add("role", int(roleID))
        await self.generic_add("messages", messages)
        await ctx.send("Setup complete.") 

    @autorole.group(name = "edit")
    async def edit(self, ctx, roleID, messages):
        """Edit the ID of the role or the amount of messages."""
        pass

    @edit.command(name = "role")
    async def role(self, ctx, roleID):
        await self.generic_add("role", roleID)

    @edit.command(name = "messages")
    async def role(self, ctx, messages):
        await self.generic_add("messages", messages)

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        user = message.author
        if user.bot:
            return
        userRoles = user.roles
        await self.validate_cache()
        role = get(user.guild.roles, id = self.cache_role)
        if role in userRoles:
            return
        try:
            self.cache_users[user] += 1
        except KeyError:
            self.cache_users[user] = 0
        finally:
            if self.cache_users[user] >= self.cache_messages:
                self.cache_users = self.cache_users.pop(user)
                await user.add_roles(role)
                await self.generic_add("users", self.cache_users)