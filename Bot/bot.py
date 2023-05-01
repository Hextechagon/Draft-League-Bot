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
import discord
from dotenv import load_dotenv
from discord.ext import commands
from cogs.coach import Coach
from cogs.draft import Draft


load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')

#Create the bot connection
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix='!', intents=intents)

@bot.event
async def on_ready():
    """Display a connection message."""
    print(f'{bot.user.name} has connected to Discord!')
    await bot.add_cog(Coach(bot))
    await bot.add_cog(Draft(bot))

@bot.command()
async def guide(ctx):
    """Display a list of all commands."""
    await ctx.send('Help message here!')


bot.run(TOKEN)
