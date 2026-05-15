-- Video Game Library Tracker — Final 3NF Schema
-- CS 665 Database Systems | Project 3
-- SQLite DDL

PRAGMA foreign_keys = ON;

-- ── Publishers ────────────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS publishers (
    publisher_id  INTEGER  PRIMARY KEY AUTOINCREMENT,
    name          TEXT     NOT NULL,
    country       TEXT,
    founded_date  DATE,
    created_at    DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- ── Games ─────────────────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS games (
    game_id       INTEGER  PRIMARY KEY AUTOINCREMENT,
    title         TEXT     NOT NULL,
    genre         TEXT,
    release_date  DATE     NOT NULL,
    price         NUMERIC(6, 2),
    publisher_id  INTEGER  REFERENCES publishers(publisher_id)
                           ON DELETE SET NULL,
    created_at    DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- ── Players ───────────────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS players (
    player_id   INTEGER  PRIMARY KEY AUTOINCREMENT,
    username    TEXT     NOT NULL,
    email       TEXT     NOT NULL UNIQUE,
    join_date   DATE     NOT NULL,
    created_at  DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- ── Player–Game Junction (library) ────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS player_games (
    player_game_id    INTEGER  PRIMARY KEY AUTOINCREMENT,
    player_id         INTEGER  NOT NULL
                               REFERENCES players(player_id)
                               ON DELETE CASCADE,
    game_id           INTEGER  NOT NULL
                               REFERENCES games(game_id)
                               ON DELETE CASCADE,
    rating            INTEGER  CHECK(rating >= 1 AND rating <= 10),
    purchase_date     DATE     NOT NULL,
    -- total_play_hours is a maintained cache: recalculated atomically on every
    -- session insert to avoid a transitive dependency anomaly during reads.
    total_play_hours  NUMERIC(6, 2) DEFAULT 0.00,
    created_at        DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- ── Play Sessions ─────────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS play_sessions (
    session_id        INTEGER  PRIMARY KEY AUTOINCREMENT,
    player_game_id    INTEGER  NOT NULL
                               REFERENCES player_games(player_game_id)
                               ON DELETE CASCADE,
    session_date      DATE     NOT NULL,
    duration_minutes  INTEGER  NOT NULL,
    created_at        DATETIME DEFAULT CURRENT_TIMESTAMP
);
