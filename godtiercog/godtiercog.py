from redbot.core import commands
import json
import random

class Godtiercog(commands.Cog):
    """Receives an IMGUR link of a great post and stores it into JSON."""

    @commands.command()
    async def download_test(self, ctx):
        try:
            await ctx.attachments[0].save("ltgkeys.json")
            with open('ltgkeys.json', 'r') as handle:
                await ctx.send(json.load(handle))
        except:
            await ctx.send("Bro you fucked up doe")
    
    @commands.group(invoke_without_command = True)
    async def godpost(self, ctx: commands.Context):
        """Base command. Without arguments it spits out a random post."""
        if ( ctx.channel.id == 319638586364395520 or ctx.channel.id == 344539989906030612 ):
            try:
                with open('posts.json') as file:
                    data = json.load(file)
                random.seed(random.random())
                selected = random.choice(data['quotes'])
                msg = selected['msg']
                await ctx.send(msg)
            except IndexError as e:
                await ctx.send("There are no posts!")

    @godpost.command(name = "show")
    async def _showpost(self, ctx: commands.Context, code):
        """Showcases a specific post given an ID."""
        if ( ctx.channel.id == 319638586364395520 or ctx.channel.id == 344539989906030612 ):
            try:
                id = int(code)
                msg = "The given ID wasn't found."
                with open('posts.json') as file:
                    data = json.load(file)
                quotes = data['quotes']
                for x in range(len(quotes)):
                    key = quotes[x]['id']
                    if ( id == key ):
                        msg = quotes[x]['msg']
                        break
                await ctx.send(msg)
            except:
                await ctx.send("Invalid code.")

    @godpost.command(name = "list")
    async def _listposts(self, ctx: commands.Context):
        """Showcases the current list of posts."""
        output = ""
        count = 0
        messages = []
        user = ctx.message.author
        with open('posts.json') as file:
            data = json.load(file)
        if ( len(data['quotes']) == 0 ):
            output = "There are no posts!"
        for quote in data['quotes']:
            id = quote['id']
            msg = quote['msg']
            output += "ID: " + str(id) + " - " + msg + "\n"
            count += 1
            if ( count == 5 ):
                messages.append(output)
                output = ""
                count = 0
        if ( output != "" ):
            messages.append(output)
        try:
            for output in messages:
                await user.send(output)
        except:
            await ctx.send("ERROR: Please open your DMs.")

    @godpost.command(name = "add")
    @commands.has_permissions(manage_messages = True)
    async def _addpost(self, ctx: commands.Context, *, msg):
        """Adds a post to the JSON file."""
        id = 0
        with open('posts.json') as file:
            data = json.load(file)
        try:
            deleted = data['deleted']
            id = deleted[0]['id']
            del deleted[0]
        except:
            for quote in data['quotes']:
                testedId = int(quote['id'])
                if (id < testedId):
                    id = testedId
            id = id + 1
        add = {
                "id": id,
                "msg": msg
              }
        data['quotes'].append(add)
        with open('posts.json', 'w') as file:
            json.dump(data, file, indent = 2)
        await ctx.send("It is done. The ID is %d." %id)

    @godpost.command(name = "delete")
    @commands.has_permissions(manage_messages = True)
    async def _deletepost(self, ctx: commands.Context, code):
        """Removes a post from the JSON file, given an ID."""
        id = int(code)
        msg = "The given ID wasn't found."
        with open('posts.json') as file:
            data = json.load(file)
        quotes = data['quotes']
        for x in range(len(quotes)):
            key = quotes[x]['id']
            if ( id == key ):
                del quotes[x]
                add = {
                        "id": id
                      }
                data['deleted'].append(add)
                with open('posts.json', 'w') as file:
                    json.dump(data, file, indent = 2)
                msg = "It is done."
                break
        await ctx.send(msg)
