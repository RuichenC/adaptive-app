from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

db = SQLAlchemy()


class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True)
    email = db.Column(db.String(120), unique=True)
    password = db.Column(db.String(255))
    country = db.Column(db.String(50))


# Add more models here, e.g., the Movie model.
class Movie(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    movie_title = db.Column(db.String(255), nullable=False)
    run_time = db.Column(db.Integer, nullable=True)
    rating = db.Column(db.String(50), nullable=True)
    user_rating = db.Column(db.Float, nullable=True)
    genres = db.Column(db.String(255), nullable=True)
    overview = db.Column(db.Text, nullable=True)
    plot_keywords = db.Column(db.String(255), nullable=True)
    director = db.Column(db.String(255), nullable=True)
    top5_cast = db.Column(db.String(255), nullable=True)
    writer = db.Column(db.String(255), nullable=True)
    year = db.Column(db.Integer, nullable=True)
    path = db.Column(db.String(255), nullable=True)
    plot_keywords_str = db.Column(db.String(255), nullable=True)
    casts_str = db.Column(db.String(255), nullable=True)
    movie_sentence = db.Column(db.String(255), nullable=True)
