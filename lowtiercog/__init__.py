from .lowtiercog import Lowtiercog

async def setup(bot):
    await bot.add_cog(Lowtiercog(bot))
