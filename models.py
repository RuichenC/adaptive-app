from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin


db = SQLAlchemy()

# Association table for likes
likes = db.Table('likes',
                 db.Column('user_id', db.Integer, db.ForeignKey('user.id')),
                 db.Column('movie_id', db.Integer, db.ForeignKey('movies.movie_id'))
                 )

# Association table for dislikes
dislikes = db.Table('dislikes',
                    db.Column('user_id', db.Integer, db.ForeignKey('user.id')),
                    db.Column('movie_id', db.Integer, db.ForeignKey('movies.movie_id'))
                    )


class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String, unique=True)
    email = db.Column(db.String, unique=True)
    password = db.Column(db.String)
    country = db.Column(db.String)
    liked_movies = db.relationship('Movie', secondary=likes, backref='liked_by_users')
    disliked_movies = db.relationship('Movie', secondary=dislikes, backref='disliked_by_users')


# Add more models here, e.g., the Movie model.
class Movie(db.Model):
    __tablename__ = 'movies'
    movie_id = db.Column(db.Integer, primary_key=True)
    movie_title = db.Column(db.String, nullable=False)
    imdb_rating = db.Column(db.String, nullable=True)
    geners = db.Column(db.String, nullable=True)
    overview = db.Column(db.Text, nullable=True)
    plot_keywords = db.Column(db.String, nullable=True)
    director = db.Column(db.String, nullable=True)
    top_5_casts = db.Column(db.String, nullable=True)
    writer = db.Column(db.String, nullable=True)
    year = db.Column(db.Integer, nullable=True)
    movie_sentence = db.Column(db.String, nullable=True)
