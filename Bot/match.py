"""Commands for matches.
!record <@winner> <@loser> margin replay TODO
!rrecord matchid TODO
!mhistory week TODO show match id (show ff loss too)
"""
import discord
from discord.ext import commands
from match_helpers import *
from db_conn import check_channel


class Match(commands.Cog):
    """Coaches class."""

    def __init__(self, bot):
        """Initialize the coach cog."""
        self.bot = bot

    @commands.command()
    @commands.has_role('Draft Host')
    @check_channel('replays')
    async def record(self, ctx, winner: discord.Member, loser: discord.Member, margin, replay = None):
        """Record the outcome of a match."""
        # TODO: for ff loss use a special margin like -1

    @commands.command()
    @commands.has_role('Draft Host')
    @check_channel('replays')
    async def rrecord(self, ctx, matchid):
        """Remove an existing match entry."""
        # TODO

    @commands.command()
    @commands.has_role('Draft League')
    @check_channel('coaches')
    async def mhistory(self, ctx, week):
        """Display the match history for a particular week."""
        # TODO

    @record.error
    async def error_handler(self, ctx, error):
        """Respond to discord.py errors."""
        if isinstance(error, commands.MissingRole):
            await ctx.send(':x: You do not have permission to use this command.')
        elif isinstance(error, commands.errors.MemberNotFound):
            await ctx.send(':x: Please specify valid server member(s).')
