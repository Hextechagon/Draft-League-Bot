"""Commands for coaches."""
import discord
from discord.ext import commands
from coach_helpers import insert_coach, replace_coach, get_leaderboard, get_info


class Coach(commands.Cog):
    """Coaches class."""

    def __init__(self, bot):
        """Initialize the coach cog."""
        self.bot = bot
        self.draft_cog = self.bot.get_cog('Draft')

    @commands.command()
    @commands.has_role('Draft Host')
    @commands.check(lambda ctx: ctx.channel.id == 1085977763833446401)
    async def register(self, ctx, user: discord.Member):
        """Enter the specified server member into the draft league."""
        status = insert_coach(user.id, user.name)
        if status == 0:
            await ctx.send(f':white_check_mark: {user.name} has been registered as a coach.')
        elif status == 1:
            await ctx.send(':x: The draft league is currently full.')
        else:
            await ctx.send(f':x: {user.name} is already a coach.')

    @commands.command()
    @commands.has_role('Draft Host')
    @commands.check(lambda ctx: ctx.channel.id == 1085977763833446401)
    async def bulk_register(self, ctx, *args: discord.Member):
        """Enter the specified server members into the draft league."""
        # TODO: status = bulk_insert(args)

    @commands.command()
    @commands.has_role('Draft Host')
    @commands.check(lambda ctx: ctx.channel.id == 1085977763833446401)
    async def replace(self, ctx, user1: discord.Member, user2: discord.Member):
        """Replace a current coach with the specified server member (inherits previous data)."""
        status = replace_coach(user1.id, user2.id, user2.name)
        if status == 0:
            # update the draft_queue if the draft process is active
            if self.draft_cog.draft_round > 0:
                # FIX THIS
                coach_index = [i for i, coach in enumerate(
                    self.draft_cog.draft_queue) if coach[0] == ctx.author.id]
                if coach_index:
                    self.draft_cog.draft_queue[coach_index][0] = user2.id
                    retained_info = self.draft_cog.skipped_coaches.pop(
                        user1.id)
                    self.draft_cog.skipped_coaches[user2.id] = retained_info
            await ctx.send(f':white_check_mark: {user1.name} has been replaced by \
                           {user2.name} as a coach.')
        elif status == 1:
            await ctx.send(f':x: {user1.name} is not a valid coach.')
        else:
            await ctx.send(f':x: {user2.name} is already a coach.')

    @commands.command()
    @commands.check(lambda ctx: ctx.channel.id == 1085977763833446401)
    async def rank(self, ctx):
        """Display the leaderboard containing all current coaches."""
        leaderboard = await get_leaderboard()
        output = ''
        if len(leaderboard) == 0:
            output += 'There are no registered coaches.'
            await ctx.send(':x: ' + output)
        else:
            for rank, coach in enumerate(leaderboard, 1):
                user = await self.bot.fetch_user(coach[0])
                username = user.name
                output += str(rank) + '. ' + username + '\n'
            await ctx.send('```yaml\n' + '[Leaderboard]\n' + output + '```')

    @commands.command()
    async def info(self, ctx, user: discord.Member):
        """Display user information (pokemon, budget for now, update later)."""
        coach_data = await get_info(user.id)
        output = ''
        if coach_data == 1:
            # FIX: shows this message even if valid coach; should still output budget (use separate queries in the helper function?)
            output += f'{user.name} has not drafted yet.'
            await ctx.send(':warning: ' + output)
        elif coach_data == 2:
            output += f'{user.name} is not a valid coach.'
            await ctx.send(':x: ' + output)
        else:
            budget = 125
            for pokemon in coach_data:
                output += str(pokemon[0]) + '. ' + \
                    pokemon[1] + f' ({pokemon[2]})\n'
                budget -= pokemon[2]
            await ctx.send('```yaml\n[' + user.name + f'\'s Draft] : {budget} points remaining\n' +
                           output + '```')

    @register.error
    @replace.error
    @info.error
    async def error_handler(self, ctx, error):
        """Respond to discord.py errors."""
        if isinstance(error, commands.MissingRole):
            await ctx.send(':x: You do not have permission to use this command.')
        elif isinstance(error, commands.errors.MemberNotFound):
            await ctx.send(':x: Please specify valid server member(s).')
