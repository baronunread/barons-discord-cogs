from redbot.core import commands, Config
import discord
import random
import re


class Regfilter(commands.Cog):
    """Uses a REGEX expression to filter bad words."""
    def __init__(self):
        self.config = Config.get_conf(self, identifier = 38927046139453664535446215365606156952951)
        default_global = {
                            "regex": [
                                      '(?i)g+[\\s+o0]{2,}k',
                                      '(?i)f+[\\s+@4aáäÄæÆ]+g',
                                      '(?i)j+[\\s+@4aáäÄæÆ]+p',
                                      '(?i)[ϟs]+[\\s+p]+[\\s+iïl1y]+c',
                                      '(?i)k+[\\s+iïl1y]+[\\s+k]+[e3]',
                                      '(?i)c+[\\s+h]+[\\s+iïl1y]+[\\s+n]+k',
                                      '(?i)n+[\\s+e3]+[\\s+gğq]+[\\s+r]+[o0]',
                                      '(?i)n+[\\s+iïl1y]+[\\s+gğq]{2,}[\\s+e3]+r',
                                      '(?i)t+[\\s+r]+[\\s+@4aáäÄæÆ]+[\\s+n]+[iïl1y]'
                                     ],
                            "names": [
                                      "Michael", "James"  
                                     ]
                         }
        self.config.register_global(**default_global)
        self.cache_regex = self.config.regex()
        self.cache_names = self.config.names()

    @commands.group()
    @commands.has_permissions(manage_messages = True)
    async def filter(self, ctx: commands.Context):
        """Base command. Check the subcommands."""
        pass

    @filter.group(name = "add")
    async def add(self, ctx: commands.Context):
        """Base command. Can either add a regex or a name."""
        pass

    @add.command(name = "regex")
    async def add_regex(self, ctx: commands.Context, *, msg):
        """Adds a REGEX to the list."""
        async with self.config.regex() as regex:
            regex.append(msg)
            self.cache_regex = regex
        await ctx.send("The new REGEX has been added.")

    @add.command(name = "name")
    async def add_name(self, ctx: commands.Context, *, msg):
        """Adds a name to the list of default names. Applied when filtering a name."""
        async with self.config.names() as names:
            names.append(msg)
            self.cache_names = names
        await ctx.send("The new name has been added.")

    @filter.group(name = "delete")
    async def delete(self, ctx: commands.Context):
        """Base commands. Can either remove a regex or a name."""
        pass

    @delete.command(name = "regex")
    async def delete_regex(self, ctx: commands.Context, *, msg):
        """Removes a REGEX from the list."""
        try:
            async with self.config.regex() as regex:
                regex.remove(msg)
                self.cache_regex = regex
            await ctx.send("REGEX removed successfully.")
        except:
            await ctx.send("Couldn't find that REGEX in the list.")

    @delete.command(name = "name")
    async def delete_name(self, ctx: commands.Context, *, msg):
        """Removes a name from the list."""
        try:
            async with self.config.names() as names:
                names.remove(msg)
                self.cache_names = names
            await ctx.send("Name removed successfully.")
        except:
            await ctx.send("Couldn't find that name in the list.")

    @filter.group(name = "list")
    async def listThings(self, ctx: commands.Context):
        """Base command. Can either send the list of names or REGEX."""

    @listThings.command(name = "regex")
    async def list_regex(self, ctx: commands.Context):
        """Sends the REGEX list through DMs."""
        try:
            user = ctx.message.author
            list = self.cache_regex
            prettyList = "\n".join(list)
            await user.send(prettyList)
        except:
            await ctx.send("ERROR: Open your DMs.")

    @listThings.command(name = "names")
    async def _list(self, ctx: commands.Context):
        """Sends the names list through DMs."""
        try:
            user = ctx.message.author
            list = self.cache_names
            prettyList = "\n".join(list)
            await user.send(prettyList)
        except:
            await ctx.send("ERROR: Open your DMs.")
    
    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        author = message.author
        content = message.content
        if author.bot:
            return
        if await self.triggered_filter(content):
            await message.delete()
    
    async def triggered_filter(self, content):
        patterns = self.cache_regex
        for pattern in patterns:
            result = re.findall(pattern, content)
            if ( result != [] ):
                return True
        return False

    @commands.Cog.listener()
    async def on_message_edit(self, _prior, message):
        await self.on_message(message)

    @commands.Cog.listener()
    async def on_member_update(self, before: discord.Member, after: discord.Member):
        if before.display_name != after.display_name:
            await self.maybe_filter_name(after)

    @commands.Cog.listener()
    async def on_member_join(self, member: discord.Member):
        await self.maybe_filter_name(member)

    async def maybe_filter_name(self, member: discord.Member):
        if await self.triggered_filter(member.display_name):
            names = self.cache_names
            try:
                name = random.choice(names)
                await member.edit(nick = name, reason = "Filtered username")
            except discord.HTTPException:
                pass
            return