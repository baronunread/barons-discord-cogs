from redbot.core import commands, Config
import discord
import unicodedata
import random
import re

class Regfilter(commands.Cog):
    """Uses a REGEX expression to filter bad words.
    Includes by default some very used slurs."""
    def __init__(self):
        self.config = Config.get_conf(self, identifier = 38927046139453664535446215365606156952951)
        default_global = {
                            "regex": [  
                                        "(?i)\\bg+\\s*[oø0@]+\\s*[oø0@]+[\\soø0@]*k",                                                         
                                        "(?i)\\bk+\\s*[i1y!]+[\\si1y!]*k+[\\sk]*[e3]",            
                                        "(?i)\\bj+\\s*[@4aæÆ]+[\\s@4aæÆ]*p+[\\sp]*s?\\b",
                                        "(?i)\\bf+\\s*[@4aæÆ]+[\\s@4aæÆ]*g+\\s*[\\sg]*s?",  
                                        "(?i)\\bc+\\s*h+[\\sh]*[il1y!]+[\\sil1y!]*[nη]+[\\snη]*k",        
                                        "(?i)\\b[nη]+\\s*[e3]+[\\se3]*g+[\\sg]*r+[\\sr]*[oø0@]",  
                                        "(?i)\\b[szϟ]+\\s*p+[\\sp]*[il1y!]+[\\sil1y!]*[ck]+[\\sck]*s?\\b",      
                                        "(?i)\\b[nη]+\\s*[il1y!]+[\\sil1y!]*g+\\s*g+[\\sg]*[e3]+[\\se3]*r",  
                                        "(?i)\\bt+\\s*r+[\\sr]*[@4aæÆ]+[\\s@4aæÆ]*[nη]+\\s*[nη]+[\\snη]*[il1y!]"
                                     ],
                            "names": [],
                            "ignore":[]
                         }
        self.config.register_global(**default_global)
        self.cache_pattern = []
        self.cache_ignored = []

    async def replace(self, msg):
        text = discord.utils.remove_markdown(msg)
        nfkd_form = unicodedata.normalize('NFKD', text)
        return u"".join([c for c in nfkd_form if not unicodedata.combining(c)])

    async def updateCache(self, type):
        if type == 'pattern':
            self.cache_pattern = await self.config.regex()
        elif type == 'ignored':
            self.cache_ignored = await self.config.ignore()

    async def validateCache(self):
        if self.cache_pattern == []: 
            await self.updateCache('pattern')
        if self.cache_ignored == []:
            await self.updateCache('ignored')

    @commands.group()
    @commands.has_permissions(manage_messages = True)
    async def filter(self, ctx: commands.Context):
        """Base command. Check the subcommands."""
        pass

    @filter.group(name = "reset", invoke_without_command = True)
    async def _reset(self, ctx: commands.Context, *, confirmation):
        """If you call it by adding a yes at the end it will reset the current regex,name and
        ignored values to the default values."""
        if confirmation.lower() == "yes":
            await self.config.clear_all() 
            await self.updateCache('pattern')
            await self.updateCache('ignored')  
            await ctx.send("Reset to default values complete.") 
            return
        await ctx.send("Reset cancelled. If you want to reset type in YES or yes.")

    @filter.group(name = "add")
    async def add(self, ctx: commands.Context):
        """Base command. Can add a regex, a name for replacing or a word to ignore."""
        pass

    @add.command(name = "regex")
    async def add_regex(self, ctx, *, msg):
        """Adds a regex to the list."""
        async with self.config.regex() as regex:
            regex.append(msg)
            self.cache_pattern = regex
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
            self.cache_ignored = ignore
        await ctx.send("The new word has been added.")

    @filter.group(name = "delete")
    async def delete(self, ctx: commands.Context):
        """Base command. Can either remove a regex, name or ignored word."""
        pass

    @delete.command(name = "regex")
    async def delete_regex(self, ctx, *, msg):
        """Removes a regex from the list."""
        try:
            async with self.config.regex() as regex:
                regex.remove(msg)
                self.cache_pattern = regex
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
                self.cache_ignored = ignore
            await ctx.send("Ignored word removed successfully.")
        except:
            await ctx.send("Couldn't find that word in the list.")

    @filter.group(name = "list")
    async def listThings(self, ctx: commands.Context):
        """Base command. Can either send the list of regex, names or ignored words."""

    @listThings.command(name = "regex")
    async def list_regex(self, ctx):
        """Sends the regex list through DMs."""
        try:
            user = ctx.message.author
            if self.cache_pattern == []:
                await self.updateCache('pattern')
            list = self.cache_pattern
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
            if self.cache_ignored == []:
                await self.updateCache('ignored')
            list = self.cache_ignored
            prettyList = "\n".join(list)
            await user.send(prettyList)
        except:
            await ctx.send("ERROR: Open your DMs.")
    
    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        author = message.author
        content = await self.replace(message.content)
        await self.validateCache()
        patterns = self.cache_pattern
        ignore = self.cache_ignored
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
        content = await self.replace(member.display_name)
        await self.validateCache()
        patterns = self.cache_pattern
        ignore = self.cache_ignored
        if ( await self.triggered_filter(content, patterns) and not await self.triggered_filter(content, ignore) ):
            names = await self.config.names()
            try:
                name = random.choice(names)
                await member.edit(nick = name, reason = "Filtered username")
            except discord.HTTPException:
                pass
            return