"""Main file that listens and responds to commands.

Commands include:
UPDATE THIS!!!
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
import asyncio
import pathlib
import discord
from dotenv import load_dotenv
from discord.ext import commands
from coach import Coach
from draft import Draft


load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')

# create the bot connection
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix='!', intents=intents)


async def upload_log():
    """Send the database file to a log channel every hour."""
    channel = bot.get_channel(1103773916327051394)
    root = pathlib.Path(__file__).resolve().parent.parent
    database_file = root/'var'/'CTLDL_Bot.sqlite3'
    while True:
        await channel.send(file=discord.File(database_file))
        await asyncio.sleep(3600)


@bot.event
async def on_ready():
    """Display a connection message."""
    print(f'{bot.user.name} has connected to Discord!')
    await bot.add_cog(Coach(bot))
    await bot.add_cog(Draft(bot))
    await upload_log()


@bot.event
async def on_command_error(ctx, error):
    """Handle invalid commands."""
    if isinstance(error, commands.CommandNotFound):
        await ctx.send('You either entered an invalid command or did not include \
                        all the required argument(s): use !guide for more details.')


@bot.command()
async def guide(ctx):
    """Display a list of all commands."""
    await ctx.send('Help message here!')


bot.run(TOKEN)
