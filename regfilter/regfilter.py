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
                                        r"(?i)\bj+\s*[@4aæÆ]+[\s@4aæÆ]*p+[\sp]*s?\b",
                                        r"(?i)\bf+\s*[@4aæÆ]+[\s@4aæÆ]*g|\b\w*f+[@4aæÆ]+g",
                                        r"(?i)\b[szϟ]+\s*p+[\sp]*[il1y!]+[\sil1y!]*[ck]+[\sck]*s?\b",
                                        r"(?i)\bg+\s*[oø0@ο]+\s*[oø0@ο]+[\soø0@ο]*k|\b\w*g+[oø0@ο]{2,}k",
                                        r"(?i)\bk+\s*[i1y!]+[\si1y!]*k+[\sk]*[e3Ε]|\b\w*k+[i1y!]+k+[e3Ε]",
                                        r"(?i)\b[nη]+\s*[e3Ε]+[\se3Ε]*g+[\sg]*r+[\sr]*[oø0@ο]|\b\w*[nη]+[e3Ε]+g+r+[oø0@ο]",
                                        r"(?i)\bc+\s*h+[\sh]*[il1y!]+[\sil1y!]*[nη]+[\snη]*k|\b\w*c+h+[il1y!]+[nη]+k",
                                        r"(?i)\b[nη]+\s*[il1y!]+[\sil1y!]*g+\s*g+[\sg]*[e3Ε]+[\se3Ε]*r|\b\w*[nη]+[il1y!]+g{2,}[e3Ε]+r",
                                        r"(?i)\bt+\s*r+[\sr]*[@4aæÆ]+[\s@4aæÆ]*[nη]+\s*[nη]+[\snη]*[il1y!]|\b\w*t+r+[@4aæÆ]+[nη]{2,}[il1y!]"
                                     ],
                            "names": [],
                            "ignore":[]
                         }
        self.config.register_global(**default_global)
        self.cache_pattern = []
        self.cache_ofnames = []
        self.cache_ignored = []
        self.leet_dict =    {
                                
                            }

    async def de_leetspeak(self, msg):
        pass

    @commands.command()
    async def test(self, ctx, *, msg):
        await ctx.send( await self.replace(msg.clean_content) )
        if( 'Æ'.isalpha() ):
            await ctx.send( "Æ is alpha!!" )

    async def replace(self, msg):
        #text = discord.utils.remove_markdown(msg)
        nfkd_form = unicodedata.normalize('NFKD', msg)
        cleaned = u"".join([c for c in nfkd_form if not unicodedata.combining(c)])
        alpha = ''.join(c for c in cleaned if c.isalpha() or c == ' ')
        for ignore in self.cache_ignored:
            alpha = re.sub(ignore, '', alpha)
        alpha = re.sub(r"http[^' ']*", '', alpha)
        return alpha

    async def updateCache(self, type):
        if type == 'pattern':
            self.cache_pattern = await self.config.regex()
            return self.cache_pattern
        elif type == 'names':
            self.cache_ofnames = await self.config.names()
            return self.cache_ofnames
        elif type == 'ignored':
            self.cache_ignored = await self.config.ignore()
            return self.cache_ignored

    async def validateCache(self):
        if self.cache_pattern == []: 
            await self.updateCache('pattern')
        if self.cache_ignored == []:
            await self.updateCache('names')    
        if self.cache_ignored == []:
            await self.updateCache('ignored')

    @commands.group()
    @commands.has_permissions(manage_messages = True)
    async def filter(self, ctx: commands.Context):
        """Base command. Check the subcommands."""
        pass

    @filter.group(name = "reset", invoke_without_command = True)
    async def _reset(self, ctx: commands.Context, *, type):
        """Reset regex, names, ignored or all by typing out what to reset."""
        if type.lower() == "regex":
            await self.config.clear_raw("regex") 
            await self.updateCache('pattern')
        elif type.lower() == "ignored":
            await self.config.clear_raw("ignore")
            await self.updateCache('ignored')
        elif type.lower() == "names":
            await self.config.clear_raw("names")
            await self.updateCache('names')
        elif type.lower() == "all":
            await self.config.clear_all()      
        else:
            await ctx.send("Reset cancelled. If you want to reset something type in REGEX, NAMES, IGNORED or ALL.")
            return
        await ctx.send("Reset complete.")

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
            self.cache_ofnames = names
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
                self.cache_ofnames = names
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
        pass

    async def generic_list(self, ctx, user, type: str):
        try:    
            list = await self.updateCache(type)
            if len(list) == 0:
                await user.send("There's nothing in that list.")
                return
            prettyList = "\n".join(list)
            if type == "pattern":
                prettyList = "```" + prettyList + "```"
            await user.send(prettyList)
        except:
            await ctx.send("ERROR: Open your DMs.")

    @listThings.command(name = "regex")
    async def list_regex(self, ctx):
        """Sends the regex list through DMs."""
        await self.generic_list(ctx, ctx.message.author, "pattern")

    @listThings.command(name = "names")
    async def list_names(self, ctx):
        """Sends the names list through DMs."""
        await self.generic_list(ctx, ctx.message.author, "names")

    @listThings.command(name = "ignored")
    async def list_ignored(self, ctx):
        """Sends the ignored word list through DMs."""
        await self.generic_list(ctx, ctx.message.author, "ignored")
    
    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        author = message.author
        if author.bot:
            return
        await self.validateCache()    
        content = await self.replace(message.clean_content)
        patterns = self.cache_pattern
        if await self.triggered_filter(content, patterns):
            await message.delete()
    
    async def triggered_filter(self, content, patterns):
        for pattern in patterns:
            result = re.findall(pattern, content)
            if result != []:
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
        await self.validateCache()
        content = await self.replace(member.display_name)
        patterns = self.cache_pattern
        if await self.triggered_filter(content, patterns):
            names = self.cache_ofnames
            try:
                name = random.choice(names)
                await member.edit(nick = name, reason = "Filtered username")
            except discord.HTTPException:
                pass
            return