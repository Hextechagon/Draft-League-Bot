"""Helper functions for all draft-related functionalities."""
import sqlite3
from db_conn import get_db


def randomize_order():
    """Return a list of all coaches in random order."""
    conn = get_db()
    cur = conn.execute(
        """
        SELECT username 
        FROM coaches
        ORDER BY RANDOM()
        """
    )
    draft_order = cur.fetchall()
    conn.close()
    # check if the draft league capacity requirment is fullfilled
    num_coaches = len(draft_order)
    if num_coaches != 16:
        return num_coaches
    return [row[0] for row in draft_order]

def pick_pokemon(userid, pokemon):
    """Associate a pokemon with the coach who drafted it."""
    conn = get_db()
    # break this into functions
    cur1 = conn.execute(
        """
        SELECT COUNT(*), cost
        FROM pokemon
        WHERE pname = ? AND coachid IS NULL
        """,
        (pokemon, )
    )
    pokemon_info = cur1.fetchone()
    if pokemon_info[0] == 0:
        conn.close()
        return 1
    cur2 = conn.execute(
        """
        SELECT budget 
        FROM coaches
        WHERE discordid = ?
        """,
        (userid, )
    )
    coach_budget = cur2.fetchone()[0]
    if coach_budget < pokemon_info[1]:
        return 2
    conn.execute(
        """
        UPDATE pokemon
        SET coachid = ?
        WHERE pname = ?
        """,
        (userid, pokemon)
    )
    conn.execute(
        """
        UPDATE coaches
        SET budget = budget - ?
        WHERE discordid = ?
        """,
        (pokemon_info[1], userid)
    )
    return 0
