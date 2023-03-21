import sqlite3
from db_conn import get_db


def insert_coach(userid, username):
    """Insert the user with userid into the coaches table."""
    conn = get_db()
    try:
        cur = conn.execute(
            """
            INSERT INTO coaches(coachid, username)
            VALUES (?, ?)
            """,
            (userid, username)
        )
        return 0
    except sqlite3.IntegrityError:
        return ':x: This user is already a coach.'
    except:
        return ':x: An Error has occured.'
    finally:
        conn.commit()
        conn.close()

def delete_coach(userid):
    """Insert the user with userid into the coaches table."""
    conn = get_db()
    test = conn.execute(
        """
        DELETE FROM coaches
        WHERE coachid = ?
        """,
        (userid, )
    )
    conn.commit()
    conn.close()
    #except sqlite3.IntegrityError:
        #return 'This user is not a valid coach.'
    #except:
        #return 'An Error has occured.'
    #finally:
        #conn.commit()
        #conn.close()
