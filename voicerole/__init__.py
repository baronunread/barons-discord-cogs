from .voicerole import Voicerole

async def setup(bot):
    await bot.add_cog(Voicerole(bot))
