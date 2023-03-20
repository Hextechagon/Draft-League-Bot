PRAGMA foreign_keys = ON;


--Check if user type is correct
--test insert same userid again to see if error, if error return error message
CREATE TABLE coaches(
    coachid INTEGER PRIMARY KEY,
    wins INTEGER NOT NULL DEFAULT 0, 
    losses INTEGER NOT NULL DEFAULT 0,
    netkd INTEGER NOT NULL DEFAULT 0,
    budget INTEGER NOT NULL DEFAULT 125, 
    finalized BOOLEAN NOT NULL DEFAULT 0,
    tname VARCHAR(50) NOT NULL DEFAULT 'TBD'
);

CREATE TABLE pokemon(
    monid INTEGER PRIMARY KEY AUTOINCREMENT,
    pname VARCHAR(50) NOT NULL, 
    cost INTEGER NOT NULL,
    kills INTEGER NOT NULL DEFAULT 0,
    coachid INTEGER,
    UNIQUE(pname),
    FOREIGN KEY(coachid) REFERENCES coaches(coachid) ON DELETE CASCADE
);

CREATE TABLE matches(
    matchid INTEGER PRIMARY KEY AUTOINCREMENT,
    coach1 INTEGER,
    coach2 INTEGER,
    mweek INTEGER NOT NULL,
    CHECK (coach1 != coach2),
    FOREIGN KEY(coach1) REFERENCES coaches(coachid) ON DELETE CASCADE,
    FOREIGN KEY(coach2) REFERENCES coaches(coachid) ON DELETE CASCADE
);