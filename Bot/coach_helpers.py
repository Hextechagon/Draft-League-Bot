"""Helper functions for all coach-related functionalities."""
import sqlite3
from db_conn import get_db


def verify_coach(userid):
    """Check if the specified coach is an existing coach."""
    conn = get_db()
    cur = conn.execute(
        """
        SELECT discordid 
        FROM coaches
        WHERE discordid = ?
        """,
        (userid, )
    )
    coach = cur.fetchone()
    conn.close()
    if coach is not None:
        return 0
    return 1


def insert_coach(userid, username):
    """Insert the user with userid into the coaches table."""
    conn = get_db()
    try:
        cur = conn.execute(
            """
            SELECT COUNT(*) AS ct
            FROM coaches
            """
        )
        # check if the draft league is already full
        if cur.fetchone()[0] == 16:
            return 1
        conn.execute(
            """
            INSERT INTO coaches(discordid, username)
            VALUES (?, ?)
            """,
            (userid, username)
        )
        return 0
    except sqlite3.IntegrityError:
        return 2
    finally:
        conn.commit()
        conn.close()


def replace_coach(userid1, userid2, username2):
    """Replace an existing coach with a new coach."""
    conn = get_db()
    try:
        if verify_coach(userid1) == 0:
            conn.execute(
                """
                UPDATE coaches
                SET username = ?, 
                    discordid = ?
                WHERE discordid = ?
                """,
                (username2, userid2, userid1)
            )
            return 0
        return 1
    except sqlite3.IntegrityError:
        return 2
    finally:
        conn.commit()
        conn.close()


def get_leaderboard():
    """Return all current coaches."""
    conn = get_db()
    cur = conn.execute(
        """
        SELECT discordid, wins, losses, netkd
        FROM coaches
        ORDER BY wins DESC, netkd DESC
        """
    )
    coach_ranking = cur.fetchall()
    conn.close()
    return coach_ranking


def get_info(userid):
    """Return the information of a coach with userid."""
    conn = get_db()
    if verify_coach(userid) == 0:
        cur = conn.execute(
            """
            SELECT round, pname, cost 
            FROM pokemon
            WHERE coachid = ?
            ORDER BY round
            """,
            (userid, )
        )
        draft_data = cur.fetchall()
        cur = conn.execute(
            """
            SELECT skipped, transactions
            FROM coaches
            WHERE coachid = ?
            """,
            (userid, )
        )
        user_data = cur.fetchone()
        conn.close()
        return draft_data, user_data
    return 1, user_data
