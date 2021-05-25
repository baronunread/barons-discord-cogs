from .lowtiercog import Lowtiercog
import json
import os.path
from os import path

if (not path.exists("quotes.json") ):
    data = {
            "quotes": [],
            "deleted": []
    }
    with open('quotes.json', 'w') as file:
        json.dump(data, file)

def setup(bot):
    bot.add_cog(Lowtiercog())
