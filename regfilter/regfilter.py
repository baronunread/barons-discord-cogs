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
                                        r"\bj+\s*a+[\sa]*p+[\sp]*s?\b",
                                        r"\bf+\s*a+[\sa]*g|\b\w*f+a+g",
                                        r"\bs+\s*p+[\sp]*i+[\si]*c+[\sc]*s?\b",
                                        r"\bg+\s*o+\s*o+[\so]*k|\b\w*g+o{2,}k",
                                        r"\bk+\s*i+[\si]*k+[\sk]*e|\b\w*k+i+k+e",
                                        r"\bn+\s*e+[\se]*g+[\sg]*r+[\sr]*o|\b\w*n+e+g+r+o",
                                        r"\bc+\s*h+[\sh]*i+[\si]*n+[\sn]*k|\b\w*c+h+i+n+k",
                                        r"\bn+\s*[il]+[\sil]*g+\s*g+[\sg]*e+[\se]*r|\b\w*n+[il]+g{2,}e+r",
                                        r"\bt+\s*r+[\sr]*a+[\sa]*n+\s*n+[\sn]*[iy]|\b\w*t+r+a+n{2,}[iy]"
                                     ],
                            "names": [],
                            "ignore":[
                                        r"\bhttp[^' ']*"
                                     ]
                         }
        self.config.register_global(**default_global)
        self.cache_regex = []
        self.cache_names = []
        self.cache_ignore = []
        self.mapping =  {   
                            "a": ["ⱥ","@","4","æ","α","λ","ƛ","δ","σ","а","ҩ"],                                             
                            "c": ["ȼ","с","¢","ƈ","ϲ","ͼ","ҫ"], 
                            "e": ["ɇ","£","€","ҽ","ҿ","ə","з","ӡ","ʒ","3","ҙ","е","э","ε","є","ξ"],
                            "f": ["ꞙ","ƒ","₣","ꬵ","ӻ","ғ"],      
                            "g": ["ǥ","ɠ"],                                          
                            "i": ["1","!","ӏ","ι","ł","ƚ","ɨ","і"], 
                            "j": ["ɉ","ј"],
                            "k": ["ƙ","ĸ","κ","к","ӄ","ҝ","ҟ","ҡ","қ"],                                                                     
                            "n": ["η","ƞ","π","п","л","ɲ","ν","и","ȵ","ŋ"],
                            "o": ["ø","0","ο","ө","о","ѳ"],
                            "p": ["р","ƥ"],
                            "r": ["ɍ","г","ӷ","я"],
                            "s": ["ѕ","ϟ","$","ß"],
                            "t": ["ⱦ","ŧ","ϯ","т","ҭ","ʈ","ƭ","ƫ"],
                            "y": ["ɏ","ч","ӌ","ƴ","у","ҷ"]
                        }
        self.leet_dict = {}
        for key in self.mapping:
            keyDict = dict.fromkeys(self.mapping[key], key)
            self.leet_dict.update(keyDict)


    @commands.command()
    async def test(self, ctx):
        await ctx.send( await discord.utils.remove_markdown(ctx.message) )

    async def replace(self, msg):
        nfkd_form = unicodedata.normalize('NFKD', msg.lower())                              # NFKD form
        noDiacritics = u"".join([c for c in nfkd_form if not unicodedata.combining(c)])     # cleans the rest of the diacritics
        noLookAlikes = await self.clean(noDiacritics)                                       # removes the remaining characters that aren't necessarily of the type ALPHABETIC WITH
        alpha = ''.join(c for c in noLookAlikes if c.isalpha() or c == ' ')                 # remove anything that isn't an alphabetic character or a space
        for ignore in self.cache_ignore:
            alpha = re.sub(ignore, '', alpha)                                               # remove ignored words as they are not important
        return alpha

    async def clean(self, cleaned):
        for toReplace in self.leet_dict:
            cleaned = cleaned.replace(toReplace, self.leet_dict[toReplace])
        return cleaned

    async def return_cache(self, type: str):
        if type == "regex":
            return self.cache_regex
        elif type == "names":
            return self.cache_names
        elif type == "ignore":
            return self.cache_ignore

    async def update_cache(self, type, content = None):
        value = content if content else await self.config.get_raw(type)
        if type == "regex":
            self.cache_regex = value
        elif type == "names":
            self.cache_names = value
        elif type == "ignore":
            self.cache_ignore = value
            
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

    @filter.command(name = "reset")
    async def reset(self, ctx: commands.Context, *, type):
        """Reset regex, names, ignore or all by typing out what to reset."""
        typed = type.lower()
        if typed == "regex" or typed == "ignore" or typed == "names":
            await self.config.clear_raw(typed) 
        elif typed == "all":
            await self.config.clear_all()
            await self.update_cache("regex")
            await self.update_cache("names")
            await self.update_cache("ignore")
            await ctx.send("Reset complete.")
            return
        else:
            await ctx.send("Reset cancelled. If you want to reset something type in REGEX, NAMES, IGNORE or ALL.")
            return
        await self.update_cache(type)
        await ctx.send("Reset complete.")

    @filter.group(name = "add")
    async def add(self, ctx: commands.Context):
        """Base command. Can add a regex, a name for replacing or a word to ignore."""
        pass

    async def generic_add_delete(self, ctx, msg, type: str, operation: str):
        await self.validate_cache()
        list = await self.return_cache(type)
        if operation == "added":
            list.append(msg)
        elif operation == "deleted":
            try:
                list.remove(msg)
            except:
                await ctx.send("Couldn't find that item in the list.")
                return
        await self.config.set_raw(type, value = list)
        await self.update_cache(type, content = list)
        await ctx.send("The new item has been " + operation + ".")

    @add.command(name = "regex")
    async def add_regex(self, ctx, *, msg):
        """Adds a regex to the list."""
        await self.generic_add_delete(ctx, msg, "regex", "added")
        
    @add.command(name = "name")
    async def add_name(self, ctx, *, msg):
        """Adds a name to the list of default names. Applied when filtering a name."""
        await self.generic_add_delete(ctx, msg, "names", "added")

    @add.command(name = "ignore")
    async def add_ignore(self, ctx, *, msg):
        """Adds a word to ignore to the list of ignored words."""
        await self.generic_add_delete(ctx, msg, "ignore", "added")

    @filter.group(name = "delete")
    async def delete(self, ctx: commands.Context):
        """Base command. Can either remove a regex, name or ignored word."""
        pass

    @delete.command(name = "regex")
    async def delete_regex(self, ctx, *, msg):
        """Removes a regex from the list."""
        await self.generic_add_delete(ctx, msg, "regex", "deleted")

    @delete.command(name = "name")
    async def delete_name(self, ctx, *, msg):
        """Removes a name from the list."""
        await self.generic_add_delete(ctx, msg, "names", "deleted")

    @delete.command(name = "ignore")
    async def delete_ignore(self, ctx, *, msg):
        """Removes an ignored word from the list."""
        await self.generic_add_delete(ctx, msg, "ignore", "deleted")

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