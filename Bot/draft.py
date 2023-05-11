"""Commands for drafting."""
import bisect
import datetime
import asyncio
from discord.ext import commands
from draft_helpers import randomize_order, get_order, pick_pokemon, finalize


 # pylint: disable=R0902
class Draft(commands.Cog):
    """Draft class."""

    def __init__(self, bot):
        """Initialize the draft cog."""
        self.bot = bot
        # each element consists of [discordid, budget, finalized]
        self.draft_queue = []
        # each element consists of [discordid, # times skipped]
        self.skipped_coaches = {}
        # -3 = end of FA, -2 = end of draft, -1 = order not generated yet
        # 0 = order generated, but draft not started yet 1+ = draft active
        self.draft_round = -1
        self.draft_position = 0
        self.drafted = False
        self.draft_deadline = None
        self.num_finalized = 0

    @commands.command()
    @commands.has_role('Draft Host')
    @commands.check(lambda ctx: ctx.channel.id == 1085977763833446401)
    async def randomize(self, ctx):
        """Randomize the draft order."""
        if self.draft_round != -1:
            await ctx.send(':x: You cannot modify the draft order at the current stage.')
            return
        random_order = randomize_order()
        output = ''
        if isinstance(random_order, int):
            output += f':x: The draft league does not have enough players ({random_order}/16).'
            await ctx.send(output)
        else:
            for order, coach in enumerate(random_order, 1):
                self.draft_queue.append([coach[0], 125, False])
                self.skipped_coaches[coach[0]] = 0
                user = await self.bot.fetch_user(coach[0])
                username = user.name
                output += str(order) + '. ' + username + '\n'
            await ctx.send('```yaml\n' + '[Draft Order]\n' + output + '```')
            self.draft_round += 1

    @commands.command()
    @commands.has_role('Draft League')
    @commands.check(lambda ctx: ctx.channel.id == 1085977763833446401)
    async def order(self, ctx):
        """Display the draft order list."""
        if self.draft_round == -1:
            await ctx.send(':x: The draft order has not been generated yet.')
        else:
            output = ''
            for coach in get_order():
                user = await self.bot.fetch_user(coach[1])
                username = user.name
                output += str(coach[0]) + '. ' + username + '\n'
                await ctx.send('```yaml\n' + '[Draft Order]\n' + output + '```')

    async def find_next(self):
        """Determine the next coach in the drafting process."""
        if self.draft_round % 2 == 0:
            if self.draft_position != 0:
                self.draft_position -= 1
            else:
                self.draft_round += 1
        else:
            if self.draft_position != (len(self.draft_queue) - 1):
                self.draft_position += 1
            else:
                self.draft_round += 1

    async def start_timer(self, current_time, duration):
        """Manage the timing of the drafting phase."""
        self.drafted = False
        # CHANGE DURATION FROM MINUTES TO HOURS AFTER TESTING
        self.draft_deadline = current_time + \
            datetime.timedelta(minutes=duration)
        while current_time < self.draft_deadline:
            if self.drafted is True:
                break
            await asyncio.sleep(1)
            current_time = datetime.datetime.now()
        prev_coach = self.draft_position
        await self.find_next()
        while self.draft_queue[self.draft_position][2] is True:
            await self.find_next()
        if self.drafted is False:
            self.skipped_coaches[prev_coach] += 1
            channel = self.bot.get_channel(1085977763833446401)
            await channel.send(f':arrows_clockwise: <@{self.draft_queue[prev_coach][0]}> is \
                               skipped; <@{self.draft_queue[self.draft_position][0]}> \
                               is now on the clock.')
        else:
            await channel.send(f':arrows_clockwise: <@\
                               {self.draft_queue[self.draft_position][0]}> is now on the clock.')

    @commands.command()
    @commands.has_role('Draft Host')
    @commands.check(lambda ctx: ctx.channel.id == 1085977763833446401)
    async def begin(self, ctx):
        """Initiate the draft process and manage the timer."""
        if self.draft_round != 0:
            await ctx.send(':x: You cannot use this command at the current stage.')
            return
        self.draft_round += 1
        await ctx.send(f'The draft process has started.\n<@\
                       {self.draft_queue[self.draft_position][0]}> is now on the clock.')
        while self.num_finalized < len(self.draft_queue):
            await self.start_timer(datetime.datetime.now(), 1)
            await asyncio.sleep(3)

    @commands.command()
    @commands.has_role('Draft League')
    @commands.check(lambda ctx: ctx.channel.id == 1085977763833446401)
    async def select(self, ctx, pokemon):
        """Add the specified pokemon to the coach's party."""
        if self.draft_round < 1:
            await ctx.send(':x: You cannot use this command at the current stage.')
        elif ctx.author.id != self.draft_queue[self.draft_position][0]:
            await ctx.send(':x: It is not your turn to draft yet.')
        else:
            status, pname, remaining_points = pick_pokemon(pokemon, self.draft_round, ctx.author.id,
                                                           self.draft_queue[self.draft_position][1])
            if status == 0:
                await ctx.send(f':white_check_mark: {pname} has been added to \
                               your team; you have {remaining_points} points left.')
                self.draft_queue[self.draft_position][1] = remaining_points
                self.drafted = True
            elif status == 1:
                await ctx.send(f':x: {pname} is not a valid Pokémon; you must enter the exact \
                               name stated in the Google Sheets.')
            elif status == 2:
                await ctx.send(f':x: {pname} is already taken.')
            else:
                await ctx.send(f':x: You do not have enough points to draft {pname}.')

    @commands.command()
    @commands.has_role('Draft League')
    @commands.check(lambda ctx: ctx.channel.id == 1085977763833446401)
    async def edit(self, ctx, prev_pokemon, pokemon):
        """Change the pick that a coach made before the next coach picks."""
        # TODO

    @commands.command()
    @commands.has_role('Draft League')
    @commands.check(lambda ctx: ctx.channel.id == 1085977763833446401)
    async def done(self, ctx):
        """Specify that a coach completed the drafting phase."""
        finalize(ctx.author.id, self.draft_queue[self.draft_position][1])
        coach_index = bisect.bisect_left([coach[0] for coach in self.draft_queue],
                                         ctx.author.id)
        if coach_index < len(self.draft_queue) and self.draft_queue[coach_index][0] == \
                                                                        ctx.author.id:
            self.draft_queue[coach_index][2] = True
            user = await self.bot.fetch_user(ctx.author.id)
            username = user.name
            await ctx.send(f':white_check_mark: {username} has finished drafting.')
            self.numfinalized += 1
        else:
            await ctx.send(f':x: {ctx.author.id} is not a valid coach.')

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
