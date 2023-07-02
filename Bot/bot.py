"""Main file that listens and responds to commands.

Commands:
!log
!guide

!register <@user>  
!replace <@old_coach> <@new_coach>
!ename <@user> old_name new_name TODO change the display name of selected coach
!ranking
!info <@user>

!randomize
!order
!begin
!select pokemon_name
!preselect??? TODO
!edit previous_pokemon new_pokemon TODO
!etime <@user> amount TODO
!resume TODO
!finish
!reenter <@user> TODO
!fadd pokemon_name TODO force add pokemon by hoster
!fremove pokemon_name TODO force remove pokemon by hoster
!setpos <@user> TODO set draft position to specified user (interrupt current timer if necessary); skip option?
!eskipped <@user> amount TODO modify the number of times a coach has been skipped for timer calculation purposes
!add <pokemon_list> TODO
!remove <pokemon_list> TODO
!trade <@user> pokemon1 pokemon2 TODO

match commands go here: match history by week, match statistics, enter showdown replay to get data, pokemon statistics, archive?

Notes: 
- pokemon_list consists of pokemon names separated by one space
- replace the space(s) with a ! if a pokemon name consists of multiple words
- if someone the coach entrusted drafted for him/her within the draft duration and the hoster did not fadd it 
before the draft deadline, the hoster has to use !eskipped to correct the time penalty associated with # skips
*** TODO: adjust the channel restrictions and times when deploying!!!
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


@tasks.loop(hours=1)
async def upload_log():
    """Send the database file to a log channel every hour."""
    channel = bot.get_channel(1103773916327051394)
    root = pathlib.Path(__file__).resolve().parent.parent
    database_file = root/'var'/'CTLDL_Bot.sqlite3'
    await channel.send(file=discord.File(database_file))


@bot.command()
@commands.has_role('Draft Host')
@commands.check(lambda ctx: ctx.channel.id == 1114021526291890260)
async def log(ctx):
    """Send the database file to a log channel every hour."""
    channel = bot.get_channel(1103773916327051394)
    root = pathlib.Path(__file__).resolve().parent.parent
    database_file = root/'var'/'CTLDL_Bot.sqlite3'
    await channel.send(file=discord.File(database_file))
    await ctx.send(':white_check_mark: The database has been generated in the log channel.')


@bot.command()
async def guide(ctx):
    """Display a list of all commands."""
    await ctx.send('Help message here!')


bot.run(TOKEN)
