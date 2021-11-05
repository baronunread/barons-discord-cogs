from redbot.core import commands
import gspread
import discord
import json
import random

class Lowtiercog(commands.Cog):
    """Receives infamous LTG quotes and stores them into JSON."""
    def __init__(self, bot):
        self.bot = bot
        self.quotes = None
        self.bot.loop.create_task(self.validate_cache())
    
    @commands.command()
    @commands.has_permissions(manage_messages = True)
    async def setup(self, ctx):
        try:
            await ctx.message.attachments[0].save("ltgkeys.json")
            gc = gspread.service_account(filename = "ltgkeys.json")   
            self.quotes = gc.open('ltg').sheet1
            await ctx.send("We have successfully setup everything.")
        except:
            await ctx.send("An error has occured.")

    async def validate_cache(self):
        try:
            gc = gspread.service_account(filename = "ltgkeys.json")   
            self.quotes = gc.open('ltg').sheet1
        except:
            pass

    def setup_check(f):
        async def wrapper(*args):
            if not args[0].quotes:
                await args[1].send("I haven't been setup yet.")
            else:
                return f(*args)
    
    @setup_check
    @commands.group(invoke_without_command = True)
    async def lowtierquote(self, ctx):
        """Base command. Without arguments it posts a random LTG quote."""
        numberOfQuotes = int(self.quotes.acell('F1').value)
        selected = random.randint(1, numberOfQuotes)
        quote = self.quotes.cell(selected, 1).value
        await ctx.send(quote)

    @lowtierquote.command(name = "show")
    async def _lowtiershow(self, ctx, code):
        """Showcases a specific quote given an ID."""
        if ( ctx.channel.id == 319638586364395520 or ctx.channel.id == 344539989906030612 ):
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
    async def _lowtierlist(self, ctx):
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
    async def _lowtieradd(self, ctx, *, msg):
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
    async def _lowtierdelete(self, ctx, code):
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
