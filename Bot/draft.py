"""Commands for drafting."""
import datetime
import asyncio
import queue
import discord
# import pytz
from discord.ext import commands
from draft_helpers import randomize_order, get_order, pick_pokemon, finalize


# pylint: disable=R0902
# pylint: disable=R0913
class Draft(commands.Cog):
    """Draft class."""

    def __init__(self, bot):
        """Initialize the draft cog."""
        self.bot = bot
        # stores [discordid, budget, finalized]
        self.draft_queue = []
        # stores discordid : [# times skipped, skipped round(s) queue, index in draft_queue]
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
    @commands.check(lambda ctx: ctx.channel.id == 1114021526291890260)
    async def randomize(self, ctx):
        """Randomize the draft order."""
        # check if the order is already generated
        if self.draft_round != -1:
            await ctx.send(':x: You cannot modify the draft order at the current stage.')
            return
        random_order = randomize_order()
        output = ''
        # check if there are enough coaches registered for the draft league
        if isinstance(random_order, int):
            output += f':x: The draft league does not have enough players ({random_order}/16).'
            await ctx.send(output)
        else:
            for order, coach in enumerate(random_order, 1):
                # populate draft_queue and skipped_coaches with the randomized coaches
                self.draft_queue.append([coach[0], 125, False])
                self.skipped_coaches[coach[0]] = [0, queue.Queue(), order - 1]
                user = await self.bot.fetch_user(coach[0])
                username = user.name
                output += str(order) + '. ' + username + '\n'
            # display the order of the draft and change the status to active
            await ctx.send('```yaml\n' + '[Draft Order]\n' + output + '```')
            self.draft_round += 1

    @commands.command()
    @commands.has_role('Draft League')
    @commands.check(lambda ctx: ctx.channel.id == 1114021526291890260)
    async def order(self, ctx):
        """Display the draft order list."""
        # check if the order has been generated
        if self.draft_round == -1:
            await ctx.send(':x: The draft order has not been generated yet.')
        else:
            # display the order of the draft
            output = ''
            for coach in await get_order():
                user = await self.bot.fetch_user(coach[1])
                username = user.name
                output += str(coach[0]) + '. ' + username + '\n'
            await ctx.send('```yaml\n' + '[Draft Order]\n' + output + '```')

    async def get_next(self):
        """Determine the next coach in the drafting process."""
        if self.draft_round % 2 == 0:
            # advance the draft queue towards the left if the round is even
            if self.draft_position != 0:
                self.draft_position -= 1
            # increment the round when the wheel pick is reached
            else:
                self.draft_round += 1
        else:
            # advance the draft queue towards the right if the round is odd
            if self.draft_position != (len(self.draft_queue) - 1):
                self.draft_position += 1
            # increment the round when the wheel pick is reached
            else:
                self.draft_round += 1

    async def start_timer(self, ctx, current_time, duration):
        """Manage the timing of the drafting phase."""
        # reset the draft status and calculate the draft deadline
        self.drafted = False
        # CHANGE DURATION FROM MINUTES TO HOURS AFTER TESTING
        self.draft_deadline = current_time + \
            datetime.timedelta(minutes=duration)
        # keep track of the draft time
        while current_time < self.draft_deadline:
            if self.drafted is True:
                break
            await asyncio.sleep(2)
            current_time = datetime.datetime.now()
        # save the previous information and advance the draft position
        prev_pos = self.draft_position
        prev_round = self.draft_round
        await self.get_next()
        # keep advancing the draft position until reaching a non-finalized coach
        while self.draft_queue[self.draft_position][2] is True and self.num_finalized < \
                len(self.draft_queue):
            await self.get_next()
        if self.drafted is False:
            # update skipped_coaches if the previous coach did not draft within the allotted time
            prev_id = self.draft_queue[prev_pos]
            self.skipped_coaches[prev_id][0] += 1
            self.skipped_coaches[prev_id][1].put(prev_round)
            await ctx.send(f':arrows_clockwise: <@{prev_id}> is'
                           f' skipped; <@{self.draft_queue[self.draft_position][0]}> is now'
                           f'on the clock (draft by ).')
        else: 
            await ctx.send(f':arrows_clockwise: <@{self.draft_queue[self.draft_position][0]}>'
                           f' is now on the clock (draft by ).')

    @commands.command()
    @commands.has_role('Draft Host')
    @commands.check(lambda ctx: ctx.channel.id == 1114021526291890260)
    async def begin(self, ctx):
        """Initiate the draft process and manage the timer until all coaches have finalized."""
        if self.draft_round != 0:
            await ctx.send(':x: You cannot use this command at the current stage.')
            return
        self.draft_round += 1
        await ctx.send(f'The draft has started.\n<@{self.draft_queue[self.draft_position][0]}>'
                       f' is now on the clock (draft by ).')
        while self.num_finalized < len(self.draft_queue):
            # modify draft timer based on round
            if self.draft_round == 1:
                duration = 24
            elif self.draft_round > 1 and self.draft_round < 4:
                duration = 8
            elif self.draft_round >= 4 and self.draft_round < 9:
                duration = 6
            else:
                duration = 4
            # halve the coach's allotted draft time based on the number of times he/she was skipped
            duration = duration * (0.5**self.skipped_coaches[self.draft_queue
                                                             [self.draft_position][0]][0])
            await self.start_timer(ctx, datetime.datetime.now(), duration)
            await asyncio.sleep(4)
        # put a message with more information (e.g. FA began and number of trades)
        await ctx.send('The draft has ended.')

    async def acquire(self, ctx, pokemon, skipped, position, round_skipped=0):
        """Reduce redundancy in the select command."""
        if skipped is False:
            # handle normal drafting
            status, pname, remaining_points = pick_pokemon(pokemon, self.draft_round, ctx.author.id,
                                                           self.draft_queue[position][1])
        else:
            # handle skipped coach drafting
            status, pname, remaining_points = pick_pokemon(pokemon, round_skipped, ctx.author.id,
                                                           self.draft_queue[position][1])
        if status == 0:
            await ctx.send(f':white_check_mark: {pname} has been added to your team; you have'
                           f' {remaining_points} points left.')
            self.draft_queue[position][1] = remaining_points
            if skipped is False:
                # end the timer if the selection is not from a skipped coach
                self.drafted = True
        elif status == 1:
            await ctx.send(f':x: {pname} is not a valid Pokémon; you must enter the exact name'
                           ' stated in the Google Sheets.')
        elif status == 2:
            await ctx.send(f':x: {pname} is already taken.')
        else:
            await ctx.send(f':x: You do not have enough points to draft {pname}.')

    @commands.command()
    @commands.has_role('Draft League')
    @commands.check(lambda ctx: ctx.channel.id == 1114021526291890260)
    async def select(self, ctx, pokemon):
        """Add the specified pokemon to the coach's party."""
        if self.draft_round < 1:
            await ctx.send(':x: You cannot use this command at the current stage.')
        # check if user issuing command is the coach in the current iteration of draft_position
        elif ctx.author.id != self.draft_queue[self.draft_position][0]:
            skipped_coach = self.skipped_coaches.get(ctx.author.id)
            if skipped_coach is None:
                await ctx.send(':x: You are not a valid coach.')
            else:
                # handle skipped coaches drafting
                if skipped_coach[1].qsize() > 0:
                    round_skipped = skipped_coach[1].get()
                    await self.acquire(ctx, pokemon, True, skipped_coach[2], round_skipped)
                else:
                    await ctx.send(':x: It is not your turn to draft yet.')
        else:
            await self.acquire(ctx, pokemon, False, self.draft_position)

    @commands.command()
    @commands.has_role('Draft League')
    @commands.check(lambda ctx: ctx.channel.id == 1114021526291890260)
    async def preselect(self, ctx, *pokemon):
        """Enable coaches to save picks for automatic selection."""

    @commands.command()
    @commands.has_role('Draft League')
    @commands.check(lambda ctx: ctx.channel.id == 1114021526291890260)
    async def edit(self, ctx, prev_pokemon, pokemon):
        """Change the pick that a coach made before the next coach picks."""
        # TODO

    @commands.command()
    @commands.has_role('Draft Host')
    @commands.check(lambda ctx: ctx.channel.id == 1114021526291890260)
    async def etime(self, ctx, user: discord.Member, amount):
        """Modify the amount of time a coach has for drafting."""
        # TODO

    @commands.command()
    @commands.has_role('Draft Host')
    @commands.check(lambda ctx: ctx.channel.id == 1114021526291890260)
    async def resume(self, ctx):
        """Resume the bot processes after updates."""
        # TODO

    @commands.command()
    @commands.has_role('Draft League')
    @commands.check(lambda ctx: ctx.channel.id == 1114021526291890260)
    async def finish(self, ctx):
        """Specify that a coach completed the drafting phase."""
        finalize(ctx.author.id, self.draft_queue[self.draft_position][1])
        coach_info = self.skipped_coaches.get(ctx.author.id)
        if coach_info is not None and self.draft_queue[coach_info[2]][2] is False:
            # set the coach's finalized status in draft_queue as true
            self.draft_queue[coach_info[2]][2] = True
            user = await self.bot.fetch_user(ctx.author.id)
            username = user.name
            await ctx.send(f':white_check_mark: {username} has finished drafting.')
            self.num_finalized += 1
            if coach_info[2] == self.draft_position:
                # stop draft timer if user is the coach in the current draft_position
                self.drafted = True
        else:
            await ctx.send(f':x: {ctx.author.id} is not a valid coach or already finalized.')

    @commands.command()
    @commands.has_role('Draft Host')
    @commands.check(lambda ctx: ctx.channel.id == 1114021526291890260)
    async def reenter(self, ctx, user: discord.Member):
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
