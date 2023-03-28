import sqlite3
from db_conn import get_db


def insert_coach(userid, username):
    """Insert the user with userid into the coaches table."""
    conn = get_db()
    try:
        conn.execute(
            """
            INSERT INTO coaches(coachid, username)
            VALUES (?, ?)
            """,
            (userid, username)
        )
        return 0
    except sqlite3.IntegrityError:
        return 1
    except:
        # ping owner if this occurs
        return 2
    finally:
        conn.commit()
        conn.close()


def delete_coach(userid):
    """Insert the user with userid into the coaches table."""
    conn = get_db()
    try:
        cur = conn.execute(
            """
            SELECT coachid 
            FROM coaches
            WHERE coachid = ?
            """,
            (userid, )
        )
        coach = cur.fetchone()
        if coach is not None:
            conn.execute(
                """
                DELETE FROM coaches
                WHERE coachid = ?
                """,
                (userid, )
            )
            return 0
        else:
            return 1
    except:
        return 2
    finally:
        conn.commit()
        conn.close()

#if modify userid1 inside, does the argument variable value change
def replace_coach(userid1, userid2, username2): 
    """Replace an existing coach (userid1) with a new coach (userid2)."""
    delete_status = delete_coach(userid1)
    if delete_status ==
    insert_status = insert_coach(userid2, username2)
    return delete_status, insert_status