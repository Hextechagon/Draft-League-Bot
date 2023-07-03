"""Commands for matches."""
import discord
from discord.ext import commands
from match_helpers import *
from db_conn import check_channel


class Match(commands.Cog):
    """Coaches class."""

    def __init__(self, bot):
        """Initialize the coach cog."""
        self.bot = bot
