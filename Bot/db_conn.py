"""Establish database connection."""
import sqlite3
import pathlib
from discord.ext import commands


def get_db():
    """Connect to the database and return a connection object."""
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


def check_channel(channel_name):
    """Restrict a command to the specified channel."""
    def predicate(ctx):
        return ctx.channel.name == channel_name
    return commands.check(predicate)
