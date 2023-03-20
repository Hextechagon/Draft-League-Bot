"""Main file that listens and responds to commands.

Commands include:
!register_coach <@user>  
!remove_coach <@user>  
!replace_coach <@old_coach> <@new_coach>  
!draft  
!select <pokemon_name>
!add <pokemon_list>
!remove <pokemon_list>
Note: pokemon_list consists of pokemon names separated by one space
put additional notes after each command
"""
import os
import discord
from dotenv import load_dotenv
from discord.ext import commands
from coach_helpers import *
from draft_helpers import *


load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')

#Create the bot connection
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix='!', intents=intents)
draft_order = []

@bot.event
async def on_ready():
    """Display a connection message."""
    print(f'{bot.user.name} has connected to Discord!')

@bot.command()
async def test(ctx, user: discord.Member):
    """Testing (use this as a sample)."""
    response = user.id
    await ctx.send(f'Hello <@{response}>!')
    await ctx.send(user.name)
    message = db_test(response)
    await ctx.send(message)

@bot.command()
async def register_coach(ctx, user: discord.Member):
    """Enter the specified server member into the draft league."""
    # TODO: see comment above

@bot.command()
async def remove_coach(ctx, user: discord.Member):
    """Remove the specified server member from the draft league."""
    # TODO: see comment above

@bot.command()
async def replace_coach(ctx, user1: discord.Member, user2: discord.Member):
    """Replace a current coach with the specified server member."""
    # TODO: see comment above

@bot.command()
async def draft(ctx):
    """Populates the draft_order list with the coaches in random order."""
    # TODO: see comment above

@bot.command()
async def select(ctx, pokemon):
    """Add the specified pokemon to the coach's party."""
    # TODO: see comment above

@bot.command()
async def add(ctx, *pokemon):
    """Add the specified pokemon(s) to the coach's party."""
    # TODO: see comment above (ONLY available after drafting finished)
    # recommend do remove before add to make sure budget not exceeded

@bot.command()
async def remove(ctx, *pokemon):
    """Remove the specified pokemon(s) from the coach's party."""
    # TODO: see comment above (ONLY available after drafting finished)


bot.run(TOKEN)
