import re
from datetime import date
from decimal import Decimal, InvalidOperation

from flask import Blueprint, abort, flash, redirect, render_template, request, url_for
from sqlalchemy import func

from .extensions import db
from .models import Game, Player, PlayerGame, PlaySession, Publisher

main = Blueprint("main", __name__)


def _valid_email(email: str) -> bool:
    return bool(re.match(r"^[^@\s]+@[^@\s]+\.[^@\s]+$", email))


# ── Dashboard ─────────────────────────────────────────────────────────────────

@main.route("/")
def index():
    total_games = db.session.query(func.count(Game.game_id)).scalar() or 0
    total_players = db.session.query(func.count(Player.player_id)).scalar() or 0
    avg_rating = db.session.query(func.avg(PlayerGame.rating)).scalar()
    total_hours = db.session.query(func.sum(PlayerGame.total_play_hours)).scalar()
    top_games = (
        db.session.query(Game.title, func.sum(PlayerGame.total_play_hours).label("hours"))
        .join(PlayerGame, Game.game_id == PlayerGame.game_id)
        .group_by(Game.game_id)
        .order_by(func.sum(PlayerGame.total_play_hours).desc())
        .limit(5)
        .all()
    )
    return render_template(
        "index.html",
        total_games=total_games,
        total_players=total_players,
        avg_rating=round(float(avg_rating), 2) if avg_rating else "N/A",
        total_hours=float(total_hours) if total_hours else 0.0,
        top_games=top_games,
    )


# ── Games ─────────────────────────────────────────────────────────────────────

@main.route("/games")
def games_index():
    games = Game.query.order_by(Game.title).all()
    return render_template("games/index.html", games=games)


@main.route("/games/new", methods=["GET", "POST"])
def game_new():
    publishers = Publisher.query.order_by(Publisher.name).all()
    if request.method == "POST":
        title = request.form.get("title", "").strip()
        genre = request.form.get("genre", "").strip()
        release_date_str = request.form.get("release_date", "").strip()
        price_str = request.form.get("price", "").strip()
        publisher_id_str = request.form.get("publisher_id", "").strip()

        errors = []
        if not title:
            errors.append("Title is required.")

        release_date = None
        if not release_date_str:
            errors.append("Release date is required.")
        else:
            try:
                release_date = date.fromisoformat(release_date_str)
            except ValueError:
                errors.append("Invalid release date.")

        price = None
        if price_str:
            try:
                price = Decimal(price_str)
                if price < 0:
                    errors.append("Price cannot be negative.")
            except InvalidOperation:
                errors.append("Price must be a valid number.")

        if errors:
            for e in errors:
                flash(e, "danger")
            return render_template("games/form.html", publishers=publishers, game=None, vals=request.form)

        game = Game(
            title=title,
            genre=genre or None,
            release_date=release_date,
            price=price,
            publisher_id=int(publisher_id_str) if publisher_id_str else None,
        )
        db.session.add(game)
        db.session.commit()
        flash(f"'{title}' added.", "success")
        return redirect(url_for("main.games_index"))

    return render_template("games/form.html", publishers=publishers, game=None, vals={})


@main.route("/games/<int:game_id>/edit", methods=["GET", "POST"])
def game_edit(game_id):
    game = db.get_or_404(Game, game_id)
    publishers = Publisher.query.order_by(Publisher.name).all()

    if request.method == "POST":
        title = request.form.get("title", "").strip()
        genre = request.form.get("genre", "").strip()
        release_date_str = request.form.get("release_date", "").strip()
        price_str = request.form.get("price", "").strip()
        publisher_id_str = request.form.get("publisher_id", "").strip()

        errors = []
        if not title:
            errors.append("Title is required.")

        release_date = None
        if not release_date_str:
            errors.append("Release date is required.")
        else:
            try:
                release_date = date.fromisoformat(release_date_str)
            except ValueError:
                errors.append("Invalid release date.")

        price = None
        if price_str:
            try:
                price = Decimal(price_str)
                if price < 0:
                    errors.append("Price cannot be negative.")
            except InvalidOperation:
                errors.append("Price must be a valid number.")

        if errors:
            for e in errors:
                flash(e, "danger")
            return render_template("games/form.html", publishers=publishers, game=game, vals=request.form)

        game.title = title
        game.genre = genre or None
        game.release_date = release_date
        game.price = price
        game.publisher_id = int(publisher_id_str) if publisher_id_str else None
        db.session.commit()
        flash(f"'{title}' updated.", "success")
        return redirect(url_for("main.games_index"))

    vals = {
        "title": game.title,
        "genre": game.genre or "",
        "release_date": game.release_date.isoformat() if game.release_date else "",
        "price": str(game.price) if game.price is not None else "",
        "publisher_id": str(game.publisher_id) if game.publisher_id else "",
    }
    return render_template("games/form.html", publishers=publishers, game=game, vals=vals)


@main.route("/games/<int:game_id>/delete", methods=["POST"])
def game_delete(game_id):
    game = db.get_or_404(Game, game_id)
    title = game.title
    db.session.delete(game)
    db.session.commit()
    flash(f"'{title}' deleted.", "warning")
    return redirect(url_for("main.games_index"))


# ── Players ───────────────────────────────────────────────────────────────────

@main.route("/players")
def players_index():
    players = Player.query.order_by(Player.username).all()
    return render_template("players/index.html", players=players)


@main.route("/players/<int:player_id>")
def player_detail(player_id):
    player = db.get_or_404(Player, player_id)
    return render_template("players/detail.html", player=player)


@main.route("/players/new", methods=["GET", "POST"])
def player_new():
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        email = request.form.get("email", "").strip()
        join_date_str = request.form.get("join_date", "").strip()

        errors = []
        if not username:
            errors.append("Username is required.")
        if not email:
            errors.append("Email is required.")
        elif not _valid_email(email):
            errors.append("Invalid email address.")
        elif Player.query.filter_by(email=email).first():
            errors.append("A player with that email already exists.")

        join_date = date.today()
        if join_date_str:
            try:
                join_date = date.fromisoformat(join_date_str)
            except ValueError:
                errors.append("Invalid join date.")

        if errors:
            for e in errors:
                flash(e, "danger")
            return render_template("players/form.html", player=None, vals=request.form)

        player = Player(username=username, email=email, join_date=join_date)
        db.session.add(player)
        db.session.commit()
        flash(f"Player '{username}' added.", "success")
        return redirect(url_for("main.players_index"))

    return render_template("players/form.html", player=None, vals={})


@main.route("/players/<int:player_id>/edit", methods=["GET", "POST"])
def player_edit(player_id):
    player = db.get_or_404(Player, player_id)

    if request.method == "POST":
        username = request.form.get("username", "").strip()
        email = request.form.get("email", "").strip()
        join_date_str = request.form.get("join_date", "").strip()

        errors = []
        if not username:
            errors.append("Username is required.")
        if not email:
            errors.append("Email is required.")
        elif not _valid_email(email):
            errors.append("Invalid email address.")
        elif Player.query.filter(Player.email == email, Player.player_id != player_id).first():
            errors.append("A player with that email already exists.")

        join_date = player.join_date
        if join_date_str:
            try:
                join_date = date.fromisoformat(join_date_str)
            except ValueError:
                errors.append("Invalid join date.")

        if errors:
            for e in errors:
                flash(e, "danger")
            return render_template("players/form.html", player=player, vals=request.form)

        player.username = username
        player.email = email
        player.join_date = join_date
        db.session.commit()
        flash(f"Player '{username}' updated.", "success")
        return redirect(url_for("main.players_index"))

    vals = {
        "username": player.username,
        "email": player.email,
        "join_date": player.join_date.isoformat() if player.join_date else "",
    }
    return render_template("players/form.html", player=player, vals=vals)


@main.route("/players/<int:player_id>/delete", methods=["POST"])
def player_delete(player_id):
    player = db.get_or_404(Player, player_id)
    username = player.username
    db.session.delete(player)
    db.session.commit()
    flash(f"Player '{username}' deleted.", "warning")
    return redirect(url_for("main.players_index"))


# ── Play Sessions ─────────────────────────────────────────────────────────────

@main.route("/players/<int:player_id>/log-session", methods=["GET", "POST"])
def log_session(player_id):
    player = db.get_or_404(Player, player_id)
    player_games = (
        PlayerGame.query.filter_by(player_id=player_id)
        .join(Game)
        .order_by(Game.title)
        .all()
    )

    if request.method == "POST":
        player_game_id_str = request.form.get("player_game_id", "").strip()
        session_date_str = request.form.get("session_date", "").strip()
        duration_str = request.form.get("duration_minutes", "").strip()

        errors = []
        if not player_game_id_str:
            errors.append("Please select a game.")

        session_date = None
        if not session_date_str:
            errors.append("Session date is required.")
        else:
            try:
                session_date = date.fromisoformat(session_date_str)
            except ValueError:
                errors.append("Invalid session date.")

        duration = None
        if not duration_str:
            errors.append("Duration is required.")
        else:
            try:
                duration = int(duration_str)
                if duration <= 0:
                    errors.append("Duration must be a positive number of minutes.")
            except ValueError:
                errors.append("Duration must be a whole number of minutes.")

        pg = None
        if player_game_id_str:
            try:
                pg = db.session.get(PlayerGame, int(player_game_id_str))
            except (ValueError, TypeError):
                pg = None
            if not pg or pg.player_id != player_id:
                errors.append("Invalid game selection.")
                pg = None

        if errors:
            for e in errors:
                flash(e, "danger")
            return render_template(
                "players/log_session.html", player=player, player_games=player_games, vals=request.form
            )

        # Atomic: insert session + recalculate total_play_hours in one transaction
        new_session = PlaySession(
            player_game_id=pg.player_game_id,
            session_date=session_date,
            duration_minutes=duration,
        )
        db.session.add(new_session)
        db.session.flush()  # persist within transaction so aggregate includes new row
        total_minutes = (
            db.session.query(func.sum(PlaySession.duration_minutes))
            .filter(PlaySession.player_game_id == pg.player_game_id)
            .scalar()
            or 0
        )
        pg.total_play_hours = round(total_minutes / 60, 2)
        db.session.commit()
        flash(f"Session of {duration} minutes logged.", "success")
        return redirect(url_for("main.player_detail", player_id=player_id))

    return render_template("players/log_session.html", player=player, player_games=player_games, vals={})


# ── Seed Data ─────────────────────────────────────────────────────────────────

@main.route("/seed")
def seed():
    if Publisher.query.first():
        flash("Database already has data. Delete app.db to re-seed.", "info")
        return redirect(url_for("main.index"))

    pub1 = Publisher(name="Nintendo", country="Japan", founded_date=date(1889, 9, 23))
    pub2 = Publisher(name="Valve", country="USA", founded_date=date(1996, 8, 24))
    pub3 = Publisher(name="CD Projekt Red", country="Poland", founded_date=date(1994, 5, 1))
    db.session.add_all([pub1, pub2, pub3])
    db.session.flush()

    g1 = Game(title="The Legend of Zelda: BotW", genre="Action-Adventure",
              release_date=date(2017, 3, 3), price=Decimal("59.99"), publisher_id=pub1.publisher_id)
    g2 = Game(title="Portal 2", genre="Puzzle",
              release_date=date(2011, 4, 19), price=Decimal("9.99"), publisher_id=pub2.publisher_id)
    g3 = Game(title="The Witcher 3", genre="RPG",
              release_date=date(2015, 5, 19), price=Decimal("39.99"), publisher_id=pub3.publisher_id)
    g4 = Game(title="Half-Life: Alyx", genre="FPS",
              release_date=date(2020, 3, 23), price=Decimal("59.99"), publisher_id=pub2.publisher_id)
    db.session.add_all([g1, g2, g3, g4])
    db.session.flush()

    p1 = Player(username="xX_Link_Xx", email="link@hyrule.com", join_date=date(2023, 1, 15))
    p2 = Player(username="geralt99", email="geralt@kaermorhen.pl", join_date=date(2023, 3, 8))
    p3 = Player(username="valve_fan", email="gaben@valve.com", join_date=date(2022, 11, 22))
    db.session.add_all([p1, p2, p3])
    db.session.flush()

    pg1 = PlayerGame(player_id=p1.player_id, game_id=g1.game_id, rating=10,
                     purchase_date=date(2023, 1, 16), total_play_hours=Decimal("120.50"))
    pg2 = PlayerGame(player_id=p1.player_id, game_id=g2.game_id, rating=8,
                     purchase_date=date(2023, 2, 1), total_play_hours=Decimal("15.00"))
    pg3 = PlayerGame(player_id=p2.player_id, game_id=g3.game_id, rating=10,
                     purchase_date=date(2023, 3, 10), total_play_hours=Decimal("200.00"))
    pg4 = PlayerGame(player_id=p3.player_id, game_id=g2.game_id, rating=9,
                     purchase_date=date(2022, 12, 1), total_play_hours=Decimal("30.00"))
    pg5 = PlayerGame(player_id=p3.player_id, game_id=g4.game_id, rating=7,
                     purchase_date=date(2023, 4, 5), total_play_hours=Decimal("45.50"))
    db.session.add_all([pg1, pg2, pg3, pg4, pg5])
    db.session.flush()

    s1 = PlaySession(player_game_id=pg1.player_game_id, session_date=date(2023, 6, 1), duration_minutes=180)
    s2 = PlaySession(player_game_id=pg3.player_game_id, session_date=date(2023, 6, 2), duration_minutes=240)
    s3 = PlaySession(player_game_id=pg5.player_game_id, session_date=date(2023, 6, 3), duration_minutes=120)
    db.session.add_all([s1, s2, s3])
    db.session.commit()

    flash("Sample data seeded successfully.", "success")
    return redirect(url_for("main.index"))
