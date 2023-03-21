import sqlite3
from db_conn import get_db


def insert_coach(userid):
    """Insert the user with userid into the coaches table."""
    conn = get_db()
    try:
        test = conn.execute(
            """
            INSERT INTO coaches(coachid)
            VALUES (?)
            """,
            (userid, )
        )
        return 0
    except sqlite3.IntegrityError:
        return 'This user is already a coach.'
    except:
        return 'An Error has occured.'
    finally:
        conn.commit()
        conn.close()
