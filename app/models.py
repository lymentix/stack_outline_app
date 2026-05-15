from datetime import datetime
from .extensions import db


class Publisher(db.Model):
    __tablename__ = "publishers"

    publisher_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    country = db.Column(db.String(50))
    founded_date = db.Column(db.Date)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # One publisher -> many games
    games = db.relationship("Game", back_populates="publisher", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Publisher {self.name}>"


class Game(db.Model):
    __tablename__ = "games"

    game_id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(150), nullable=False)
    genre = db.Column(db.String(50))
    release_date = db.Column(db.Date, nullable=False)
    price = db.Column(db.Numeric(6, 2))
    publisher_id = db.Column(db.Integer, db.ForeignKey("publishers.publisher_id"))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    publisher = db.relationship("Publisher", back_populates="games")
    player_games = db.relationship("PlayerGame", back_populates="game", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Game {self.title}>"


class Player(db.Model):
    __tablename__ = "players"

    player_id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), nullable=False)
    email = db.Column(db.String(100), nullable=False, unique=True)
    join_date = db.Column(db.Date, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    player_games = db.relationship("PlayerGame", back_populates="player", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Player {self.username}>"


class PlayerGame(db.Model):
    __tablename__ = "player_games"

    player_game_id = db.Column(db.Integer, primary_key=True)
    player_id = db.Column(db.Integer, db.ForeignKey("players.player_id"), nullable=False)
    game_id = db.Column(db.Integer, db.ForeignKey("games.game_id"), nullable=False)
    rating = db.Column(db.Integer)
    purchase_date = db.Column(db.Date, nullable=False)
    total_play_hours = db.Column(db.Numeric(6, 2), default=0.00)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    player = db.relationship("Player", back_populates="player_games")
    game = db.relationship("Game", back_populates="player_games")
    play_sessions = db.relationship("PlaySession", back_populates="player_game", cascade="all, delete-orphan")

    __table_args__ = (
        db.CheckConstraint("rating >= 1 AND rating <= 10", name="rating_range"),
    )

    def __repr__(self):
        return f"<PlayerGame player={self.player_id} game={self.game_id}>"


class PlaySession(db.Model):
    __tablename__ = "play_sessions"

    session_id = db.Column(db.Integer, primary_key=True)
    player_game_id = db.Column(db.Integer, db.ForeignKey("player_games.player_game_id"), nullable=False)
    session_date = db.Column(db.Date, nullable=False)
    duration_minutes = db.Column(db.Integer, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    player_game = db.relationship("PlayerGame", back_populates="play_sessions")

    def __repr__(self):
        return f"<PlaySession {self.session_id} duration={self.duration_minutes}m>"