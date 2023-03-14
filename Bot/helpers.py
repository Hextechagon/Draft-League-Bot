import sqlite3
import pathlib


def get_db():
    root = pathlib.Path(__file__).resolve().parent.parent
    database_file = root/'var'/'CTLDL_Bot.sqlite3'
    sqlite_db = sqlite3.connect(str(database_file))
    sqlite_db.execute("PRAGMA foreign_keys = ON")
    return sqlite_db

def db_test(userid):
    team = 'Hextechagon'
    conn = get_db()
    test = conn.execute(
        """
        INSERT INTO coaches(userid )
        VALUES (?)
        """,
        (team, )
    )
    conn.commit()
    conn.close()
    print("Inserted!")
    #trigger check in query
    conn.close()
