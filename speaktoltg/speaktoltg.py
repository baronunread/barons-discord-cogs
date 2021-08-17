from redbot.core import commands, Config
from textgenrnn import textgenrnn

class SpeakToLtg(commands.Cog):
    """Replicates LTG's pastas through ai text generation."""
    # def __init__(self):
    #     self.config = Config.get_conf(self, identifier = 3434348210111210810599971161011)
    #     self.config.register_global(model = None)
    #     self.cached_next = None

    @commands.group(name = "AI")
    @commands.has_permissions(manage_messages = True)
    async def ai(self, ctx):
        """Base command. Check the subcommands."""
        pass

    @ai.command(name = "setup")
    async def run(self, ctx):
       ai = textgenrnn()
       ai.train_from_file("ltg.txt", num_epochs = 1)
       await ctx.send(ai.generate()) 