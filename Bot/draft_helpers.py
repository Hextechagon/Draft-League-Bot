"""Helper functions for all draft-related functionalities."""
from db_conn import get_db


def randomize_order():
    """Return a list of all coaches in random order."""
    conn = get_db()
    cur = conn.execute(
        """
        SELECT discordid 
        FROM coaches
        ORDER BY RANDOM()
        """
    )
    draft_order = cur.fetchall()
    # check if the draft league capacity requirment is fullfilled (CHANGE TO 16)
    num_coaches = len(draft_order)
    if num_coaches < 3:
        conn.close()
        return num_coaches
    # save the order in coaches table for recovery purposes
    for order, coach in enumerate(draft_order, 1):
        conn.execute(
            """     
            UPDATE coaches
            SET dorder = ?
            WHERE discordid = ?
            """,
            (order, coach[0])
        )
    conn.commit()
    conn.close()
    return draft_order


def get_order():
    """Return the draft order."""
    conn = get_db()
    cur = conn.execute(
        """
        SELECT dorder, discordid
        FROM coaches
        ORDER BY dorder
        """
    )
    draft_order = cur.fetchall()
    conn.close()
    return draft_order


def verify_pokemon(pokemon, rounds):
    """Check if the specified pokemon is a valid pokemon and is draftble in the current round."""
    # convert the pokemon name into the format stored in the database
    words = pokemon.split('!')
    pname = ' '.join(words)
    conn = get_db()
    cur = conn.execute(
        """
        SELECT coachid, cost, round
        FROM pokemon
        WHERE pname = ?
        """,
        (pname, )
    )
    pokemon_info = cur.fetchone()
    conn.close()
    if pokemon_info is None:
        # invalid pokemon name
        return 1, pokemon_info, pname
    if pokemon_info[2] is None:
        # undrafted pokemon
        return 2, pokemon_info, pname
    if pokemon_info[2] in rounds:
        return 0, pokemon_info, pname
    # pokemon ineligible for editing
    return 3, pokemon_info, pname


def pick_pokemon(pokemon, draft_round, userid, coach_budget):
    """Associate the specified pokemon with the coach who drafted it."""
    formatted_names = []
    for mon in pokemon:
        _, pokemon_info, formatted_name = verify_pokemon(mon, [])
        conn = get_db()
        # check if the specified name is a valid pokemon
        if pokemon_info is None:
            conn.close()
            return 1, formatted_name, None
        # check if the specified pokemon is not already drafted
        if pokemon_info[0] is not None:
            conn.close()
            return 2, formatted_name, None
        # check if the coach has enough points to draft the specified pokemon
        if coach_budget < pokemon_info[1]:
            conn.close()
            return 3, formatted_name, None
        # associate the specified pokemon with the coach who drafted it
        conn.execute(
            """
            UPDATE pokemon
            SET coachid = ?,
                round = ?
            WHERE pname = ?
            """,
            (userid, draft_round, formatted_name)
        )
        coach_budget -= pokemon_info[1]
        formatted_names.append(formatted_name)
    conn.commit()
    conn.close()
    # return 0, remaining budget, and a list with formatted names
    return 0, formatted_names, coach_budget


def remove_pokemon(pokemon, userid, coach_budget):
    """Delete the specified pokemon from the coach's team."""
    # MAYBE HAVE TO RETURN ROUND HERE
    formatted_names = []
    for mon in pokemon:
        _, pokemon_info, formatted_name = verify_pokemon(mon, [])
        conn = get_db()
        # check if the specified name is a valid pokemon
        if pokemon_info is None:
            conn.close()
            return 1, formatted_name, None
        # check if the specified pokemon belongs to the user issuing the command
        if pokemon_info[0] != userid:
            conn.close()
            return 2, formatted_name, None
        # dissociate the pokemon from the coach who drafted it
        conn.execute(
            """
            UPDATE pokemon
            SET coachid = NULL,
                round = NULL
            WHERE pname = ?
            """,
            (formatted_name, )
        )
        coach_budget += pokemon_info[1]
        formatted_names.append(formatted_name)
    conn.commit()
    conn.close()
    return 0, formatted_names, coach_budget


def edit_pokemon(old_pokemon, new_pokemon, editable_rounds):
    """Replace a drafted pokemon with another undrafted one."""
    """
    verify_status, pokemon_info, _ = verify_pokemon(prev_pokemon, editable_rounds)
    if verify_status == 0:
        delete_status = await self.delete(ctx, [prev_pokemon], coach_info[2])
        if delete_status == 0:
            await self.acquire(ctx, [new_pokemon], True, coach_info[2], pokemon_info[2])
    elif verify_status == 1:
        await ctx.send(f':x: {prev_pokemon} is an invalid pokemon name.')
    elif verify_status == 2:
        await ctx.send(f':x: {prev_pokemon} is an undrafted pokemon.')
    else:
        await ctx.send(f':x: {prev_pokemon} is ineligible for replacement at this time.')
    """


def finalize(userid, status):
    """Mark a coach's status as finalized or unfinalized in the coaches table."""
    conn = get_db()
    # set the coach's status as finalized or unfinalized based on status
    conn.execute(
        """
        UPDATE coaches
        SET finalized = ?
        WHERE discordid = ?
        """,
        (status, userid)
    )
    conn.commit()
    conn.close()


def edit_skipped(userid, amount):
    """Change the value of the number of skips for the specified user."""
    conn = get_db()
    conn.execute(
        """
        UPDATE coaches
        SET skipped = ?
        WHERE discordid = ?
        """,
        (amount, userid)
    )
    conn.commit()
    conn.close()
