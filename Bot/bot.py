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
import pathlib
import discord
from dotenv import load_dotenv
from discord.ext import tasks, commands
from coach import Coach
from draft import Draft


load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')

# create the bot connection
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix='!', intents=intents)


@tasks.loop(hours=1)
async def upload_log():
    """Send the database file to a log channel every hour."""
    channel = bot.get_channel(1103773916327051394)
    root = pathlib.Path(__file__).resolve().parent.parent
    database_file = root/'var'/'CTLDL_Bot.sqlite3'
    await channel.send(file=discord.File(database_file))


@bot.event
async def on_ready():
    """Display the bot connection status."""
    print(f'{bot.user.name} has connected to Discord!')
    await bot.add_cog(Draft(bot))
    await bot.add_cog(Coach(bot))
    upload_log.start()


@bot.event
async def on_command_error(ctx, error):
    """Handle invalid commands."""
    if isinstance(error, commands.CommandNotFound):
        await ctx.send('You entered an invalid command or left out required arguments (use'
                       ' !guide for help).')


@bot.command()
async def guide(ctx):
    """Display a list of all commands."""
    await ctx.send('Help message here!')


bot.run(TOKEN)
