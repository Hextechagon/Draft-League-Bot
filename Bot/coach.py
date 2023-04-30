"""Commands for coaches."""
import discord
from discord.ext import commands


class coach(commands.Cog):
    def __init__(self, bot):
        """Initialize the cog."""
        self.bot = bot
    
