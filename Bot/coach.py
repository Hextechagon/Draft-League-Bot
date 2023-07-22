"""Commands for coaches.
!register <@user>  
!replace <@old_coach> <@new_coach>
!ranking
!info <@user>
"""
import discord
from discord.ext import commands
from coach_helpers import insert_coach, replace_coach, get_leaderboard, get_info
from draft_helpers import edit_skipped
from db_conn import check_channel


class Coach(commands.Cog):
    """Coaches class."""

    def __init__(self, bot):
        """Initialize the coach cog."""
        self.bot = bot
        self.draft_cog = self.bot.get_cog('Draft')

    @commands.command()
    @commands.has_role('Draft Host')
    @check_channel('coaches')
    async def register(self, ctx, *users: discord.Member):
        """Enter the specified server member(s) into the draft league."""
        for user in users:
            status = insert_coach(user.id, user.display_name)
            if status == 0:
                await ctx.send(f':white_check_mark: {user.display_name} has'
                               ' been registered as a coach.')
            elif status == 1:
                await ctx.send(':x: The draft league is full.')
                return
            else:
                await ctx.send(f':x: {user.display_name} is already a coach.')

    @commands.command()
    @commands.has_role('Draft Host')
    @check_channel('coaches')
    async def replace(self, ctx, user1: discord.Member, user2: discord.Member):
        """Replace a current coach with the specified server member (inherits previous data)."""
        status = replace_coach(user1.id, user2.id, user2.display_name)
        if status == 0:
            # update the draft_queue with the new coach
            coach_info = self.draft_cog.skipped_coaches.get(user1.id)
            # update the old discordid in draft_queue and skipped_coaches with the new one
            self.draft_cog.draft_queue[coach_info[2]][0] = user2.id
            retained_info = self.draft_cog.skipped_coaches.pop(
                user1.id)
            self.draft_cog.skipped_coaches[user2.id] = retained_info
            # reset the draft time penalty for skipping
            self.draft_cog.skipped_coaches[user2.id][0] = 0
            edit_skipped(user2.id, 0)
            await ctx.send(f':white_check_mark: {user1.display_name} has been replaced'
                           f' by {user2.display_name} as a coach.')
        elif status == 1:
            await ctx.send(f':x: {user1.display_name} is not a valid coach.')
        else:
            await ctx.send(f':x: {user2.display_name} is already a coach.')

    @commands.command()
    @check_channel('coaches')
    async def ranking(self, ctx):
        """Display the leaderboard containing all current coaches."""
        leaderboard = get_leaderboard()
        output = ''
        if len(leaderboard) == 0:
            output += 'There are no registered coaches.'
            await ctx.send(':x: ' + output)
        else:
            for rank, coach in enumerate(leaderboard, 1):
                user = await self.bot.fetch_user(coach[0])
                username = user.display_name
                output += str(rank) + '. ' + username + \
                    f': {coach[1]}-{coach[2]} ({coach[3]})\n'
            await ctx.send('```yaml\n' + '[Leaderboard]\n' + output + '```')

    @commands.command()
    @check_channel('coaches')
    async def info(self, ctx, user: discord.Member):
        """Display user information for the specified coach."""
        draft_data, coach_data = get_info(user.id)
        output = ''
        if draft_data == 1:
            output += f'{user.display_name} is not a valid coach.'
            await ctx.send(':x: ' + output)
        else:
            if len(draft_data) == 0:
                output += f'{user.display_name} has not drafted a pokemon yet.'
            coach_info = self.draft_cog.skipped_coaches.get(user.id)
            remaining_budget = self.draft_cog.draft_queue[coach_info[2]][1]
            for pokemon in draft_data:
                output += str(pokemon[0]) + '. ' + \
                    pokemon[1] + f' ({pokemon[2]})\n'
            await ctx.send('```yaml\n[' + user.display_name + ']\nRemaining Budget:'
                           f'{remaining_budget} | Remaining Transactions: {coach_data[1]}'
                           f' | # Times Skipped: {coach_data[0]}\n' + output + '```')

    @register.error
    @replace.error
    @info.error
    async def error_handler(self, ctx, error):
        """Respond to discord.py errors."""
        if isinstance(error, commands.MissingRole):
            await ctx.send(':x: You do not have permission to use this command.')
        elif isinstance(error, commands.errors.MemberNotFound):
            await ctx.send(':x: Please specify valid server member(s).')
