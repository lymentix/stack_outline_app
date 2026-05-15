# Video Game Library Tracker

**CS 665 – Database Systems | Project 3**

A full-stack Python web application that lets users manage a personal video-game library. Users can
browse games and publishers, track which games they own, rate them, log play sessions, and view
a live summary dashboard powered by SQL aggregate queries.

---

## Table of Contents

1. [Project Description](#project-description)
2. [Tech Stack](#tech-stack)
3. [Project Structure](#project-structure)
4. [Installation](#installation)
5. [Database Setup](#database-setup)
6. [Usage](#usage)
7. [Features](#features)
8. [Normalization](#normalization)

---

## Project Description

The Video Game Library Tracker stores and manages:

- **Publishers** – game studios with country and founding information  
- **Games** – titles with genre, release date, price, and publisher  
- **Players** – registered users with unique email addresses  
- **Player Library** – a junction table recording which player owns which game, their 1–10 rating,
  purchase date, and accumulated play hours  
- **Play Sessions** – individual session records (date + duration in minutes)

The app targets gamers who want a personal catalogue and play-time log, or a database instructor
looking for a worked example of 3NF, transactions, and aggregate dashboards.

---

## Tech Stack

| Layer | Technology |
|---|---|
| Language | Python 3.9 |
| Backend framework | Flask 3.0.3 |
| ORM | Flask-SQLAlchemy 3.1.1 |
| Database | SQLite (`instance/app.db`) |
| Templates | Jinja2 (via Flask) |
| Frontend CSS | Bootstrap 5.3 (CDN) |
| Version control | Git |

---

## Project Structure

```
stack_outline_app/
├── app/
│   ├── __init__.py          # App factory – registers blueprint, runs db.create_all()
│   ├── extensions.py        # SQLAlchemy instance
│   ├── models.py            # ORM models (Publisher, Game, Player, PlayerGame, PlaySession)
│   ├── routes.py            # Blueprint "main" – all routes
│   ├── static/css/styles.css
│   └── templates/
│       ├── base.html
│       ├── index.html       # Dashboard
│       ├── games/
│       │   ├── index.html
│       │   └── form.html
│       └── players/
│           ├── index.html
│           ├── detail.html
│           ├── form.html
│           └── log_session.html
├── config.py
├── requirements.txt
├── run.py
├── schema.sql               # Final 3NF SQL schema for reference
├── NORMALIZATION.md
└── AI_LOG.md
```

---

## Installation

### Prerequisites

- Python 3.9+
- Git

### Steps

```bash
# 1. Clone the repository
git clone <your-repo-url>
cd stack_outline_app

# 2. Create and activate a virtual environment
python -m venv venv

# Windows
venv\Scripts\activate

# macOS / Linux
source venv/bin/activate

# 3. Install dependencies
pip install -r requirements.txt
```

> No `.env` file is required for local development. The app uses sensible defaults
> (`SECRET_KEY=dev-secret-key`, `DATABASE_URL=sqlite:///app.db`).  
> For production, create a `.env` file or set environment variables accordingly.

---

## Database Setup

SQLite tables are **created automatically** on first run via `db.create_all()` in the app factory.
No manual SQL script execution is needed for development.

### Optional: review the schema

The file `schema.sql` contains the complete DDL for all five tables for reference or if you want
to inspect or recreate the schema in another SQL tool:

```bash
# inspect with SQLite CLI (optional)
sqlite3 instance/app.db < schema.sql
```

### Load sample data

After starting the server, visit **http://127.0.0.1:5000/seed** once to populate the database
with 3 publishers, 4 games, 3 players, 5 game-library entries, and 3 play sessions.
The seed route is idempotent — it does nothing if data already exists.

---

## Usage

```bash
# Start the development server
python run.py
```

Open **http://127.0.0.1:5000** in your browser.

### Navigation

| URL | Description |
|---|---|
| `/` | Summary dashboard (COUNT / SUM / AVG stats + top games) |
| `/seed` | Load sample data (one-time) |
| `/games` | Browse all games |
| `/games/new` | Add a game |
| `/games/<id>/edit` | Edit a game |
| `/players` | Browse all players |
| `/players/new` | Register a player |
| `/players/<id>` | Player detail — full game library with hours & sessions |
| `/players/<id>/edit` | Edit a player |
| `/players/<id>/log-session` | Log a play session (atomic transaction) |

---

## Features

### Multi-Table CRUD
Full Create / Read / Update / Delete for both **Games** (linked to Publishers) and **Players**
(linked to their game library). Cascade deletes ensure referential integrity.

### Relationship Display
The player detail page (`/players/<id>`) renders every `PlayerGame` row for that player, joining
through to the `Game` model — a live One-to-Many display across two related tables.

### Transaction Logic
Logging a play session (`/players/<id>/log-session`) performs two writes inside a single
SQLAlchemy transaction:
1. `INSERT` a new `PlaySession` row.
2. Recalculate and `UPDATE` `player_games.total_play_hours` using a `SUM` aggregate over all
   sessions for that game.

`db.session.flush()` makes the new session visible within the same transaction before the
aggregate runs, so the recalculated value is always accurate.

### Server-Side Validation
All form handlers reject bad input before touching the database:

| Rule | Applies to |
|---|---|
| Empty required fields | All forms |
| Negative price | Add / Edit Game |
| Malformed email (regex) | Add / Edit Player |
| Duplicate email | Add / Edit Player |
| Non-positive duration | Log Session |

### Summary Dashboard
The index view runs four aggregate SQL queries:
- `COUNT(game_id)` – total games catalogued
- `COUNT(player_id)` – total registered players
- `AVG(rating)` – average library rating across all player-game relationships
- `SUM(total_play_hours)` – total hours logged globally
- Top-5 most-played games by total hours (GROUP BY + ORDER BY)

---

## Normalization

See [NORMALIZATION.md](NORMALIZATION.md) for the full 3NF audit including functional
dependencies, anomaly analysis, decomposition steps, and final relational schema.
