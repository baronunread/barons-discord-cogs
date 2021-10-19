from .regfilter import Regfilter

def setup(bot):
    bot.add_cog(Regfilter(bot))