"""Helper functions for all draft-related functionalities."""
import sqlite3
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
    # save the order in coaches table
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
    return [[row[0], 125, False] for row in draft_order]


def pick_pokemon(pokemon, userid):
    # FIX: budget related things since budget is removed from table
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
        return 1, None
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
        conn.close()
        return 2, None
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
    conn.commit()
    conn.close()
    return 0, coach_budget - pokemon_info[1]
