from redbot.core import commands
import json
import random

class Lowtiercog(commands.Cog):
    """Receives infamous LTG quotes and stores them into JSON."""

    @commands.group(invoke_without_command = True)
    async def lowtierquote(self, ctx: commands.Context):
        """Base command. Without arguments it speaks a random LTG quote."""
        try:
            with open('quotes.json') as file:
                data = json.load(file)
            random.seed(random.random())
            selected = random.choice(data['quotes'])
            msg = selected['msg']
            await ctx.send(msg)
        except IndexError as e:
            await ctx.send("There are no LTG quotes.")

    @lowtierquote.command(name = "show")
    async def _lowtiershow(self, ctx: commands.Context, code):
        """Showcases a specific quote given an ID."""
        try:
            id = int(code)
            msg = "The given ID wasn't found."
            with open('quotes.json') as file:
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

    @lowtierquote.command(name = "list")
    async def _lowtierlist(self, ctx: commands.Context):
        """Showcases the current list of quotes. The preview is 50 characters long."""
        output = ""
        messages = []
        user = ctx.message.author
        with open('quotes.json') as file:
            data = json.load(file)
        if ( len(data['quotes']) == 0 ):
            output = "There are no LTG quotes."
        for quote in data['quotes']:
            id = quote['id']
            msg = quote['msg'][0:50].rstrip().replace('\n', ' ')
            if ( len(output) >= 1900 ):
                messages.append(output)
                output = ""
            output = output + "ID: " + str(id) + " - " + msg
            if ( len(quote['msg']) > 50 ):
                output += "..."
            output += "\n"
        if ( output != "" ):
            messages.append(output)
        try:
            for output in messages:
                await user.send(output)
        except:
            await ctx.send("ERROR: Please open your DMs.")

    @lowtierquote.command(name = "add")
    @commands.has_permissions(manage_messages = True)
    async def _lowtieradd(self, ctx: commands.Context, *, msg):
        """Adds a quote to the JSON file."""
        id = 0
        with open('quotes.json') as file:
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
        with open('quotes.json', 'w') as file:
            json.dump(data, file, indent = 2)
        await ctx.send("It is done. The ID is %d." %id)

    @lowtierquote.command(name = "delete")
    @commands.has_permissions(manage_messages = True)
    async def _lowtierdelete(self, ctx: commands.Context, code):
        """Removes a quote from the JSON file, given an id."""
        id = int(code)
        msg = "The given ID wasn't found."
        with open('quotes.json') as file:
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
                with open('quotes.json', 'w') as file:
                    json.dump(data, file, indent = 2)
                msg = "It is done."
                break
        await ctx.send(msg)
