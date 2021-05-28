from redbot.core import commands, Config
import discord
import re

class Regfilter(commands.Cog):
    """Uses a REGEX expression to filter bad words."""
    def __init__(self):
        self.config = Config.get_conf(self, identifier = 38927046139453664535446215365606156952951)
        default_global = {
                            "regex": ['(?i)g+[\\s+o0]{2,}k',
                                      '(?i)f+[\\s+@4aáäÄæÆ]+g',
                                      '(?i)j+[\\s+@4aáäÄæÆ]+p',
                                      '(?i)s+[\\s+p]+[\\s+iïl1y]+c',
                                      '(?i)k+[\\s+iïl1y]+[\\s+k]+[e3]',
                                      '(?i)c+[\\s+h]+[\\s+iïl1y]+[\\s+n]+k',
                                      '(?i)n+[\\s+e3]+[\\s+gğq]+[\\s+r]+[o0]',
                                      '(?i)n+[\\s+iïl1y]+[\\s+gğq]{2,}[\\s+e3]+r',
                                      '(?i)t+[\\s+r]+[\\s+@4aáäÄæÆ]+[\\s+n]+[iïl1y]'
                                     ]
                        }
        self.config.register_global(**default_global)
        self.cache = default_global['regex']

    @commands.group()
    @commands.has_permissions(manage_messages = True)
    async def filter(self, ctx: commands.Context):
        """Base command. Check the subcommands."""
        pass

    @filter.command(name = "add")
    async def _add(self, ctx: commands.Context, *, msg):
        """Adds a REGEX to the list."""
        async with self.config.regex() as regex:
            regex.append(msg)
            self.cache = regex
        await ctx.send("The new REGEX has been added.")

    @filter.command(name = "delete")
    async def _delete(self, ctx: commands.Context, *, msg):
        """Removes a REGEX from the list."""
        try:
            async with self.config.regex() as regex:
                regex.remove(msg)
                self.cache = regex
                await self.config.regex.set(regex)
            await ctx.send("REGEX removed successfully.")
        except:
            await ctx.send("Couldn't find that REGEX in the list.")
    
    @filter.command(name = "list")
    async def _list(self, ctx: commands.Context):
        """Sends the REGEX list through DMs."""
        try:
            user = ctx.message.author
            list = await self.config.regex()
            prettyList = "\n".join(str(e) for e in list)
            await user.send(prettyList)
        except:
            await ctx.send("ERROR: Open your DMs.")
    
    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        patterns = self.cache
        author = message.author
        content = message.content
        if author.bot:
            return
        for pattern in patterns:
            result = re.findall(pattern, content)
            if ( result != [] ):
                await message.delete()
                return
            