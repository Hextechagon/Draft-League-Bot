"""Commands for drafting."""
import discord
from discord.ext import commands
from draft_helpers import randomize_order, pick_pokemon


class Draft(commands.Cog):
    """Draft class."""

    def __init__(self, bot):
        """Initialize the draft cog."""
        self.bot = bot
        self.draft_active = False
        self.draft_order = []

    @commands.command()
    @commands.has_role('Draft Host')
    @commands.check(lambda ctx: ctx.channel.id == 1085977763833446401)
    async def start(self, ctx):
        """Initiate the draft process by randomizing the draft order and beginning the timer."""
        random_order = randomize_order()
        output = ''
        if isinstance(random_order, int):
            output += f':x: The draft league does not have enough players ({random_order}/16).'
            await ctx.send(output)
        else:
            self.draft_order = random_order
            self.draft_active = True
            for order, coach in enumerate(self.draft_order, 1):
                output += str(order) + '. ' + coach + '\n'
            await ctx.send('```yaml\n' + '[Draft Order]\n' + output + '```')

    @commands.command()
    @commands.has_role('Draft League')
    @commands.check(lambda ctx: ctx.channel.id == 1085977763833446401)
    async def select(self, ctx, pokemon):
        """Add the specified pokemon to the coach's party."""
        # also need to check if command sender is the one who should be drafting (decorator).
        # checks if the draft is active (maybe use decorator)
        if self.draft_active is False:
            await ctx.send(':x: The draft process has not started yet.')
        else:
            status, remaining_points = pick_pokemon(pokemon, ctx.author.id)
            if status == 0:
                await ctx.send(f':white_check_mark: {pokemon} has been added to \
                               your team; you have {remaining_points} points left.')
            elif status == 1:
                # FIX: invalid pokemon outputs this too (select pname in helper query instead of putting it in condition, and check if is null after fetchone)
                # FIX: two word pokemon (e.g. Iron Valient) shows up as already taken since only first word is read in
                # maybe ask users to put the two words together with a special symbol in between
                await ctx.send(f':x: {pokemon} is already taken.')
            else:
                await ctx.send(f':x: You do not have enough points to draft {pokemon}.')

    @commands.command()
    @commands.has_role('Draft League')
    @commands.check(lambda ctx: ctx.channel.id == 1085977763833446401)
    async def edit(self, ctx, prev_pokemon, pokemon):
        """Change the pick that a coach made before the next coach picks."""
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

    @start.error
    @select.error
    async def error_handler(self, ctx, error):
        """Respond to discord.py errors."""
        if isinstance(error, commands.MissingRole):
            await ctx.send(':x: You do not have permission to use this command.')
