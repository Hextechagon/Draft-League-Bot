"""Commands for drafting."""
import datetime
import asyncio
import queue
import discord
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
        # each pair consists of discordid : # times skipped
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
                self.skipped_coaches[coach[0]] = [0, queue.Queue()]
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
            for coach in await get_order():
                user = await self.bot.fetch_user(coach[1])
                username = user.name
                output += str(coach[0]) + '. ' + username + '\n'
            await ctx.send('```yaml\n' + '[Draft Order]\n' + output + '```')

    async def get_next(self):
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

    async def start_timer(self, ctx, current_time, duration):
        """Manage the timing of the drafting phase."""
        self.drafted = False
        # CHANGE DURATION FROM MINUTES TO HOURS AFTER TESTING
        self.draft_deadline = current_time + \
            datetime.timedelta(minutes=duration)
        while current_time < self.draft_deadline:
            if self.drafted is True:
                break
            await asyncio.sleep(3)
            current_time = datetime.datetime.now()
        prev_coach = self.draft_position
        prev_round = self.draft_round
        await self.get_next()
        while self.draft_queue[self.draft_position][2] is True:
            await self.get_next()
        if self.drafted is False:
            self.skipped_coaches[prev_coach][0] += 1
            self.skipped_coaches[prev_coach][1].put(prev_round)
            # channel = self.bot.get_channel(1085977763833446401); await channel.send
            await ctx.send(f':arrows_clockwise: <@{self.draft_queue[prev_coach][0]}> is skipped; <@{self.draft_queue[self.draft_position][0]}> is now on the clock.')
        else:
            await ctx.send(f':arrows_clockwise: <@{self.draft_queue[self.draft_position][0]}> is now on the clock.')

    @commands.command()
    @commands.has_role('Draft Host')
    @commands.check(lambda ctx: ctx.channel.id == 1085977763833446401)
    async def begin(self, ctx):
        """Initiate the draft process and manage the timer."""
        if self.draft_round != 0:
            await ctx.send(':x: You cannot use this command at the current stage.')
            return
        self.draft_round += 1
        await ctx.send(f'The draft process has started.\n<@{self.draft_queue[self.draft_position][0]}> is now on the clock.')
        while self.num_finalized < len(self.draft_queue):
            # modify draft timer based on round and halve every time a coach is skipped
            if self.draft_round == 1:
                duration = 24
            elif self.draft_round > 1 and self.draft_round < 4:
                duration = 8
            elif self.draft_round >= 4 and self.draft_round < 9:
                duration = 6
            else:
                duration = 4
            duration = duration * (0.5**self.skipped_coaches[self.draft_queue
                                                             [self.draft_position][0]][0])
            await self.start_timer(ctx, datetime.datetime.now(), duration)
            await asyncio.sleep(3)

    async def acquire(self, ctx, pokemon, skipped, round_skipped=0):
        """Reduce redundancy in the select command."""
        if skipped is False:
            status, pname, remaining_points = pick_pokemon(pokemon, self.draft_round, ctx.author.id,
                                                           self.draft_queue[self.draft_position][1])
        else:
            status, pname, remaining_points = pick_pokemon(pokemon, round_skipped, ctx.author.id,
                                                           self.draft_queue[self.draft_position][1])
        if status == 0:
            await ctx.send(f':white_check_mark: {pname} has been added to your team; you have {remaining_points} points left.')
            self.draft_queue[self.draft_position][1] = remaining_points
            if skipped is False:
                self.drafted = True
        elif status == 1:
            await ctx.send(f':x: {pname} is not a valid Pokémon; you must enter the exact name stated in the Google Sheets.')
        elif status == 2:
            await ctx.send(f':x: {pname} is already taken.')
        else:
            await ctx.send(f':x: You do not have enough points to draft {pname}.')

    @commands.command()
    @commands.has_role('Draft League')
    @commands.check(lambda ctx: ctx.channel.id == 1085977763833446401)
    async def select(self, ctx, pokemon):
        """Add the specified pokemon to the coach's party."""
        if self.draft_round < 1:
            await ctx.send(':x: You cannot use this command at the current stage.')
        elif ctx.author.id != self.draft_queue[self.draft_position][0]:
            skipped_coach = self.skipped_coaches.get(ctx.author.id)
            print(list(skipped_coach[1].queue))
            if skipped_coach is None:
                await ctx.send(':x: You are not a valid coach.')
            else:
                if skipped_coach[1].qsize() > 0:
                    round_skipped = skipped_coach[1].get()
                    await self.acquire(ctx, pokemon, True, round_skipped)
                else:
                    await ctx.send(':x: It is not your turn to draft yet.')
        else:
            await self.acquire(ctx, pokemon, False)

    @commands.command()
    @commands.has_role('Draft League')
    @commands.check(lambda ctx: ctx.channel.id == 1085977763833446401)
    async def preselect(self, ctx, *pokemon):
        """Enable coaches to save picks for automatic selection."""

    @commands.command()
    @commands.has_role('Draft League')
    @commands.check(lambda ctx: ctx.channel.id == 1085977763833446401)
    async def edit(self, ctx, prev_pokemon, pokemon):
        """Change the pick that a coach made before the next coach picks."""
        # TODO

    @commands.command()
    @commands.has_role('Draft Host')
    @commands.check(lambda ctx: ctx.channel.id == 1085977763833446401)
    async def dtime(self, ctx, action, amount):
        """Modify the amount of time a coach has for drafting."""
        # TODO

    @commands.command()
    @commands.has_role('Draft Host')
    @commands.check(lambda ctx: ctx.channel.id == 1085977763833446401)
    async def resume(self, ctx):
        """Resume the bot processes after updates."""
        # TODO

    @commands.command()
    @commands.has_role('Draft League')
    @commands.check(lambda ctx: ctx.channel.id == 1085977763833446401)
    async def finish(self, ctx):
        """Specify that a coach completed the drafting phase."""
        finalize(ctx.author.id, self.draft_queue[self.draft_position][1])
        coach_index = None
        for index, coach in enumerate(self.draft_queue):
            if coach[0] == ctx.author.id:
                coach_index = index
                break
        if coach_index is not None:
            # maybe add another check for if finalized already
            self.draft_queue[coach_index][2] = True
            user = await self.bot.fetch_user(ctx.author.id)
            username = user.name
            await ctx.send(f':white_check_mark: {username} has finished drafting.')
            self.num_finalized += 1
        else:
            await ctx.send(f':x: {ctx.author.id} is not a valid coach.')

    @commands.command()
    @commands.has_role('Draft Host')
    @commands.check(lambda ctx: ctx.channel.id == 1085977763833446401)
    async def reenter(self, ctx):
        """Re-enter a finalized coach into the draft."""
        # maybe need a finalize function for hoster as well (or put in finish function)

    @commands.command()
    async def add(self, ctx, *pokemon):
        """Add the specified pokemon(s) to the coach's party during FA."""
        # TODO: see comment above (ONLY available after drafting finished)
        # recommend do remove before add to make sure budget not exceeded

    @commands.command()
    async def remove(self, ctx, *pokemon):
        """Remove the specified pokemon(s) from the coach's party during FA."""
        # TODO: see comment above (ONLY available after drafting finished)

    @commands.command()
    async def trade(self, ctx, user: discord.Member, pokemon1, pokemon2):
        """Complete a trade with another coach."""
        # TODO: see comment above (ONLY available after drafting finished)
        # recommend do remove before add to make sure budget not exceeded

    @randomize.error
    @begin.error
    @select.error
    async def error_handler(self, ctx, error):
        """Respond to discord.py errors."""
        if isinstance(error, commands.MissingRole):
            await ctx.send(':x: You do not have permission to use this command.')
