"""Commands for drafting."""
import datetime
import asyncio
import discord
from discord.ext import commands
from draft_helpers import randomize_order, pick_pokemon


class Draft(commands.Cog):
    """Draft class."""

    def __init__(self, bot):
        """Initialize the draft cog."""
        self.bot = bot
        # each element consists of [discordid, budget]
        self.draft_queue = []
        self.skipped_coaches = []
        self.draft_round = 0
        self.draft_position = 0
        self.drafted = False
        self.draft_deadline = None

    async def find_next(self):
        """Determine the next coach in the drafting process."""
        # think about logic here
        if self.draft_round % 2 == 0:
            if self.draft_position != (len(self.draft_queue) - 1):
                self.draft_position += 1
            else:
                self.draft_round += 1
        else:
            if self.draft_position != 0:
                self.draft_position -= 1
            else:
                self.draft_round += 1

    async def start_timer(self, current_time, duration):
        """Manage the timing of the drafting phase."""
        self.drafted = False
        self.draft_deadline = current_time + \
            datetime.timedelta(minutes=duration)
        while current_time < self.draft_deadline:
            # check if drafted, if true break out; else await and update
            if self.drafted is True:
                break
            # MAYBE NEED TO INCREASE THIS!!!
            await asyncio.sleep(5)
            current_time = datetime.datetime.now()
        # FIX: HOW TO HALVE: INSTANCE VARIABLE???
        prev_coach = self.draft_position
        await self.find_next()
        if self.drafted is False:
            self.skipped_coaches.append(self.draft_position)
            channel = self.bot.get_channel(1085977763833446401)
            await channel.send(f'<@{self.draft_queue[prev_coach][0]}> is skipped; \
                               <@{self.draft_queue[self.draft_position][0]}> is now on the clock.')
        else:
            await channel.send(f'<@{self.draft_queue[self.draft_position][0]}> \
                               is now on the clock.')

    @commands.command()
    @commands.has_role('Draft Host')
    @commands.check(lambda ctx: ctx.channel.id == 1085977763833446401)
    async def randomize(self, ctx):
        """Randomize the draft order."""
        if not (self.draft_round == 0 and self.draft_position == 0):
            await ctx.send('The draft process already started, so the order cannot be modified.')
            return
        random_order = randomize_order()
        output = ''
        if isinstance(random_order, int):
            output += f':x: The draft league does not have enough players ({random_order}/16).'
            await ctx.send(output)
        else:
            self.draft_queue = random_order
            self.draft_round = 1
            for order, coach in enumerate(self.draft_queue, 1):
                user = await self.bot.fetch_user(coach[0])
                username = user.name
                output += str(order) + '. ' + username + '\n'
            await ctx.send('```yaml\n' + '[Draft Order]\n' + output + '```')

    @commands.command()
    @commands.has_role('Draft Host')
    @commands.check(lambda ctx: ctx.channel.id == 1085977763833446401)
    async def begin(self, ctx):
        """Initiate the draft process."""
        await ctx.send(f'The draft process has started.\n<@\
                       {self.draft_queue[self.draft_position][0]}> is now on the clock.')
        await self.start_timer(datetime.datetime.now(), 1)

    @commands.command()
    @commands.has_role('Draft League')
    @commands.check(lambda ctx: ctx.channel.id == 1085977763833446401)
    async def order(self, ctx):
        """Display the draft order list."""
        return

    @commands.command()
    @commands.has_role('Draft League')
    @commands.check(lambda ctx: ctx.channel.id == 1085977763833446401)
    async def select(self, ctx, pokemon):
        """Add the specified pokemon to the coach's party."""
        # also need to check if command sender is the one who should be drafting (decorator).
        if self.draft_round == 0:
            await ctx.send(':x: The draft process has not started yet.')
        elif ctx.author.id != self.draft_queue[self.draft_position][0]:
            await ctx.send(':x: It is not your turn to draft yet.')
        else:
            status, remaining_points = pick_pokemon(pokemon, ctx.author.id, self.draft_queue[self.draft_position][1])
            if status == 0:
                await ctx.send(f':white_check_mark: {pokemon} has been added to \
                               your team; you have {remaining_points} points left.')
                self.drafted = True
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
    @commands.has_role('Draft League')
    @commands.check(lambda ctx: ctx.channel.id == 1085977763833446401)
    async def final(self, ctx):
        """Specify that a coach completed his or her draft."""
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

    @randomize.error
    @begin.error
    @select.error
    async def error_handler(self, ctx, error):
        """Respond to discord.py errors."""
        if isinstance(error, commands.MissingRole):
            await ctx.send(':x: You do not have permission to use this command.')
