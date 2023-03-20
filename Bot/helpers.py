import sqlite3
import pathlib


def get_db():
    root = pathlib.Path(__file__).resolve().parent.parent
    database_file = root/'var'/'CTLDL_Bot.sqlite3'
    sqlite_db = sqlite3.connect(str(database_file))
    sqlite_db.execute("PRAGMA foreign_keys = ON")
    return sqlite_db

def db_test(userid):
    try:
        conn = get_db()
        test = conn.execute(
            """
            INSERT INTO coaches(coachid)
            VALUES (?)
            """,
            (userid, )
        )
        conn.commit()
        test2 = conn.execute(
            """
            SELECT pname 
            FROM pokemon
            WHERE monid < 11
            """
        )
        pokemon = test2.fetchall()
        for mon in pokemon:
            print(mon)
        return "Success!"
    except:
        return "Failure!"
    finally:
        conn.close()
    #trigger check in query
