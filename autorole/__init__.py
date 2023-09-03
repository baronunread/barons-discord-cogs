from .autorole import Autorole

async def setup(bot):
    await bot.add_cog(Autorole(bot))