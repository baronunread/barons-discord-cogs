from redbot.core import commands, Config
import discord

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
        self.cache_messages = None
        self.cache_users = {}

    async def return_cache(self, type: str):
        if type == "role":
            return self.cache_role
        elif type == "messages":
            return self.cache_messages
        elif type == "users":
            return self.cache_users

    async def update_cache(self, type, content = None):
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

    @commands.command()
    async def test(self, ctx, userID):
        users = await self.config.get_raw("users")
        users[userID] = 0
        await self.update_cache("users", users)

    @commands.group()
    @commands.has_permissions(manage_messages = True)
    async def autorole(self, ctx):
        """Base command. Check the subcommands."""
        pass

    @autorole.group(name = "setup")
    async def setup(self, ctx, roleID, messages):
        """Insert the ID of the role and the amount of messages that you'd want for it to be given."""
        pass