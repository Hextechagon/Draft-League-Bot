"""Helper functions for all match-related functionalities."""
import sqlite3
from db_conn import get_db


def insert_match(winner, loser, week, margin, replay):
    """Insert the draft battle result into the matches table."""
    conn = get_db()
    try:
        cur = conn.execute(
            """
            SELECT COUNT(*) AS ct
            FROM matches
            WHERE (winner = ? AND loser = ?) OR (loser = ? AND winner = ?)
            """,
            (winner, loser, winner, loser)
        )
        # check if the match has already been entered
        if cur.fetchone()[0] > 0:
            return 1
        conn.execute(
            """
            INSERT INTO matches(winner, loser, record, mweek, replay)
            VALUES (?, ?, ?, ?, ?)
            """,
            (winner, loser, margin, week, replay)
        )
        # update the kill differential and win/loss for each coach
        conn.execute(
            """     
            UPDATE coaches
                SET netkd = netkd + ?,
                    wins = wins + 1
            WHERE discordid = ?
            """,
            (margin, winner)
        )
        conn.execute(
            """     
            UPDATE coaches
                SET netkd = netkd - ?,
                    losses = losses + 1
            WHERE discordid = ?
            """,
            (margin, loser)
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
        SELECT winner, loser, record
        FROM matches
        WHERE matchid = ?
        """,
        (matchid, )
    )
    match_data = cur.fetchone()
    if match_data is None:
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
    margin = match_data[2]
    # set the margin to 3 if the match is a forfeit loss (indicated by -1 record)
    if margin == -1:
        margin = 3
    # revert the kill differential and win/loss for each coach
    conn.execute(
        """     
        UPDATE coaches
            SET netkd = netkd + ?,
                losses = losses - 1
        WHERE discordid = ?
        """,
        (margin, match_data[1])
    )
    conn.execute(
        """     
        UPDATE coaches
            SET netkd = netkd - ?,
                wins = wins - 1
        WHERE discordid = ?
        """,
        (margin, match_data[0])
    )
    conn.commit()
    conn.close()
    return 0


def get_history(week):
    """Return the match history for the specified week."""
    conn = get_db()
    cur = conn.execute(
        """
        SELECT matchid, winner, loser, record, replay
        FROM matches
        WHERE mweek = ?
        """,
        (week, )
    )
    matches = cur.fetchall()
    conn.close()
    return matches
