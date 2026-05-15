# AI Assistance Log

**CS 665 – Database Systems | Project 3**  
**Policy:** All AI assistance must be disclosed per course requirements.

---

## Entry 1

| Field | Details |
|---|---|
| **Date** | 2026-05-15 |
| **Tool** | GitHub Copilot (Claude Sonnet 4.6 model, VS Code extension) |
| **Context** | Initial project scaffolding and full feature implementation |

### Prompt Provided to AI

> I'm working on Project 3 for CS 665 (Database Systems) at WSU. It's a full-stack Python web app
> built on a database schema I designed in Project 2.
> Tech stack: Python 3.9, Flask 3.0.3, Flask-SQLAlchemy 3.1.1, SQLite (app.db), Jinja2 templates,
> HTML/CSS. Using an app factory pattern with a Blueprint.
> [Full schema description: publishers, games, players, player_games, play_sessions with
> relationships and cascade deletes.]
> Project 3 requirements I still need to implement: Multi-table CRUD, Relationship display,
> Transaction logic, Server-side validation, Summary dashboard, Seed data, NORMALIZATION.md,
> AI_LOG.md, README.md, Git.
> Current status: Models and basic index route are working. App runs at localhost:5000 and shows
> empty games/players lists. Need to build everything else.

### AI Output Summary

GitHub Copilot:

1. **Rewrote `app/routes.py`** — complete Blueprint with:
   - Dashboard route using `func.count`, `func.avg`, `func.sum`, top-5 query with `GROUP BY`
   - Full CRUD for Games: `game_new`, `game_edit`, `game_delete`
   - Full CRUD for Players: `player_new`, `player_edit`, `player_delete`, `player_detail`
   - `log_session` route with atomic transaction (insert + recalculate `total_play_hours`)
   - `/seed` route populating 3 publishers, 4 games, 3 players, 5 `player_games`, 3 sessions
   - `_valid_email()` helper using `re.match` for server-side email validation

2. **Updated `app/templates/base.html`** — added full navbar with links to Dashboard, Games,
   Players, Seed DB; added Bootstrap flash message block using `get_flashed_messages`.

3. **Rewrote `app/templates/index.html`** — dashboard with stat cards for total games, total
   players, avg rating, total hours; top-played games table; quick-links card.

4. **Created `app/templates/games/index.html`** — sortable table with Edit/Delete per row.

5. **Created `app/templates/games/form.html`** — shared create/edit form with publisher dropdown,
   date + price inputs.

6. **Created `app/templates/players/index.html`** — table with game-count badge per player.

7. **Created `app/templates/players/detail.html`** — library table with rating badge, hours, and
   session count; totals footer row using Jinja2 namespace trick.

8. **Created `app/templates/players/form.html`** — create/edit form for player registration.

9. **Created `app/templates/players/log_session.html`** — session logging form with game
   selector, date, and duration.

10. Ran smoke tests via Flask test client confirming all routes return HTTP 200.

11. Fixed a Jinja2 `TemplateAssertionError: block defined twice` bug (cannot use `{% block %}`
    inside `{% if %}`); moved conditional logic inside a single `{% block title %}`.

### My Modifications and Verification

- **Verified model compatibility:** Confirmed all route logic (foreign keys, relationship
  attribute names, cascade behaviour) matched the `models.py` I had already written.
- **Tested seed data manually:** Navigated to `/seed` in the browser and confirmed all five
  tables populated correctly; ran `/players/1` to verify the seeded library entries appeared.
- **Reviewed validation logic:** Confirmed `_valid_email` regex matches standard email formats;
  confirmed the `rating` range (1–10) is enforced both in the DB `CheckConstraint` (models.py)
  and by the form's `min`/`max` HTML attributes.
- **Reviewed transaction logic:** Traced through the `log_session` route to confirm
  `db.session.flush()` is called before the `SUM` aggregate so the new session row is included
  in the recalculation within the same transaction.
- **Confirmed idempotent seed:** Verified the `if Publisher.query.first()` guard prevents
  duplicate seeding on subsequent visits.
- **Template audit:** Reviewed all eight Jinja2 templates for correctness; confirmed `vals.get()`
  calls use the correct form field names; confirmed delete confirm dialogs name the correct item.

---

## Entry 2

| Field | Details |
|---|---|
| **Date** | 2026-05-15 |
| **Tool** | GitHub Copilot (Claude Sonnet 4.6 model, VS Code extension) |
| **Context** | Documentation deliverables |

### Prompt Provided to AI

> [Pasted the full Project 3 requirements PDF.]  
> Help me complete the remaining deliverables: README.md, NORMALIZATION.md, AI_LOG.md,
> schema.sql, and .gitignore.

### AI Output Summary

GitHub Copilot generated:

1. **`README.md`** — professional documentation including project description, tech stack table,
   project structure tree, step-by-step installation, database setup section, usage table of
   URLs, and a features section explaining each requirement (CRUD, relationships, transactions,
   validation, dashboard).

2. **`NORMALIZATION.md`** — full 3NF audit covering: original flat schema, all 7 functional
   dependencies in tabular form, update/insertion/deletion anomaly examples for the original
   design, step-by-step decomposition from flat → 1NF → 2NF → 3NF with justification for the
   `total_play_hours` cache, and the final relational schema with relationship table.

3. **`schema.sql`** — DDL `CREATE TABLE` statements matching the SQLAlchemy models exactly,
   with `CHECK` constraint on `rating`, `UNIQUE` on `email`, and all foreign keys.

4. **`AI_LOG.md`** (this file) — structured disclosure of both AI assistance sessions.

5. Verified `.gitignore` already covered `venv/`, `__pycache__/`, `instance/`, `.env`.

### My Modifications and Verification

- **Cross-checked NORMALIZATION.md** against my actual `models.py` to confirm all column names,
  data types, and relationships were accurately described.
- **Cross-checked schema.sql** — made sure the DDL matched the SQLAlchemy model definitions
  (e.g., `NUMERIC(6,2)` for price and hours, `CHECK(rating >= 1 AND rating <= 10)`).
- **README reviewed for accuracy** — all URLs, file paths, and feature descriptions match the
  actual running application.
- **Added personal context** to this AI log (the exact prompts I used, my verification steps).
