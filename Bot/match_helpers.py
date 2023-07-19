"""Helper functions for all match-related functionalities."""
import sqlite3
from db_conn import get_db


def insert_match(winner, loser, replay):
    """Insert the draft battle result into the matches table."""
    # TODO: have to check if coach combo has already been entered
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


def remove_match(matchid):
    """Remove the draft battle result with matchid from the matches table."""
    conn = get_db()
    cur = conn.execute(
        """
        SELECT matchid
        FROM matches
        WHERE matchid = ?
        """,
        (matchid, )
    )
    mid = cur.fetchone()
    if mid is None:
        # invalid matchid
        conn.close()
        return 1
    conn.execute(
        """
        DELETE FROM matches
        WHERE matchid = ?
        """,
        (matchid, )
    )
    conn.commit()
    conn.close()
    return 0


def get_history(week):
    """Return the match history for the specified week."""
    conn = get_db()
    cur = conn.execute(
        """
        SELECT winner, loser, record, mweek, replay
        FROM matches
        WHERE mweek = ?
        """,
        (week, )
    )
    matches = cur.fetchall()
    conn.close()
    return matches
