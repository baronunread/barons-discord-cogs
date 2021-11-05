from redbot.core import commands
import gspread
import discord
import json
import random
import inspect

class Lowtiercog(commands.Cog):
    """Receives infamous LTG quotes and stores them into JSON."""
    def __init__(self, bot):
        self.bot = bot
        self.quotes = None
        self.numQuotes = 0
        self.bot.loop.create_task(self.validate_cache())
    
    @commands.command()
    @commands.has_permissions(manage_messages = True)
    async def setup(self, ctx):
        try:
            await ctx.message.attachments[0].save("ltgkeys.json")
            gc = gspread.service_account(filename = "ltgkeys.json")   
            self.quotes = gc.open('ltg').sheet1
            self.numQuotes = int(self.quotes.acell('F1').value)
            await ctx.send("We have successfully setup everything.")
        except:
            await ctx.send("An error has occured.")

    async def validate_cache(self):
        try:
            gc = gspread.service_account(filename = "ltgkeys.json")   
            self.quotes = gc.open('ltg').sheet1
            self.numQuotes = int(self.quotes.acell('F1').value)
        except:
            pass
 
    @commands.group(invoke_without_command = True)
    async def lowtierquote(self, ctx):
        """Base command. Without arguments it posts a random LTG quote."""
        selected = random.randint(1, self.numQuotes)
        quote = self.quotes.cell(selected, 1).value
        await ctx.send(quote) 

    @lowtierquote.command(name = "show")
    async def _lowtiershow(self, ctx, code):
        """Showcases a specific quote given an ID."""
        quote = self.quotes.cell(code, 1).value
        if not quote: quote = "There's no quote associated to that ID."
        await ctx.send(quote)

    @lowtierquote.command(name = "list")
    async def _lowtierlist(self, ctx):
        """Showcases the current list of quotes. The preview is 50 characters long."""
        output = ""
        messages = []
        user = ctx.message.author
        for i in range(self.numQuotes):
            msg = self.quotes.cell(i, 1)
            if len(msg) > 50: msg = msg[0:50].rstrip().replace('\n', ' ') + "..."
            if len(output) >= 1950:
                messages.append(output)
                output = ""
            output += output + "ID: " + str(i) + " - " + msg + "\n"
        if output: messages.append(output)
        for output in messages:
            await user.send(output)

    @lowtierquote.command(name = "add")
    @commands.has_permissions(manage_messages = True)
    async def _lowtieradd(self, ctx, *, msg):
        """Adds a quote to the list of quotes."""
        self.numQuotes += 1
        self.quotes.update_cell(self.numQuotes, 1, msg)
        await ctx.send("Quote successfully added!")
        
    @lowtierquote.command(name = "delete")
    @commands.has_permissions(manage_messages = True)
    async def _lowtierdelete(self, ctx, *, msg):
        """Removes a quote from the list of quotes, given the quote."""
        self.numQuotes -= 1
        self.quotes.delete_rows(self.quotes.find(msg).row)
        await ctx.send("Quote successfully deleted!")
        
    @lowtierquote.error
    async def check_error(self, ctx, error):
        if not self.quotes:
            await ctx.send("I haven't been setup yet.")
        else:
            await ctx.send("An unexpected error has happened.")
            #HTTPException?