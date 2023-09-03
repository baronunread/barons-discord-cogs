from .regfilter import Regfilter

async def setup(bot):
    await bot.add_cog(Regfilter(bot))