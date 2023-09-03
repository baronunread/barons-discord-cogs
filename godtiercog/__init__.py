from .godtiercog import Godtiercog
import json
import os.path
from os import path

if (not path.exists("posts.json") ):
    data = {
            "quotes": [],
            "deleted": []
    }
    with open('posts.json', 'w') as file:
        json.dump(data, file)

async def setup(bot):
    await bot.add_cog(Godtiercog())
