from redbot.core import commands, Config
from discord.utils import get

class Voicerole(commands.Cog):
    """Checks if people have joined the voice chat and gives them the voice chat role."""
    def __init__(self):
        self.config = Config.get_conf(self, identifier = 3434346710410199107115321051023211210)
        default_global = {
                            "voicepairs":[]
                         }
        self.config.register_global(**default_global)
        self.cache_voicepairs = []

    @commands.Cog.listener()
    async def on_voice_state_update(self, member, before, after):
        voiceChannel = after.channel
        voice = self.get_voice()
        role = get(member.guild.roles, id = voice)
        if member.bot:
            return
        if not before.channel:
            await member.add_roles(role)
        if before.channel and not after.channel:
            await member.remove_roles(role)

    async def get_voice():
        pass
    
    @commands.group()
    @commands.has_permissions(manage_messages = True)
    async def voicerole(self, ctx: commands.Context):
        """Base command. Check the subcommands."""
        pass

    @voicerole.group()
    async def add(self, ctx, voiceChannelID, voiceRoleID):
        await ctx.send("This is the voice channel id" + voiceChannelID)
        await ctx.send("This is the voice role id" + voiceRoleID)