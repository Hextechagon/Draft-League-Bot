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


async def get_order():
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


def pick_pokemon(pokemon, draft_round, userid, coach_budget):
    """Associate a pokemon with the coach who drafted it."""
    # convert the Pokémon name into the format stored in the database
    words = pokemon.split('!')
    pname = ' '.join(words)
    conn = get_db()
    # break this into functions if FA has similar code!!!
    cur = conn.execute(
        """
        SELECT coachid, cost
        FROM pokemon
        WHERE pname = ?
        """,
        (pname, )
    )
    pokemon_info = cur.fetchone()
    # check if the specified name is a valid Pokémon
    if pokemon_info is None:
        conn.close()
        return 1, pname, None
    # check if the specified Pokémon is not already drafted
    if pokemon_info[0] is not None:
        conn.close()
        return 2, pname, None
    # check if the coach has enough points to draft the specified Pokémon
    if coach_budget < pokemon_info[1]:
        conn.close()
        return 3, pname, None
    # associate the specified Pokémon with the coach who drafted it
    conn.execute(
        """
        UPDATE pokemon
        SET coachid = ?,
            round = ?
        WHERE pname = ?
        """,
        (userid, draft_round, pname)
    )
    conn.commit()
    conn.close()
    return 0, pname, coach_budget - pokemon_info[1]


def finalize(userid, remaining_budget):
    """Mark a coach's status as finalized and update the remaining budget in the coaches table."""
    conn = get_db()
    # set the coach's status as finalized and record the remaining budget
    conn.execute(
        """
        UPDATE coaches
        SET finalized = 1,
            budget = ?
        WHERE discordid = ?
        """,
        (remaining_budget, userid)
    )
    conn.commit()
    conn.close()
