"""Commands for drafting.
!randomize
!order
!begin
!select pokemon_name
!preselect TODO
!edit perv_pokemon new_pokemon
!etime minutes
!finish (<@user>) TODO
!reenter <@user> TODO
!fadd pokemon_name TODO force add pokemon by hoster
!fremove pokemon_name TODO force remove pokemon by hoster
!eskipped <@user> amount
!add <pokemon_list> TODO
!remove <pokemon_list> TODO
!trade <@user> pokemon1 pokemon2 TODO
!resume TODO

Notes: 
- pokemon_list consists of pokemon names separated by one space
- replace the space(s) with a ! if a pokemon name consists of multiple words
- if someone the coach entrusted drafted for him/her within the draft duration and the hoster did not fadd it 
before the draft deadline, the hoster has to use !eskipped to correct the time penalty associated with # skips
"""
import datetime
import asyncio
import queue
import discord
import pytz
from discord.ext import commands
from draft_helpers import randomize_order, get_order, pick_pokemon, remove_pokemon, finalize, verify_round
from db_conn import check_channel


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
        # [draft position, is second part of wheel pick]
        self.prev_position = [0, False]
        self.drafted = False
        self.draft_deadline = None
        self.num_finalized = 0

    @commands.command()
    @commands.has_role('Draft Host')
    @check_channel('draft-mons')
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
                username = user.display_name
                output += str(order) + '. ' + username + '\n'
            # display the order of the draft and change the status to active
            await ctx.send('```yaml\n' + '[Draft Order]\n' + output + '```')
            self.draft_round += 1

    @commands.command()
    @commands.has_role('Draft League')
    @check_channel('coaches')
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
                username = user.display_name
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
        timezone = pytz.timezone('US/Eastern')
        converted_time = self.draft_deadline.astimezone(
            timezone).strftime('%Y-%m-%d %H:%M')
        did = self.draft_queue[self.draft_position][0]
        await ctx.send(f':alarm_clock: <@{did}>'
                       f' is now on the clock (draft by'
                       f' {converted_time} EST).')
        # keep track of the draft time
        while current_time < self.draft_deadline:
            if self.drafted is True:
                break
            await asyncio.sleep(2)
            current_time = datetime.datetime.now()
        if self.drafted is False:
            # update skipped_coaches if the previous coach did not draft within the allotted time
            self.skipped_coaches[did][0] += 1
            self.skipped_coaches[did][1].put(self.draft_round)
            await ctx.send(f':arrows_clockwise: <@{did}> is skipped.')
        if self.draft_position == self.prev_position[0]:
            self.prev_position[0] = self.draft_position
            self.prev_position[1] = True
        else:
            self.prev_position[0] = self.draft_position
            self.prev_position[1] = False
        await self.get_next()
        # keep advancing the draft position until reaching a non-finalized coach
        while self.draft_queue[self.draft_position][2] is True and self.num_finalized < \
                len(self.draft_queue):
            await self.get_next()

    @commands.command()
    @commands.has_role('Draft Host')
    @check_channel('draft-mons')
    async def begin(self, ctx):
        """Initiate the draft process and manage the timer until all coaches have finalized."""
        if self.draft_round != 0:
            await ctx.send(':x: You cannot use this command at the current stage.')
            return
        self.draft_round += 1
        await ctx.send(':scroll: The draft has started.')
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
        """Helper function for commands involving selection."""
        if skipped is False:
            # handle normal drafting
            status, pname, remaining_points = pick_pokemon(pokemon, self.draft_round, ctx.author.id,
                                                           self.draft_queue[position][1])
        else:
            # handle skipped coach drafting
            status, pname, remaining_points = pick_pokemon(pokemon, round_skipped, ctx.author.id,
                                                           self.draft_queue[position][1])
        if status == 0:
            self.draft_queue[position][1] = remaining_points
            await ctx.send(f':white_check_mark: {pname} has been added to your draft; you have'
                           f' {remaining_points} points left.')
            if skipped is False:
                # end the timer if the selection is not from a skipped coach
                self.drafted = True
        elif status == 1:
            await ctx.send(f':x: {pname} is not a valid pokemon; you must enter the exact name'
                           ' stated in the Google Sheets.')
        elif status == 2:
            await ctx.send(f':x: {pname} is already taken.')
        else:
            await ctx.send(f':x: You do not have enough points to draft {pname}.')

    @commands.command()
    @commands.has_role('Draft League')
    @check_channel('draft-mons')
    async def select(self, ctx, pokemon):
        """Add the specified pokemon to the coach's party."""
        coach_info = self.skipped_coaches.get(ctx.author.id)
        if self.draft_round < 1:
            await ctx.send(':x: You cannot use this command at the current stage.')
        # check if user issuing command is the coach in the current iteration of draft_position
        elif ctx.author.id != self.draft_queue[self.draft_position][0]:
            if coach_info is None:
                await ctx.send(':x: You are not a valid coach.')
            else:
                # handle skipped coaches drafting
                if coach_info[1].qsize() > 0:
                    await self.acquire(ctx, pokemon, True, coach_info[2],
                                       coach_info[1].get())
                else:
                    await ctx.send(':x: It is not your turn to draft yet.')
        else:
            if not coach_info[1].empty():
                # fulfill previously skipped picks first if coach is in current draft_position
                await self.acquire(ctx, pokemon, True, self.draft_position, coach_info[1].get())
            else:
                await self.acquire(ctx, pokemon, False, self.draft_position)

    @commands.command()
    @commands.has_role('Draft League')
    @check_channel('coaches')
    async def preselect(self, ctx):
        """Enable coaches to save picks for automatic selection in DMs."""
        # TODO: not an essential functionality (implement later)

    async def delete(self, ctx, pokemon, position):
        """Helper function for commands involving removal."""
        coach_info = self.draft_queue[position]
        status, pname, remaining_points = remove_pokemon(pokemon, coach_info[0], coach_info[1])
        if status == 0:
            # update the coach's budget
            coach_info[1] = remaining_points
            await ctx.send(f':white_check_mark: {pname} has been removed from your draft; you have'
                           f' {remaining_points} points left.')
            return 0
        elif status == 1:
            await ctx.send(f':x: {pname} is not a valid pokemon; you must enter the exact name'
                           ' stated in the Google Sheets.')
            return 1
        else:
            await ctx.send(f':x: {pname} is not currently in your draft.')
            return 2

    @commands.command()
    @commands.has_role('Draft League')
    @check_channel('draft-mons')
    async def edit(self, ctx, prev_pokemon, new_pokemon):
        """Change the pick(s) that a coach made before the next coach picks."""
        editable_rounds = []
        coach_info = self.skipped_coaches.get(ctx.author.id)
        if coach_info is None or self.draft_queue[coach_info[2]][2] is True:
            await ctx.send(':x: You are not a valid coach or already finalized.')
        else:
            # check if the position the coach is at is editable
            if coach_info[2] == self.prev_position[0]:
                if self.prev_position[0] == self.draft_position:
                    # editable pick is the first wheel pick if previous and current positions match
                    editable_rounds.append(self.draft_round - 1)
                elif self.prev_position[1] is True:
                    # editable pick is the second wheel pick if wheel poolean for previous is true
                    editable_rounds.append(self.draft_round)
                    editable_rounds.append(self.draft_round - 1)
                else:
                    # editable pick is not a wheel pick
                    editable_rounds.append(self.draft_round)
        # verify the prev_pokemon was drafted in a round that is currently eligible for replacement
        verify_status, round_num = verify_round(prev_pokemon, editable_rounds)
        if verify_status == 0:
            delete_status = await self.delete(ctx, prev_pokemon, coach_info[2])
            if delete_status == 0:
                await self.acquire(ctx, new_pokemon, True, coach_info[2], round_num)
        elif verify_status == 1:
            await ctx.send(f':x: {prev_pokemon} is an invalid pokemon name.')
        elif verify_status == 2:
            await ctx.send(f':x: {prev_pokemon} is an undrafted pokemon.')
        else:
            await ctx.send(f':x: {prev_pokemon} is ineligible for replacement at this time.')

    @commands.command()
    @commands.has_role('Draft Host')
    @check_channel('draft-mons')
    async def etime(self, ctx, minutes: int):
        """Modify the amount of time for the currently drafting coach."""
        if self.draft_round < 1:
            await ctx.send(':x: You cannot use this command at the current stage.')
        else:
            if minutes < 0:
                minutes *= -1
                self.draft_deadline -= datetime.timedelta(minutes=minutes)
            else:
                self.draft_deadline += datetime.timedelta(minutes=minutes)
            timezone = pytz.timezone('US/Eastern')
            converted_time = self.draft_deadline.astimezone(timezone). \
                strftime('%Y-%m-%d %H:%M')
            await ctx.send(f':exclamation: Update: <@{self.draft_queue[self.draft_position][0]}>'
                           f' must make a pick by {converted_time} EST.')

    @commands.command()
    @commands.has_any_role('Draft League', 'Draft Host')
    @check_channel('draft-mons')
    async def finish(self, ctx, user: discord.Member = None):
        """Specify that a coach completed the drafting phase."""
        # TODO: add force finish logic
        coach_info = self.skipped_coaches.get(ctx.author.id)
        if coach_info is not None and self.draft_queue[coach_info[2]][2] is False:
            finalize(ctx.author.id, self.draft_queue[self.draft_position][1])
            # set the coach's finalized status in draft_queue as true
            self.draft_queue[coach_info[2]][2] = True
            user = await self.bot.fetch_user(ctx.author.id)
            username = user.display_name
            await ctx.send(f':white_check_mark: {username} has finished drafting.')
            self.num_finalized += 1
            if coach_info[2] == self.draft_position:
                # stop draft timer if user is the coach in the current draft_position
                self.drafted = True
        else:
            await ctx.send(':x: You are not a valid coach or already finalized.')

    @commands.command()
    @commands.has_role('Draft Host')
    @check_channel('draft-mons')
    async def reenter(self, ctx, user: discord.Member):
        """Re-enter a finalized coach into the draft."""
        # make sure update database too

    @commands.command()
    @commands.has_role('Draft Host')
    @check_channel('draft-mons')
    async def fadd(self, ctx, pokemon):
        """Force add the specified pokemon to the coach's party during draft."""
        # TODO: see comment above
        # recommend do remove before add to make sure budget not exceeded

    @commands.command()
    @commands.has_role('Draft Host')
    @check_channel('draft-mons')
    async def fremove(self, ctx, pokemon):
        """Force remove the specified pokemon from the coach's party during draft."""
        # TODO: see comment above

    @commands.command()
    @commands.has_role('Draft Host')
    @check_channel('draft-mons')
    async def eskipped(self, ctx, user: discord.Member, amount: int):
        """Modify the number of times a coach has been skipped for timer calculation purposes."""
        coach_info = self.skipped_coaches.get(user.id)
        if amount < 0 and coach_info is not None:
            self.skipped_coaches[user.id][0] -= amount
            await ctx.send(f'white_check_mark: The recorded number of times skipped for'
                           f' {user.display_name} has been reduced to'
                           f' {self.skipped_coaches[user.id][0]} times.')
        elif amount >= 0 and coach_info is not None:
            self.skipped_coaches[user.id][0] += amount
            await ctx.send(f'white_check_mark: The recorded number of times skipped for'
                           f' {user.display_name} has been increased to'
                           f' {self.skipped_coaches[user.id][0]} times.')
        else:
            await ctx.send('x: Please specify a valid coach.')

    @commands.command()
    @commands.has_role('Draft League')
    @check_channel('draft-mons')
    async def add(self, ctx, *pokemon):
        """Add the specified pokemon(s) to the coach's party during FA."""
        # TODO: see comment above (ONLY available after drafting finished)
        # recommend do remove before add to make sure budget not exceeded

    @commands.command()
    @commands.has_role('Draft League')
    @check_channel('draft-mons')
    async def remove(self, ctx, *pokemon):
        """Remove the specified pokemon(s) from the coach's party during FA."""
        # TODO: see comment above (ONLY available after drafting finished)

    @commands.command()
    @commands.has_role('Draft League')
    @check_channel('draft-mons')
    async def trade(self, ctx, user: discord.Member, pokemon1, pokemon2):
        """Complete a trade with another coach."""
        # TODO: see comment above (ONLY available after drafting finished)
        # recommend do remove before add to make sure budget not exceeded, detect reaction for confirmation?

    @commands.command()
    @commands.has_role('Draft Host')
    @check_channel('draft-mons')
    async def resume(self, ctx):
        """Resume the bot processes after updates."""
        # TODO think about what arguments and separate for draft or take extra argument?

    @randomize.error
    @begin.error
    @select.error
    @reenter.error
    @etime.error
    @eskipped.error
    @trade.error
    async def error_handler(self, ctx, error):
        """Respond to discord.py errors."""
        if isinstance(error, commands.MissingRole):
            await ctx.send(':x: You do not have permission to use this command.')
        elif isinstance(error, commands.errors.MemberNotFound):
            await ctx.send(':x: Please specify valid server member(s).')
        elif isinstance(error, TypeError):
            await ctx.send('Please enter an integer for the last argument.')
