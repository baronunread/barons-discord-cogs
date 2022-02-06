from redbot.core import commands, Config
import unicodedata
import discord
import random
import re

class Regfilter(commands.Cog):
    """Uses a REGEX expression to filter bad words.
    Includes by default some very used slurs."""
    def __init__(self, bot):
        self.bot = bot
        self.config = Config.get_conf(self, identifier = 38927046139453664535446215365606156952951)
        default_global = {
                            "regex": [  
                                        r"\bj+\s*[aæ]+[\saæ]*p+[\sp]*s?\b",
                                        r"\bf+\s*[aæ]+[\saæ]*g|\b\w*f+[aæ]+g",
                                        r"\bs+\s*p+[\sp]*i+[\si]*c+[\sc]*s?\b",
                                        r"\bg+\s*[oœ]+\s*[oœ]+[\soœ]*k|\b\w*g+[oœ]{2,}k",
                                        r"\bk+\s*i+[\si]*k+[\sk]*[eæœ]|\b\w*k+i+k+[eæœ]",
                                        r"\bn+\s*[eæœ]+[\seæœ]*g+[\sg]*r+[\sr]*[oœ]|\b\w*n+[eæœ]+g+r+[oœ]",
                                        r"\bc+\s*h+[\sh]*i+[\si]*n+[\sn]*k|\b\w*c+h+i+n+k",
                                        r"\bn+\s*[il]+[\sil]*g+\s*g+[\sg]*[eæœ]+[\seæœ]*r|\b\w*n+[il]+g{2,}[eæœ]+r",
                                        r"\bt+\s*r+[\sr]*[aæ]+[\saæ]*n+\s*n+[\sn]*[iy]|\b\w*t+r+[aæ]+n{2,}[iy]"
                                        ],
                            "names": [],
                            "ignore":[ r"\bhttp[^' ']*" ],
                            "letters":["a","c","e","f","g","h","i","j","k","n","o","p","r","s","t","y"],
                            "a": ["ⱥ","@","4","α","λ","ƛ","δ","σ","а","ҩ"],                                             
                            "c": ["ȼ","с","¢","ƈ","ϲ","ͼ","ҫ"], 
                            "e": ["ɇ","£","€","ҽ","ҿ","ə","з","ӡ","ʒ","3","ҙ","е","э","ε","є","ξ"],
                            "f": ["ꞙ","ƒ","₣","ꬵ","ӻ","ғ"],      
                            "g": ["ǥ","ɠ","غ","ع"],                                          
                            "h": ["ħ"],
                            "i": ["1","!","|","ӏ","ι","ł","ƚ","ɨ","і"], 
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
        self.config.register_global(**default_global)
        self.cache_regex = []
        self.cache_names = []
        self.cache_ignore = []
        self.leet_dict = {}
        self.bot.loop.create_task(self.validate_cache())

    async def build_dict(self):
        for key in await self.config.letters():
            keyDict = dict.fromkeys(await self.config.get_raw(key), key)
            self.leet_dict.update(keyDict)

    async def update_dict(self, badLetter, letter, add: bool):
        if add:
            self.leet_dict[badLetter] = letter
        else:
            self.leet_dict.pop(badLetter)
    
    async def replace(self, msg):
        noMarkdown = msg.lower().replace("||","")                                           # makes text lowercase and removes critical markdown pairs, leaves singular |
        nfkd_form = unicodedata.normalize('NFKD', noMarkdown)                               # NFKD form
        noDiacritics = u"".join([c for c in nfkd_form if not unicodedata.combining(c)])     # removes most of the diacritics TODO #1 better diacritic remover
        noLookAlikes = await self.clean(noDiacritics)                                       # removes the remaining characters that aren't necessarily of the type ALPHABETIC WITH
        alphanum = ''.join(c for c in noLookAlikes if c.isalnum() or c == ' ')              # remove anything that isn't an alphabetic character or a space
        for ignore in self.cache_ignore:
            alphanum = ignore.sub('', alphanum)                                             # remove ignored words as they are not important
        return alphanum

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
        else:
            return await self.config.get_raw(type)

    async def compile_cache(self, type, value = None):
        toCompile = value if value else await self.config.get_raw(type)
        compiled = []
        for pattern in toCompile:
            compiled.append( re.compile(pattern) )
        return compiled

    async def update_cache(self, type, content = None):
        value = content if content else await self.config.get_raw(type)
        if type == "regex":
            self.cache_regex = await self.compile_cache("regex", value = value)
        elif type == "names":
            self.cache_names = value
        elif type == "ignore":
            self.cache_ignore = await self.compile_cache("ignore", value = value)
                     
    async def validate_cache(self):
        if  not self.cache_regex: 
            await self.compile_cache("regex")
        if not self.cache_ignore:
            await self.update_cache("names")    
        if not self.cache_ignore:
            await self.compile_cache("ignore")
        if not self.leet_dict:
            await self.build_dict()
            
    @commands.group()
    @commands.has_permissions(manage_messages = True)
    async def filter(self, ctx: commands.Context):
        """Base command. Check the subcommands."""
        pass

    @filter.group(name = "add")
    async def add(self, ctx):
        """Base command. Can add a regex, a name for replacing or a word to ignore."""
        pass

    async def generic_add_delete(self, ctx, item, type: str, add: bool):
        list = await self.config.get_raw(type)
        found = not item in list if add else item in list
        letterType = type in await self.config.get_raw("letters")
        if found:
            list.append(item) if add else list.remove(item)
            await self.config.set_raw(type, value = list)
            await self.update_dict(item, type, add) if letterType else await self.update_cache(type, content = list)
            message = "Operation completed successfully."
        else:
            message = "That item is already there." if add else "Couldn't find that item."
        await ctx.send(message)

    @add.command(name = "letter")
    async def add_letter(self, ctx, keyLetter, badLetter):
        """Adds a foreign letter to the list of normal letters."""
        await self.generic_add_delete(ctx, badLetter, keyLetter, True)

    @add.command(name = "regex")
    async def add_regex(self, ctx, *, msg):
        """Adds a regex to the list."""
        await self.generic_add_delete(ctx, msg, "regex", True)
        
    @add.command(name = "name")
    async def add_name(self, ctx, *, msg):
        """Adds a name to the list of default names. Applied when filtering a name."""
        await self.generic_add_delete(ctx, msg, "names", True)

    @add.command(name = "ignore")
    async def add_ignore(self, ctx, *, msg):
        """Adds a word to ignore to the list of ignored words."""
        await self.generic_add_delete(ctx, msg, "ignore", True)

    @filter.group(name = "delete")
    async def delete(self, ctx):
        """Base command. Can either remove a regex, name or ignored word."""
        pass

    @delete.command(name = "letter")
    async def delete_letter(self, ctx, keyLetter, badLetter):
        await self.generic_add_delete(ctx, badLetter, keyLetter, False)

    @delete.command(name = "regex")
    async def delete_regex(self, ctx, *, msg):
        """Removes a regex from the list."""
        await self.generic_add_delete(ctx, msg, "regex", False)

    @delete.command(name = "name")
    async def delete_name(self, ctx, *, msg):
        """Removes a name from the list."""
        await self.generic_add_delete(ctx, msg, "names", False)

    @delete.command(name = "ignore")
    async def delete_ignore(self, ctx, *, msg):
        """Removes an ignored word from the list."""
        await self.generic_add_delete(ctx, msg, "ignore", False)

    @filter.group(name = "list")
    async def listThings(self, ctx):
        """Base command. Can either send the list of regex, names or ignored words."""
        pass

    async def letters_list(self):
        letters = await self.config.letters()
        prettyList = ""
        for letter in letters:
            list = await self.config.get_raw(letter)
            prettyList = prettyList + letter + " : " + str(list) + "\n"
        return prettyList

    async def generic_list(self, ctx, user, type: str):
        try:
            if type == "letters":
                prettyList = await self.letters_list()    
            else:    
                list = await self.config.get_raw(type)
                prettyList = "\n".join(list)
            if not prettyList:
                await user.send("There's nothing in that list.")
                return
            if type == "regex" or "letters":
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

    @listThings.command(name = "letters")
    async def list_letters(self, ctx):
        """Sends the letter list through DMs."""
        await self.generic_list(ctx, ctx.message.author, "letters")
    
    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        await self.validate_cache()
        author = message.author
        if author.bot:
            return
        content = await self.replace(message.clean_content)
        regexs = await self.return_cache("regex")
        if await self.triggered_filter(content, regexs):
            await message.delete()

    async def triggered_filter(self, content, regexs):
        for regex in regexs:
            if regex.search(content):
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