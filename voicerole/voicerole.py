import voicerole
from redbot.core import commands, Config
from discord.utils import get
import json

class Voicerole(commands.Cog):
    """Checks if people have joined the voice chat and gives them the voice chat role."""
    def __init__(self):
        self.config = Config.get_conf(self, identifier = 3434346710410199107115321051023211210)
        self.config.register_global(voiceroles={})
        self.cache_voicepairs = {}

    async def validate_cache(self):
        if self.cache_voicepairs == {}: 
            self.cache_voicepairs = await self.config.voiceroles()
            
    @commands.Cog.listener()
    async def on_voice_state_update(self, member, before, after):
        voiceChannel = after.channel.id
        voice = await self.get_voice(voiceChannel)
        if member.bot or voice == None:
            return
        role = get(member.guild.roles, id = voice)
        if not before.channel:
            await member.add_roles(role)
        if before.channel and not after.channel:
            await member.remove_roles(role)

    async def get_voice(self, voiceChannel):
        await self.validate_cache()
        pairs = self.cache_voicepairs
        try:
            return pairs[voiceChannel]
        except:
            return None

    @commands.group()
    @commands.has_permissions(manage_messages = True)
    async def voicerole(self, ctx: commands.Context):
        """Base command. Check the subcommands."""
        pass

    @voicerole.group(name = "add", invoke_without_command = True)
    async def _add(self, ctx, voiceChannelID, voiceRoleID):
        """Adds a voicerole rule. Needs, in order, the voice channel ID and then the voice role ID."""
        async with self.config.voiceroles() as pairs:
            pairs[ int(voiceChannelID) ] = int(voiceRoleID)
            self.voicepairs = pairs
        await ctx.send("The new voicerole rule has been added.")

    @voicerole.group(name = "delete", invoke_without_command = True)
    async def _delete(self, ctx, voiceChannelID):
        """Removes a voicerole rule. Needs, in order, the voice channel ID."""
        try:
            async with self.config.voiceroles() as pairs:
                pairs.pop(voiceChannelID)
                self.cache_voicepairs = pairs
            await ctx.send("Voicerole rule removed successfully.")
        except:
            await ctx.send("Couldn't find that voicerole rule in the list.")

    @voicerole.group(name = "list", invoke_without_command = True)
    async def _list(self, ctx):
        try:    
            await self.validate_cache()
            dict = self.cache_voicepairs
            if len(dict) == 0:
                await ctx.message.author.send("There's nothing in that list.")
                return
            prettyList = json.dumps(dict)
            await ctx.message.author.send(prettyList)
        except:
            await ctx.send("ERROR: Open your DMs.")