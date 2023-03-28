"""Main file that listens and responds to commands.

Commands include:
!register <@user>  
!delete <@user>  
!replace <@old_coach> <@new_coach>  
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
from coach_helpers import insert_coach, delete_coach, replace_coach
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
async def register(ctx, user: discord.Member):
    """Enter the specified server member into the draft league."""
    # code to ping user await ctx.send(f'Hello <@{user.id}>!')
    status = insert_coach(user.id, user.name)
    if status == 0:
        await ctx.send(f':ballot_box_with_check: {user.name} has been registered as a coach.')
    elif status == 1:
        await ctx.send(':x: This user is already a coach.')
    else:
        await ctx.send(':x: An error has occured.')

@bot.command()
async def delete(ctx, user: discord.Member):
    """Remove the specified server member from the draft league."""
    status = delete_coach(user.id)
    if status == 0:
        await ctx.send(f':ballot_box_with_check: {user.name} has been removed as a coach.')
    elif status == 1:
        await ctx.send(':x: The user is not a valid coach.')
    else:
        await ctx.send(':x: An error has occured.')

@bot.command()
async def replace(ctx, user1: discord.Member, user2: discord.Member):
    """Replace a current coach with the specified server member."""
    delete_status, insert_status = replace_coach(user1.id, user2.id, user2.name)
    #if statement with operation status

@register.error
@delete.error
@replace.error
async def reg_del_error(ctx, error):
    """Check if the entered user is a server member."""
    if isinstance(error, commands.errors.MemberNotFound):
        await ctx.send(":x: Please specify valid server member(s).")

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
