from redbot.core import commands
import discord

class Autorole(commands.Cog):
    """Automatically hands out a single role you can setup beforehand."""

    @commands.group()
    @commands.has_permissions(manage_messages = True)
    async def autorole(self, ctx):
        """Adds the role to be given when you level up"""
        pass