import os
import discord
from dotenv import load_dotenv
from discord.ext import commands
#replace * with function names
from helpers import db_test


load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix='!', intents=intents)

@bot.event
async def on_ready():
    print(f'{bot.user.name} has connected to Discord!')

@bot.command(name='test')
async def testing(ctx, user: discord.Member = None):
    response = 'Hello  ' + str(arg)
    await ctx.send(response)
    db_test()

bot.run(TOKEN)
