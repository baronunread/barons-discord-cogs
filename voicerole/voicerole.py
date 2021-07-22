import voicerole
from redbot.core import commands, Config
from discord.utils import get

class Voicerole(commands.Cog):
    """Checks if people have joined the voice chat and gives them the voice chat role."""
    def __init__(self):
        self.config = Config.get_conf(self, identifier = 3434346710410199107115321051023211210)
        default_global = {
                            "pairs":[]
                         }
        self.config.register_global(**default_global)
        self.cache_voicepairs = []

    async def validate_cache(self):
        if self.cache_voicepairs == []: 
            self.cache_voicepairs = await self.config.pairs()
            
    @commands.Cog.listener()
    async def on_voice_state_update(self, member, before, after):
        voiceChannel = after.channel
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
        for pair in pairs:
            if voiceChannel == pair[0]:
                return pair[1]
        return None

    @commands.group()
    @commands.has_permissions(manage_messages = True)
    async def voicerole(self, ctx: commands.Context):
        """Base command. Check the subcommands."""
        pass

    @voicerole.group(name = "add", invoke_without_command = True)
    async def _add(self, ctx, voiceChannelID, voiceRoleID):
        """Adds a voicerole rule. Needs, in order, the voice channel ID and then the voice role ID."""
        (voiceChannelID, voiceRoleID)
        async with self.config.pairs() as pairs:
            pairs.append( (int(voiceChannelID), int(voiceRoleID) ) )
            self.cache_pattern = pairs
        await ctx.send("The new voicerole rule has been added.")

    @voicerole.group(name = "delete", invoke_without_command = True)
    async def _delete(self, ctx, voiceChannelID, voiceRoleID):
        """Removes a voicerole rule. Needs, in order, the voice channel ID and then the voice role ID."""
        try:
            async with self.config.pairs() as pairs:
                pairs.remove( (int(voiceChannelID), int(voiceRoleID) ) )
                self.cache_voicepairs = pairs
            await ctx.send("Voicerole rule removed successfully.")
        except:
            await ctx.send("Couldn't find that voicerole rule in the list.")

    @voicerole.group(name = "list", invoke_without_command = True)
    async def _list(self, ctx):
        try:    
            await self.validate_cache()
            list = self.cache_voicepairs
            if len(list) == 0:
                await ctx.message.author.send("There's nothing in that list.")
                return
            prettyList = ""
            for tuple in list:
                work = ' '.join(map(str, tuple))
                prettyList = work + "\n"
            await ctx.message.author.send(prettyList)
        except:
            await ctx.send("ERROR: Open your DMs.")