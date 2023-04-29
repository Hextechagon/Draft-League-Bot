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
    if coach is not None:
        return 0
    return 1

def insert_coach(userid, username, tname):
    """Insert the user with userid into the coaches table."""
    conn = get_db()
    try:
        cur = conn.execute(
            """
            SELECT COUNT(*) AS ct
            FROM coaches
            """
        )
        # change number to league capacity
        if cur.fetchone()[0]== 16:
            return 1
        conn.execute(
            """
            INSERT INTO coaches(discordid, username, tname)
            VALUES (?, ?, ?)
            """,
            (userid, username, tname)
        )
        return 0
    except sqlite3.IntegrityError:
        return 2
    finally:
        conn.commit()
        conn.close()

def bulk_insert(coaches):
    """Insert the users with the specified userids into the coaches table."""
    return 0

def delete_coach(userid):
    """Insert the user with userid into the coaches table."""
    conn = get_db()
    if verify_coach(userid) == 0:
        conn.execute(
            """
            DELETE FROM coaches
            WHERE discordid = ?
            """,
            (userid, )
        )
        conn.commit()
        conn.close()
        return 0
    conn.close()
    return 1

def replace_coach(userid1, userid2, username2, tname):
    """Replace an existing coach with a new coach."""
    conn = get_db()
    try:
        if verify_coach(userid1) == 0:
            conn.execute(
                """
                UPDATE coaches
                SET username = ?, 
                    tname = ?,
                    discordid = ?
                WHERE discordid = ?
                """,
                (username2, tname, userid2, userid1)
            )
            return 0
        return 1
    except sqlite3.IntegrityError:
        return 2
    finally:
        conn.commit()
        conn.close()

def get_leaderboard():
    """Display all current coaches."""
    conn = get_db()
    cur = conn.execute(
        """
        SELECT username
        FROM coaches
        ORDER BY wins DESC, netkd DESC
        """
    )
    coaches = cur.fetchall()
    output = ''
    if len(coaches) == 0:
        output = 'There are no registered coaches.'
    else:
        for rank, coach in enumerate(coaches, 1):
            output += str(rank) + '. ' + coach[0] + '\n'
    return output
