"""Establish database connection."""
import sqlite3
import pathlib


def get_db():
    """Connect to the database."""
    root = pathlib.Path(__file__).resolve().parent.parent
    database_file = root/'var'/'CTLDL_Bot.sqlite3'
    sqlite_db = sqlite3.connect(str(database_file))
    sqlite_db.execute("PRAGMA foreign_keys = ON")
    return sqlite_db


def close(db_conn):
    """Close the database connection."""
    db_conn.close()


def comm_close(db_conn):
    """Commit and close the database connection."""
    db_conn.commit()
    db_conn.close()
