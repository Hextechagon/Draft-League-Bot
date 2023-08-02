"""Commands for matches.
!record <@winner> <@loser> margin replay TODO: double ff loss (non essential)
!rrecord matchid TODO double ff loss (non essential)
!mhistory week
!chistory <@coach>
"""
import discord
from discord.ext import commands
from match_helpers import insert_match, remove_match, get_history, coach_history
from db_conn import check_channel


class Match(commands.Cog):
    """Coaches class."""

    def __init__(self, bot):
        """Initialize the coach cog."""
        self.bot = bot

    @commands.command()
    @commands.has_role('Draft Host')
    @check_channel('replays')
    async def record(self, ctx, week: int, winner: discord.Member, loser: discord.Member, margin, replay=None):
        """Record the outcome of a match (enter -1 for margin if forfeit win/loss)."""
        if winner == loser:
            await ctx.send(':x: Please specify two different coaches.')
            return
        status = insert_match(winner.id, loser.id, week, margin, replay)
        if status == 0:
            await ctx.send(':white_check_mark: The match has been recorded.')
        elif status == 1:
            await ctx.send(':x: The match between the two coaches has already been'
                           ' recorded for the specified week.')
        else:
            await ctx.send(':x: Please specify valid coaches.')

    @commands.command()
    @commands.has_role('Draft Host')
    @check_channel('replays')
    async def rrecord(self, ctx, matchid: int):
        """Remove an existing match entry."""
        status = remove_match(matchid)
        if status == 0:
            await ctx.send(':white_check_mark: The specified match has been removed.')
        else:
            await ctx.send(':x: Please specify a valid match ID.')

    @commands.command()
    @check_channel('coaches')
    async def mhistory(self, ctx, week: int):
        """Display the match history for a particular week."""
        matches = get_history(week)
        output = ''
        if len(matches) == 0:
            output += 'There are no matches recorded for the specified week.'
            await ctx.send(':x: ' + output)
        else:
            for match in matches:
                matchid = match[0]
                winner = await self.bot.fetch_user(match[1]).display_name
                loser = await self.bot.fetch_user(match[2]).display_name
                record = match[3]
                replay = match[4]
                if record == -1:
                    record = 'Forfeit Win'
                if replay is None:
                    replay = 'No Replay'
                output += str(matchid) + '. ' + winner + ' won against ' + \
                    loser + f' ({record} - 0): ' + replay
            await ctx.send(f'[Week {week}]\n' + output)

    @commands.command()
    @check_channel('coaches')
    async def chistory(self, ctx, user: discord.Member):
        """Display the match history for a particular coach."""
        matches = coach_history(user.id)
        output = ''
        if len(matches) == 0:
            output += 'There are no matches recorded for the specified coach.'
            await ctx.send(':x: ' + output)
        else:
            result = None
            for match in matches:
                matchid = match[0]
                winner = await self.bot.fetch_user(match[1]).display_name
                loser = await self.bot.fetch_user(match[2]).display_name
                record = match[3]
                replay = match[4]
                week = match[5]
                if replay is None:
                    replay = 'No Replay'
                if match[1] == user.id:
                    result = ':regional_indicator_w:'
                    if record == -1:
                        record = 'Forfeit Win'
                    output += str(week) + f' ({matchid}). {result} ' + winner + ' won against ' + \
                        loser + f' ({record} - 0): ' + replay
                else:
                    result = ':regional_indicator_l:'
                    if record == -1:
                        record = 'Forfeit Loss'
                    output += str(week) + f' ({matchid}). {result} ' + loser + ' lost against ' + \
                        winner + f' (0 - {record}): ' + replay
            await ctx.send(f'[{user.display_name} Match History]\n' + output)

    @record.error
    @rrecord.error
    @mhistory.error
    @chistory.error
    async def error_handler(self, ctx, error):
        """Respond to discord.py errors."""
        if isinstance(error, commands.MissingRole):
            await ctx.send(':x: You do not have permission to use this command.')
        elif isinstance(error, commands.errors.MemberNotFound):
            await ctx.send(':x: Please specify valid server member(s).')
        elif isinstance(error, TypeError):
            await ctx.send('Please enter an integer argument where applicable.')
