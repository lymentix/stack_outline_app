# AI Assistance Log

**CS 665 – Database Systems | Project 3**
**Policy:** All AI assistance must be disclosed per course requirements.

---

## Entry 1

| Field | Details |
|---|---|
| **Date** | 2026-05-15 |
| **Tool** | GitHub Copilot (Claude Sonnet 4.6 model, VS Code extension) |
| **Context** | Building the main app features |

### Prompt Provided to AI

> I'm working on Project 3 for CS 665 at WSU. It's a full-stack Python web app built on the
> database I designed in Project 2.
>
> Tech stack: Python 3.9, Flask, Flask-SQLAlchemy, SQLite, Jinja2 templates, HTML/CSS.
>
> Database tables: publishers, games, players, player_games, play_sessions. The relationships
> are publishers → games, games → player_games ← players, and player_games → play_sessions.
>
> I still need to build: CRUD for games and players, a player detail page showing their games,
> a play session logger that updates total play hours in one transaction, server-side
> validation, a dashboard with COUNT/SUM/AVG stats, and seed data.
>
> The models and a basic index page are already working. Help me build the rest.

### AI Output Summary

Copilot built out the main app features:

1. **`app/routes.py`** — wrote all the routes:
   - Dashboard with stats (total games, total players, average rating, total hours)
   - Create/edit/delete pages for games
   - Create/edit/delete pages for players
   - Player detail page showing all games they own
   - Play session logger that updates total play hours in the same transaction
   - A `/seed` route that adds sample publishers, games, and players
   - Email validation using regex

2. **HTML templates** — created the pages for:
   - Dashboard (`index.html`) with stat cards and top games table
   - Games list and add/edit form
   - Players list, player detail page, add/edit form, and session logging form
   - Updated the base template with a navbar and flash messages

3. **Fixed a template error** — Jinja2 wouldn't let me put a `{% block %}` inside an `{% if %}`,
   so Copilot rewrote it with the condition inside the block instead.

### My Modifications and Verification

- Made sure all the route code matched the column names and relationships in my `models.py`.
- Tested the seed route in the browser and confirmed all the tables filled with sample data.
- Checked the player detail page to make sure the owned games showed up correctly.
- Confirmed the rating validation (1–10) works on both the form and the database.
- Walked through the session logger to make sure the new session and updated play hours both
  save together as one transaction.
- Reviewed each template to make sure form fields and delete prompts referenced the right items.

---

## Entry 2

| Field | Details |
|---|---|
| **Date** | 2026-05-15 |
| **Tool** | GitHub Copilot (Claude Sonnet 4.6 model, VS Code extension) |
| **Context** | Writing project documentation |

### Prompt Provided to AI

> I attached the Project 3 requirements PDF. Help me write the remaining files: README.md,
> NORMALIZATION.md, AI_LOG.md, schema.sql, and .gitignore.

### AI Output Summary

Copilot generated:

1. **`README.md`** — project description, tech stack, folder structure, install steps, how to
   set up the database, and what each feature does.

2. **`NORMALIZATION.md`** — the 3NF write-up: functional dependencies, anomaly examples for
   a flat schema, the decomposition from 1NF to 2NF to 3NF, and the final schema.

3. **`schema.sql`** — `CREATE TABLE` statements matching the SQLAlchemy models, including the
   rating check constraint, unique email, and foreign keys.

4. **`AI_LOG.md`** — this file.

5. Checked `.gitignore` — already had `venv/`, `__pycache__/`, `instance/`, and `.env`.

### My Modifications and Verification

- Compared `NORMALIZATION.md` against `models.py` to make sure the column names and
  relationships were right.
- Compared `schema.sql` against my models to make sure the data types and constraints matched.
- Read through the README to make sure all the URLs and file paths actually work.
- Added my real prompts to this log instead of generic descriptions.