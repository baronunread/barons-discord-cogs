from redbot.core import commands, checks
from discord.utils import get

class Voicerole(commands.Cog):
    """Checks if people have joined the voice chat and gives them the voice chat role."""

    @commands.Cog.listener()
    async def on_voice_state_update(self, member, before, after):
        voice = 770658787740090398
        role = get(member.guild.roles, id = voice)
        if member.bot:
            return
        if not before.channel:
            await member.add_roles(role)
        if before.channel and not after.channel:
            await member.remove_roles(role)
