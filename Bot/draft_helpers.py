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


def valid_pokemon(pokemon):
    """Check if the specified pokemon is a valid pokemon."""
    # convert the pokemon name into the format stored in the database
    words = pokemon.split('!')
    pname = ' '.join(words)
    conn = get_db()
    cur = conn.execute(
        """
        SELECT coachid, cost, pname
        FROM pokemon
        WHERE pname = ?
        """,
        (pname, )
    )
    pokemon_info = cur.fetchone()
    conn.close()
    return pokemon_info


def pick_pokemon(pokemon, draft_round, userid, coach_budget):
    """Associate the specified pokemon with the coach who drafted it."""
    pokemon_info = valid_pokemon(pokemon)
    conn = get_db()
    # check if the specified name is a valid pokemon
    if pokemon_info is None:
        conn.close()
        return 1, pokemon_info[2], None
    # check if the specified pokemon is not already drafted
    if pokemon_info[0] is not None:
        conn.close()
        return 2, pokemon_info[2], None
    # check if the coach has enough points to draft the specified pokemon
    if coach_budget < pokemon_info[1]:
        conn.close()
        return 3, pokemon_info[2], None
    # associate the specified pokemon with the coach who drafted it
    conn.execute(
        """
        UPDATE pokemon
        SET coachid = ?,
            round = ?
        WHERE pname = ?
        """,
        (userid, draft_round, pokemon_info[2])
    )
    conn.commit()
    conn.close()
    return 0, pokemon_info[2], coach_budget - pokemon_info[1]


def remove_pokemon(pokemon, userid, coach_budget):
    """Delete the specified pokemon from the coach's team."""
    # NEED TO RETURN ROUND TOO
    pokemon_info = valid_pokemon(pokemon)
    conn = get_db()
    # check if the specified name is a valid pokemon
    if pokemon_info is None:
        conn.close()
        return 1, pokemon_info[2], None
    # check if the specified pokemon belongs to the user issuing the command
    if pokemon_info[0] != userid:
        conn.close()
        return 2, pokemon_info[2], None
    # dissociate the pokemon from the coach who drafted it
    conn.execute(
        """
        UPDATE pokemon
        SET coachid = NULL,
            round = NULL
        WHERE pname = ?
        """,
        (pokemon_info[2], )
    )
    conn.commit()
    conn.close()
    return 0, pokemon_info[2], coach_budget + pokemon_info[1]


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


def verify_round(pokemon, rounds):
    """Check if the specified pokemon was drafted in the specified round(s)."""
    words = pokemon.split('!')
    pname = ' '.join(words)
    conn = get_db()
    cur = conn.execute(
        """
        SELECT round
        FROM pokemon
        WHERE pname = ?
        """,
        (pname, )
    )
    pokemon_round = cur.fetchone()
    conn.close()
    if pokemon_round is None:
        # invalid pokemon name
        return 1, None
    if pokemon_round[0] is None:
        # undrafted pokemon
        return 2, None
    if pokemon_round in rounds:
        return 0, pokemon_round[0]
    # pokemon ineligible for editing
    return 3, pokemon_round[0]


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
