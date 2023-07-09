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
    budget INTEGER,
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
    coach1 INTEGER,
    coach2 INTEGER,
    mweek INTEGER NOT NULL,
    CHECK (coach1 != coach2),
    FOREIGN KEY(coach1) REFERENCES coaches(discordid) 
    ON UPDATE CASCADE
    ON DELETE CASCADE,
    FOREIGN KEY(coach2) REFERENCES coaches(discordid) 
    ON UPDATE CASCADE
    ON DELETE CASCADE
);