from .replypin import Replypin

async def setup(bot):
    await bot.add_cog(Replypin())