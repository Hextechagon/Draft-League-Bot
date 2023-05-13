PRAGMA foreign_keys = ON;


--keep budget for post-draft changes (fill in after draft finalized)
CREATE TABLE coaches(
    discordid INTEGER PRIMARY KEY,
    username VARCHAR(50) NOT NULL,
    wins INTEGER NOT NULL DEFAULT 0, 
    losses INTEGER NOT NULL DEFAULT 0,
    netkd INTEGER NOT NULL DEFAULT 0,
    finalized BOOLEAN NOT NULL DEFAULT 0,
    budget INTEGER,
    dorder INTEGER,
    transactions INTEGER,
    UNIQUE(discordid)
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