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
                                        r"(?i)\bj+\s*a+[\sa]*p+[\sp]*s?\b",
                                        r"(?i)\bf+\s*a+[\sa]*g|\b\w*f+a+g",
                                        r"(?i)\bs+\s*p+[\sp]*i+[\si]*c+[\sc]*s?\b",
                                        r"(?i)\bg+\s*o+\s*o+[\so]*k|\b\w*g+o{2,}k",
                                        r"(?i)\bk+\s*i+[\si]*k+[\sk]*e|\b\w*k+i+k+e",
                                        r"(?i)\bn+\s*e+[\se]*g+[\sg]*r+[\sr]*o|\b\w*n+e+g+r+o",
                                        r"(?i)\bc+\s*h+[\sh]*i+[\si]*n+[\sn]*k|\b\w*c+h+i+n+k",
                                        r"(?i)\bn+\s*[il]+[\sil]*g+\s*g+[\sg]*e+[\se]*r|\b\w*n+[il]+g{2,}e+r",
                                        r"(?i)\bt+\s*r+[\sr]*a+[\sa]*n+\s*n+[\sn]*[iy]|\b\w*t+r+a+n{2,}[iy]"
                                     ],
                            "names": [],
                            "ignore":[
                                        r"(?i)\bhttp[^' ']*"
                                     ]
                         }
        self.config.register_global(**default_global)
        self.cache_regex = []
        self.cache_names = []
        self.cache_ignore = []
        self.leet_dict =    {
                                "@":"a",
                                "4":"a",
                                "æ":"a", 
                                "Æ":"a",
                                "3":"e",
                                "Ε":"e", #Greek E
                                "1":"i",
                                "!":"i",
                                "ø":"o",
                                "0":"o",
                                "ο":"o", #Greek o
                                "η":"n",
                                "ϟ":"s"
                            }

    async def replace(self, msg):
        nfkd_form = unicodedata.normalize('NFKD', msg)
        cleaned = u"".join([c for c in nfkd_form if not unicodedata.combining(c)])
        for toReplace in self.leet_dict:
            cleaned = cleaned.replace(toReplace, self.leet_dict[toReplace])
        alpha = ''.join(c for c in cleaned if c.isalpha() or c == ' ')
        for ignore in self.cache_ignore:
            alpha = re.sub(ignore, '', alpha)
        return alpha

    async def return_cache(self, type: str):
        if type == "regex":
            return self.cache_regex
        elif type == "names":
            return self.cache_names
        elif type == "ignore":
            return self.cache_ignore

    async def update_cache(self, type, content = None):
        if type == "regex":
            self.cache_regex = content if content else await self.config.regex()
        elif type == "names":
            self.cache_names = content if content else await self.config.names()
        elif type == "ignore":
            self.cache_ignore = content if content else await self.config.ignore()
        elif type == "all":
            await self.update_cache("regex")
            await self.update_cache("names")
            await self.update_cache("ignore")

    async def validate_cache(self):
        if self.cache_regex == []: 
            await self.update_cache("regex")
        if self.cache_ignore == []:
            await self.update_cache("names")    
        if self.cache_ignore == []:
            await self.update_cache("ignore")

    @commands.group()
    @commands.has_permissions(manage_messages = True)
    async def filter(self, ctx: commands.Context):
        """Base command. Check the subcommands."""
        pass

    @filter.group(name = "reset", invoke_without_command = True)
    async def _reset(self, ctx: commands.Context, *, type):
        """Reset regex, names, ignore or all by typing out what to reset."""
        typed = type.lower()
        if typed == "regex" or typed == "ignore" or typed == "names":
            await self.config.clear_raw(typed) 
        elif typed == "all":
            await self.config.clear_all() 
        else:
            await ctx.send("Reset cancelled. If you want to reset something type in REGEX, NAMES, IGNORE or ALL.")
            return
        await self.update_cache(type)
        await ctx.send("Reset complete.")

    @filter.group(name = "add")
    async def add(self, ctx: commands.Context):
        """Base command. Can add a regex, a name for replacing or a word to ignore."""
        pass

    async def generic_add(self, ctx, msg, type: str):
        await self.validate_cache()
        list = await self.return_cache(type)
        list = list.append(msg)
        await self.config.set_raw(type, value = list)
        await self.update_cache(type, content = list)
        await ctx.send("The new item has been added.")


    @add.command(name = "regex")
    async def add_regex(self, ctx, *, msg):
        """Adds a regex to the list."""
        await self.generic_add(ctx, msg, "regex")

    @add.command(name = "name")
    async def add_name(self, ctx, *, msg):
        """Adds a name to the list of default names. Applied when filtering a name."""
        await self.generic_add(ctx, msg, "names")

    @add.command(name = "ignore")
    async def add_ignore(self, ctx, *, msg):
        """Adds a word to ignore to the list of ignored words."""
        await self.generic_add(ctx, "(?i)" + msg, "ignore")

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
                self.cache_regex = regex
            await ctx.send("Regex removed successfully.")
        except:
            await ctx.send("Couldn't find that regex in the list.")

    @delete.command(name = "name")
    async def delete_name(self, ctx, *, msg):
        """Removes a name from the list."""
        try:
            async with self.config.names() as names:
                names.remove(msg)
                self.cache_names = names
            await ctx.send("Name removed successfully.")
        except:
            await ctx.send("Couldn't find that name in the list.")

    @delete.command(name = "ignore")
    async def delete_ignore(self, ctx, *, msg):
        """Removes an ignored word from the list."""
        try:
            async with self.config.ignore() as ignore:
                ignore.remove( "(?i)" + msg )
                self.cache_ignore = ignore
            await ctx.send("Ignored word removed successfully.")
        except:
            await ctx.send("Couldn't find that word in the list.")

    @filter.group(name = "list")
    async def listThings(self, ctx: commands.Context):
        """Base command. Can either send the list of regex, names or ignored words."""
        pass

    async def generic_list(self, ctx, user, type: str):
        try:
            await self.validate_cache()    
            list = await self.return_cache(type)
            if len(list) == 0:
                await user.send("There's nothing in that list.")
                return
            prettyList = "\n".join(list)
            if type == "regex":
                prettyList = "```" + prettyList + "```"
            await user.send(prettyList)
        except:
            await ctx.send("ERROR: Open your DMs.")

    @listThings.command(name = "regex")
    async def list_regex(self, ctx):
        """Sends the regex list through DMs."""
        await self.generic_list(ctx, ctx.message.author, "regex")

    @listThings.command(name = "names")
    async def list_names(self, ctx):
        """Sends the names list through DMs."""
        await self.generic_list(ctx, ctx.message.author, "names")

    @listThings.command(name = "ignore")
    async def list_ignored(self, ctx):
        """Sends the ignored word list through DMs."""
        await self.generic_list(ctx, ctx.message.author, "ignore")
    
    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        author = message.author
        if author.bot:
            return
        await self.validate_cache()    
        content = await self.replace(message.clean_content)
        regexs = await self.return_cache("regex")
        if await self.triggered_filter(content, regexs):
            await message.delete()
    
    async def triggered_filter(self, content, regexs):
        for regex in regexs:
            result = re.findall(regex, content)
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
        await self.validate_cache()
        content = await self.replace(member.display_name)
        regex = await self.return_cache("regex")
        if await self.triggered_filter(content, regex):
            names = await self.return_cache("names")
            try:
                name = random.choice(names)
                await member.edit(nick = name, reason = "Filtered username")
            except discord.HTTPException:
                pass
            except IndexError:
                return