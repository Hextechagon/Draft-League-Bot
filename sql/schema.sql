PRAGMA foreign_keys = ON;


--username is for higher readability when checking the table content manually
--for recovery, have to store the number of times skipped and populate based on selection from pokemon table
CREATE TABLE coaches(
    discordid INTEGER PRIMARY KEY,
    username VARCHAR(50) NOT NULL,
    wins INTEGER NOT NULL DEFAULT 0, 
    losses INTEGER NOT NULL DEFAULT 0,
    netkd INTEGER NOT NULL DEFAULT 0,
    finalized BOOLEAN NOT NULL DEFAULT 0,
    dorder INTEGER,
    skipped INTEGER NOT NULL DEFAULT 0,
    transactions INTEGER NOT NULL DEFAULT 3
);

CREATE TABLE pokemon(
    pname VARCHAR(50) PRIMARY KEY, 
    cost INTEGER NOT NULL,
    kills INTEGER NOT NULL DEFAULT 0,
    coachid INTEGER,
    round INTEGER,
    FOREIGN KEY(coachid) REFERENCES coaches(discordid) 
    ON UPDATE CASCADE 
    ON DELETE CASCADE
);

CREATE TABLE matches(
    matchid INTEGER PRIMARY KEY AUTOINCREMENT,
    winner INTEGER,
    loser INTEGER,
    record INTEGER,
    mweek INTEGER NOT NULL,
    replay VARCHAR(100),
    FOREIGN KEY(winner) REFERENCES coaches(discordid) 
    ON UPDATE CASCADE
    ON DELETE CASCADE,
    FOREIGN KEY(loser) REFERENCES coaches(discordid) 
    ON UPDATE CASCADE
    ON DELETE CASCADE
);

CREATE TABLE trades(
    tradeid INTEGER PRIMARY KEY AUTOINCREMENT,
    omon VARCHAR(50),
    dmon VARCHAR(50),
    requester INTEGER,
    requestee INTEGER,
    CHECK (requester != requestee),
    FOREIGN KEY(omon) REFERENCES pokemon(pname)
    ON UPDATE CASCADE
    ON DELETE CASCADE,
    FOREIGN KEY(dmon) REFERENCES pokemon(pname)
    ON UPDATE CASCADE
    ON DELETE CASCADE,
    FOREIGN KEY(requester) REFERENCES coaches(discordid) 
    ON UPDATE CASCADE
    ON DELETE CASCADE,
    FOREIGN KEY(requestee) REFERENCES coaches(discordid)
    ON UPDATE CASCADE
    ON DELETE CASCADE
);