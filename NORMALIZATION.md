# Normalization Report — Video Game Library Tracker

**CS 665 – Database Systems | Project 3**

---

## 1. Original / Starting Schema

Before normalization the conceptual design was a single flat table describing a player's game
library:

```
game_library(
    player_id, username, email, join_date,
    game_id, title, genre, release_date, price,
    publisher_name, publisher_country, publisher_founded,
    rating, purchase_date, total_play_hours,
    session_id, session_date, duration_minutes
)
```

---

## 2. Original Functional Dependencies

Using standard notation A → B to mean "A functionally determines B":

| # | Determinant | Dependent attributes | Notes |
|---|---|---|---|
| FD1 | `player_id` | `username`, `email`, `join_date` | A player's profile is determined by their ID |
| FD2 | `email` | `player_id`, `username`, `join_date` | Email is a candidate key for players |
| FD3 | `game_id` | `title`, `genre`, `release_date`, `price`, `publisher_name`, `publisher_country`, `publisher_founded` | A game's metadata is determined by the game |
| FD4 | `publisher_name` | `publisher_country`, `publisher_founded` | Publisher attributes depend only on the publisher, not the game |
| FD5 | `(player_id, game_id)` | `rating`, `purchase_date`, `total_play_hours` | Library entry is identified by the player–game pair |
| FD6 | `session_id` | `player_id`, `game_id`, `session_date`, `duration_minutes` | A session is identified by its own key |
| FD7 | `(player_id, game_id)` | `total_play_hours` | Total hours is derived from summing all sessions — a transitive dependency |

---

## 3. Anomaly Identification

### 3.1 Update Anomaly

If a publisher changes its country of origin (e.g., after a merger), every row in the flat table
for any game published by that studio must be updated. Missing even one row leaves the database in
an inconsistent state.

**Example:** "Nintendo" moves from Japan to a holding company.  
Every row referencing any Nintendo game needs `publisher_country` changed.

### 3.2 Insertion Anomaly

A publisher cannot be recorded until at least one game exists, because `publisher_name` is only an
attribute of a game row — there is no independent publisher entity.

**Example:** A new studio is signed before its first game releases; it cannot be stored.

### 3.3 Deletion Anomaly

Deleting the last game by a publisher erases all knowledge of that publisher (country, founding
date, etc.) because publisher data lives solely inside the game rows.

**Example:** Removing the only game by "CD Projekt Red" from the library permanently loses the
publisher record.

### 3.4 Redundancy

Publisher metadata (`publisher_name`, `publisher_country`, `publisher_founded`) is repeated on
every row for every game by that publisher — once per player who owns the game.

---

## 4. Decomposition Steps

### Step 1 — Achieve 1NF

The flat table already has atomic columns, a primary key, and no repeating groups.  
✅ Already in 1NF.

### Step 2 — Achieve 2NF (eliminate partial dependencies)

The composite key `(player_id, game_id)` is the primary key of the flat table.  
Attributes `title`, `genre`, `release_date`, `price`, `publisher_*` depend only on `game_id` —
a **partial dependency** on the composite key.  
Attributes `username`, `email`, `join_date` depend only on `player_id` — also a partial
dependency.

**Decomposition:**

```
players(player_id PK, username, email, join_date)
games(game_id PK, title, genre, release_date, price, publisher_name,
      publisher_country, publisher_founded)
player_games(player_game_id PK, player_id FK, game_id FK,
             rating, purchase_date, total_play_hours)
play_sessions(session_id PK, player_game_id FK, session_date, duration_minutes)
```

✅ Now in 2NF. No non-key attribute is partially dependent on a composite key.

### Step 3 — Achieve 3NF (eliminate transitive dependencies)

Two transitive dependencies remain after 2NF:

**3a. FD4 — publisher details transitively depend on `game_id` via `publisher_name`:**

```
game_id → publisher_name → publisher_country, publisher_founded
```

`publisher_country` and `publisher_founded` do not describe the *game*; they describe the
publisher. This is a transitive dependency through a non-key attribute.

**Fix:** Extract `Publisher` into its own table and replace the denormalized publisher columns in
`games` with a foreign key:

```
publishers(publisher_id PK, name, country, founded_date)
games(game_id PK, title, genre, release_date, price, publisher_id FK)
```

**3b. FD7 — `total_play_hours` is transitively derived:**

`total_play_hours` in `player_games` is mathematically derived from `SUM(duration_minutes)` over
all `play_sessions` for that `(player_id, game_id)` pair. Storing a derived value is technically
a redundancy. However, it is retained as a **denormalized cache** for performance — it is
maintained atomically with every session insert (the transaction logic in `routes.py`
recalculates it immediately). This is a deliberate, documented design trade-off.

✅ Now in 3NF. No non-key attribute transitively depends on the primary key through another
non-key attribute (except the documented cache described above).

---

## 5. Final Relational Schema (3NF)

```
publishers
──────────────────────────────────────────────────────────────────
publisher_id   INTEGER  PRIMARY KEY AUTOINCREMENT
name           TEXT     NOT NULL
country        TEXT
founded_date   DATE
created_at     DATETIME DEFAULT CURRENT_TIMESTAMP


games
──────────────────────────────────────────────────────────────────
game_id        INTEGER  PRIMARY KEY AUTOINCREMENT
title          TEXT     NOT NULL
genre          TEXT
release_date   DATE     NOT NULL
price          NUMERIC(6,2)
publisher_id   INTEGER  REFERENCES publishers(publisher_id)
created_at     DATETIME DEFAULT CURRENT_TIMESTAMP


players
──────────────────────────────────────────────────────────────────
player_id      INTEGER  PRIMARY KEY AUTOINCREMENT
username       TEXT     NOT NULL
email          TEXT     NOT NULL UNIQUE
join_date      DATE     NOT NULL
created_at     DATETIME DEFAULT CURRENT_TIMESTAMP


player_games      ← junction table (M:N between players and games)
──────────────────────────────────────────────────────────────────
player_game_id    INTEGER  PRIMARY KEY AUTOINCREMENT
player_id         INTEGER  NOT NULL REFERENCES players(player_id)
game_id           INTEGER  NOT NULL REFERENCES games(game_id)
rating            INTEGER  CHECK(rating >= 1 AND rating <= 10)
purchase_date     DATE     NOT NULL
total_play_hours  NUMERIC(6,2) DEFAULT 0.00   ← maintained cache
created_at        DATETIME DEFAULT CURRENT_TIMESTAMP


play_sessions
──────────────────────────────────────────────────────────────────
session_id        INTEGER  PRIMARY KEY AUTOINCREMENT
player_game_id    INTEGER  NOT NULL REFERENCES player_games(player_game_id)
session_date      DATE     NOT NULL
duration_minutes  INTEGER  NOT NULL
created_at        DATETIME DEFAULT CURRENT_TIMESTAMP
```

### Relationships

| Relationship | Type | FK |
|---|---|---|
| publishers → games | One-to-Many | `games.publisher_id` |
| players → player_games | One-to-Many | `player_games.player_id` |
| games → player_games | One-to-Many | `player_games.game_id` |
| player_games → play_sessions | One-to-Many | `play_sessions.player_game_id` |

All tables satisfy:
- **1NF** — atomic values, single-valued columns, defined primary key.
- **2NF** — all non-key attributes are fully functionally dependent on the whole primary key.
- **3NF** — no non-key attribute transitively depends on the primary key through another non-key
  attribute (except the documented `total_play_hours` cache).
