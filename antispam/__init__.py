from .antispam import Antispam

async def setup(bot):
    await bot.add_cog(Antispam(bot))