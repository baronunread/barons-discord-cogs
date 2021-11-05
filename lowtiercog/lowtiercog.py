from redbot.core import commands
import gspread
import discord
import random

class Lowtiercog(commands.Cog):
    """Receives infamous LTG quotes and stores them into JSON."""
    def __init__(self, bot):
        self.bot = bot
        self.quotes = None
        self.numQuotes = None
        self.bot.loop.create_task(self.validate_cache())
    
    @commands.command()
    @commands.has_permissions(manage_messages = True)
    async def setup(self, ctx):
        try:
            await ctx.message.attachments[0].save("ltgkeys.json")
            await self.parse()
            await ctx.send("We have successfully setup everything.")
            await ctx.message.delete()
        except:
            await ctx.send("An error has occured.")

    async def validate_cache(self):
        try:
            await self.parse()
        except:
            pass

    async def parse(self):
        gc = gspread.service_account(filename = "ltgkeys.json")   
        self.quotes = gc.open('ltg').sheet1
        self.numQuotes = int(self.quotes.acell('A1').value)
 
    @commands.group(invoke_without_command = True)
    async def lowtierquote(self, ctx):
        """Base command. Without arguments it posts a random LTG quote."""
        selected = random.randint(1, self.numQuotes)
        quote = self.quotes.cell(selected + 1, 1).value
        await ctx.send(quote) 

    @lowtierquote.command(name = "show")
    async def _lowtiershow(self, ctx, code):
        """Showcases a specific quote given an ID. The row number in the Google Sheet is the code.
           To see the the Google Sheets use the list command."""
        quote = self.quotes.cell(code + 1, 1).value
        if not quote: quote = "There's no quote associated to that ID."
        await ctx.send(quote)

    @lowtierquote.command(name = "list")
    async def _lowtierlist(self, ctx):
        """Sends the Google Sheet link."""
        await ctx.send("https://docs.google.com/spreadsheets/d/1wOBldLlBONvFxVI0jRALLuUpaQ8uev_JOUvzyL6PTd8")

    @lowtierquote.command(name = "add")
    @commands.has_permissions(manage_messages = True)
    async def _lowtieradd(self, ctx, *, msg):
        """Adds a quote to the list of quotes."""
        self.quotes.update_cell(self.numQuotes + 2, 1, msg)
        self.numQuotes += 1
        await ctx.send("Quote successfully added! Its ID is: {}".format(self.numQuotes))
        
    @lowtierquote.command(name = "delete")
    @commands.has_permissions(manage_messages = True)
    async def _lowtierdel(self, ctx, *, code):
        """Removes a quote from the list of quotes, given the ID"""
        self.quotes.delete_rows(int(code) + 1)
        self.numQuotes -= 1
        await ctx.send("Quote successfully deleted!")
        
    @lowtierquote.error
    @_lowtierlist.error
    @_lowtiershow.error
    @_lowtieradd.error
    @_lowtierdel.error
    async def check_error(self, ctx, error):
        if not self.quotes:
            await ctx.send("I haven't been setup yet.")
        elif isinstance(error, discord.HTTPException):
            await ctx.send("Open up your DMs.")
        else:
            await ctx.send("An unexpected error has happened.")