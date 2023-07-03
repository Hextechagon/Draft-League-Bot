"""Commands for matches.
!record showdown_link showdown_username1 <@user1> <@user2> TODO
!forfeit <@user1> <@user2> TODO
!mhistory week TODO show match id (show ff loss too)
!match match_id TODO
!kleader TODO pokemon kill leader ranking with owner next to pokemon name
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
    async def record(self, ctx, link, user1_sd, user1: discord.Member, user2: discord.Member):
        """Analyze a match replay and save the resulting data."""
        # TODO

    @commands.command()
    @commands.has_role('Draft Host')
    @check_channel('coaches')
    async def forfeit(self, ctx, user1: discord.Member, user2: discord.Member):
        """Record a forfeit loss for user1 to user2."""
        # TODO

    @commands.command()
    @commands.has_role('Draft League')
    @check_channel('coaches')
    async def mhistory(self, ctx, week):
        """Display the match history for a particular week."""
        # TODO

    @commands.command()
    @commands.has_role('Draft League')
    @check_channel('coaches')
    async def match(self, ctx, matchid):
        """Display detailed statistics for a specific match."""
        # TODO

    @commands.command()
    @commands.has_role('Draft League')
    @check_channel('coaches')
    async def kleader(self, ctx):
        """Display the top 10 Pokémon with the most kills in the current season."""
        # TODO
