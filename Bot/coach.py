"""Commands for coaches."""
import discord
from discord.ext import commands
from coach_helpers import insert_coach, delete_coach, replace_coach, get_leaderboard


class Coach(commands.Cog):
    """Coaches class."""

    def __init__(self, bot):
        """Initialize the coach cog."""
        self.bot = bot

    @commands.command()
    @commands.has_role('Draft Host')
    @commands.check(lambda ctx: ctx.channel.id == 1085977763833446401)
    async def register(self, ctx, user: discord.Member, team_name = 'TBD'):
        """Enter the specified server member into the draft league."""
        status = insert_coach(user.id, user.name, team_name)
        if status == 0:
            await ctx.send(f':ballot_box_with_check: {user.name} has been registered as a coach.')
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
    async def delete(self, ctx, user: discord.Member):
        """Remove the specified server member from the draft league."""
        status = delete_coach(user.id)
        if status == 0:
            await ctx.send(f':ballot_box_with_check: {user.name} has been removed as a coach.')
        else:
            await ctx.send(f':x: {user.name} is not a valid coach.')

    @commands.command()
    @commands.has_role('Draft Host')
    @commands.check(lambda ctx: ctx.channel.id == 1085977763833446401)
    async def replace(self, ctx, user1: discord.Member, user2: discord.Member, team_name = 'TBD'):
        """Replace a current coach with the specified server member (inherits all previous coach data)."""
        status = replace_coach(user1.id, user2.id, user2.name, team_name)
        if status == 0:
            await ctx.send(f':ballot_box_with_check: {user1.name} has been replaced by {user2.name} as a coach.')
        elif status == 1:
            await ctx.send(f':x: {user1.name} is not a valid coach.')
        else:
            await ctx.send(f':x: {user2.name} is already a coach.')

    @commands.command()
    async def rank(self, ctx):
        """Display the leaderboard containing all current coaches."""
        coaches = get_leaderboard()
        output = ''
        if len(coaches) == 0:
            output += 'There are no registered coaches.'
            await ctx.send(':x: ' + output)
        else:
            for rank, coach in enumerate(coaches, 1):
                output += str(rank) + '. ' + coach + '\n'
            await ctx.send('```yaml\n' + '[Leaderboard]\n' + output + '```')
    
    @commands.command()
    async def info(self, ctx, user: discord.Member):
        """Display user information (pokemon, budget for now, update later)."""

    @register.error
    @delete.error
    @replace.error
    async def error_handler(self, ctx, error):
        """Respond to discord.py errors."""
        if isinstance(error, commands.MissingRole):
            await ctx.send(':x: You do not have permission to use this command.')
        elif isinstance(error, commands.errors.MemberNotFound):
            await ctx.send(':x: Please specify valid server member(s).')
