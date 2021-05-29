from redbot.core import commands, Config
import discord
import random
import re


class Regfilter(commands.Cog):
    """Uses a REGEX expression to filter bad words.
    Includes by default some very used slurs."""
    def __init__(self):
        self.config = Config.get_conf(self, identifier = 38927046139453664535446215365606156952951)
        default_global = {
                            "regex": [  
                                        "(?i)\\b[gğ]+\\s*[oø0ö@]+\\s*[oø0ö@]+[\\soø0ö@]*k",                                                         
                                        "(?i)\\bk+\\s*[iïl1y!]+[\\siïl1y!]*k+[\\sk]*[e3]",            
                                        "(?i)\\bj+\\s*[@4aáäÄæÆ]+[\\s@4aáäÄæÆ]*p+[\\sp]*s?\\b",  
                                        "(?i)\\bc+\\s*h+[\\sh]*[iïl1y!]+[\\siïl1y!]*n+[\\sn]*k",        
                                        "(?i)\\bn+\\s*[e3]+[\\se3]*[gğ]+[\\sgğ]*r+[\\sr]*[oø0ö@]",  
                                        "(?i)\\b[szϟ]+\\s*p+[\\sp]*[iïl1y!]+[\\siïl1y!]*[ck]+[\\sck]*s?\\b",      
                                        "(?i)\\bn+\\s*[iïl1y!]+[\\siïl1y!]*[gğ]+\\s*[gğ]+[\\sgğ]*[e3]+[\\se3]*r",  
                                        "(?i)\\bt+\\s*r+[\\sr]*[@4aáäÄæÆ]+[\\s@4aáäÄæÆ]*n+\\s*n+[\\sn]*[iïl1y!]",
                                        "(?i)f+\\s*[@4aáäÄæÆ]+[\\s@4aáäÄæÆ]*[gğ]+\\s*[\\sgğ]*s?\\b|f+\\s*[@4aáäÄæÆ]+[\\s@4aáäÄæÆ]*[gğ]+\\s*[gğ]+[\\sgğ]*[oø0ö@]+[\\soø0ö@]*t"
                                     ],
                            "names": ["Michael"],
                            "ignore":[]
                         }
        self.config.register_global(**default_global)

    @commands.group()
    @commands.has_permissions(manage_messages = True)
    async def filter(self, ctx: commands.Context):
        """Base command. Check the subcommands."""
        pass

    @filter.group(name = "reset", invoke_without_command = True)
    async def _reset(self, ctx: commands.Context, *, confirmation):
        """If you call it by adding a yes at the end it will reset the current regex 
        and name values to the default values."""
        if confirmation.lower() == "yes":
            await self.config.clear_all()   
            await ctx.send("Reset to default values complete.") 
            return
        await ctx.send("Reset cancelled. If you want to reset type in YES or yes.")

    @filter.group(name = "add")
    async def add(self, ctx: commands.Context):
        """Base command. Can add a regex, a name or a word to ignore."""
        pass

    @add.command(name = "regex")
    async def add_regex(self, ctx, *, msg):
        """Adds a regex to the list."""
        async with self.config.regex() as regex:
            regex.append(msg)
        await ctx.send("The new regex has been added.")

    @add.command(name = "name")
    async def add_name(self, ctx, *, msg):
        """Adds a name to the list of default names. Applied when filtering a name."""
        async with self.config.names() as names:
            names.append(msg)
        await ctx.send("The new name has been added.")

    @add.command(name = "ignore")
    async def add_ignore(self, ctx, *, msg):
        """Adds a word to ignore to the list of ignored words."""
        async with self.config.ignore() as ignore:
            ignore.append( "(?i)" + msg )
        await ctx.send("The new word has been added.")

    @filter.group(name = "delete")
    async def delete(self, ctx: commands.Context):
        """Base command. Can either remove a regex or a name."""
        pass

    @delete.command(name = "regex")
    async def delete_regex(self, ctx, *, msg):
        """Removes a regex from the list."""
        try:
            async with self.config.regex() as regex:
                regex.remove(msg)
            await ctx.send("Regex removed successfully.")
        except:
            await ctx.send("Couldn't find that regex in the list.")

    @delete.command(name = "name")
    async def delete_name(self, ctx, *, msg):
        """Removes a name from the list."""
        try:
            async with self.config.names() as names:
                names.remove(msg)
            await ctx.send("Name removed successfully.")
        except:
            await ctx.send("Couldn't find that name in the list.")

    @delete.command(name = "ignore")
    async def delete_ignore(self, ctx, *, msg):
        """Removes an ignored word from the list."""
        try:
            async with self.config.ignore() as ignore:
                ignore.remove( "(?i)" + msg )
            await ctx.send("Ignored word removed successfully.")
        except:
            await ctx.send("Couldn't find that word in the list.")

    @filter.group(name = "list")
    async def listThings(self, ctx: commands.Context):
        """Base command. Can either send the list of regex or names."""

    @listThings.command(name = "regex")
    async def list_regex(self, ctx):
        """Sends the regex list through DMs."""
        try:
            user = ctx.message.author
            list = await self.config.regex()
            prettyList = "\n".join(list)
            prettyList = "```" + prettyList + "```"
            await user.send(prettyList)
        except:
            await ctx.send("ERROR: Open your DMs.")

    @listThings.command(name = "names")
    async def list_names(self, ctx):
        """Sends the names list through DMs."""
        try:
            user = ctx.message.author
            list = await self.config.names()
            prettyList = "\n".join(list)
            await user.send(prettyList)
        except:
            await ctx.send("ERROR: Open your DMs.")

    @listThings.command(name = "ignored")
    async def list_ignored(self, ctx):
        """Sends the ignored word list through DMs."""
        try:
            user = ctx.message.author
            list = await self.config.ignore()
            prettyList = "\n".join(list)
            await user.send(prettyList)
        except:
            await ctx.send("ERROR: Open your DMs.")
    
    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        author = message.author
        content = message.content
        patterns = await self.config.regex()
        ignore = await self.config.ignore()
        if author.bot:
            return
        if ( await self.triggered_filter(content, patterns) and not await self.triggered_filter(content, ignore) ):
            await message.delete()
    
    async def triggered_filter(self, content, patterns):
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
        patterns = await self.config.regex()
        ignore = await self.config.ignore()
        if ( await self.triggered_filter(member.display_name, patterns) and not await self.triggered_filter(member.display_name, ignore) ):
            names = await self.config.names()
            try:
                name = random.choice(names)
                await member.edit(nick = name, reason = "Filtered username")
            except discord.HTTPException:
                pass
            return