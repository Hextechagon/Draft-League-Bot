"""Commands for drafting."""
import discord
from discord.ext import commands
from draft_helpers import *


class Draft(commands.Cog):
    """Draft class."""

    def __init__(self, bot):
        """Initialize the draft cog."""
        self.bot = bot
        self.draft_order = []

    @commands.command()
    async def start(self, ctx):
        """Initiate the draft process by randomizing the draft order and beginning the timer."""
        # TODO

    @commands.command()
    async def select(self, ctx, pokemon):
        """Add the specified pokemon to the coach's party."""
        # TODO

    @commands.command()
    async def add(self, ctx, *pokemon):
        """Add the specified pokemon(s) to the coach's party."""
        # TODO: see comment above (ONLY available after drafting finished)
        # recommend do remove before add to make sure budget not exceeded

    @commands.command()
    async def remove(self, ctx, *pokemon):
        """Remove the specified pokemon(s) from the coach's party."""
        # TODO: see comment above (ONLY available after drafting finished)
