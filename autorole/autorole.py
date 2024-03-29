from redbot.core import commands, Config
from discord.utils import get
from math import floor
import discord

class Autorole(commands.Cog):
    """Automatically hands out a single role that you can setup beforehand."""
    def __init__(self, bot):
        self.bot = bot
        self.config = Config.get_conf(self, identifier = 343434651171161111099711610599971)
        default_global = {
                            "role": None,
                            "messages": 0,
                         }
        self.config.register_global(**default_global)
        self.config.register_member(messages = 0, remembered = False)
        self.cache_role = None
        self.cache_messages = 0
        self.bot.loop.create_task(self.validate_cache())

    async def update_cache(self, type: str, content = None):
        value = content if content else await self.config.get_raw(type)
        if type == "role":
            self.cache_role = value
        elif type == "messages":
            self.cache_messages = value
        
    async def validate_cache(self):
        if not self.cache_role: 
            await self.update_cache("role")
        if not self.cache_messages:
            await self.update_cache("messages")

    @commands.command()
    async def iamrole(self, ctx):
        user = ctx.message.author
        messages = await self.config.member(user).messages()
        remembered = await self.config.member(user).remembered()
        role = get(user.guild.roles, id = self.cache_role)
        if not role:
            await ctx.send("I've not been set up yet. Sorry!")
            return
        userRoles = user.roles    
        if role in userRoles:
            await ctx.send("You already have that role.")
            return
        if remembered:
            await user.add_roles(role)
            await ctx.send("Here you go!")
        else:
            percentage = messages / self.cache_messages
            await ctx.send( "You're level: " + str(floor(percentage * 10)) )

    @commands.group()
    @commands.has_permissions(manage_messages = True)
    async def autorole(self, ctx):
        """Base command. Check the subcommands."""
        pass

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
        await ctx.send("Edited the role successfully.")

    @edit.command(name = "messages")
    async def messages(self, ctx, messages):
        await self.generic_add("messages", int(messages))
        await ctx.send("Edited the message amount successfully.")
    
    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        user = message.author
        remembered = await self.config.member(user).remembered()
        if user.bot or not self.cache_role or remembered:
            return
        role = get(user.guild.roles, id = self.cache_role)
        maxMessages = await self.config.messages()
        messages = await self.config.member(user).messages()
        messages += 1
        await self.config.member(user).messages.set(messages)
        if messages >= maxMessages:
            await user.add_roles(role)
            await self.config.member(user).remembered.set(True)

    @commands.Cog.listener()
    async def on_member_ban(self, guild, user):
        await self.config.member(user).clear()  

    @commands.Cog.listener()
    async def on_member_remove(self, guild, user):
        await self.config.member(user).messages.set(0)  