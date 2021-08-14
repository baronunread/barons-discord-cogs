from .antispam import Antispam

def setup(bot):
    bot.add_cog(Antispam())