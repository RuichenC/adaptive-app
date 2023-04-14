from flask import Flask, request, jsonify
from flask_restful import Resource, Api, reqparse
from flask_cors import CORS
from flask_jwt_extended import JWTManager, jwt_required, create_access_token, get_jwt_identity
from werkzeug.security import generate_password_hash, check_password_hash

import pandas as pd
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np
import pickle

import os
from models import db, User, Movie

app = Flask(__name__)
CORS(app, origins="*")
basedir = os.path.abspath(os.path.dirname(__file__))
USER = 'root'
PASSWORD = 'rootpassword'
HOST = '130.211.55.25'
PORT = '3306'
DATABASE = 'movie'
app.config['SQLALCHEMY_DATABASE_URI'] = f'mysql+mysqlconnector://{USER}:{PASSWORD}@{HOST}:{PORT}/{DATABASE}'
app.config['SECRET_KEY'] = os.urandom(24)
app.config['JWT_SECRET_KEY'] = os.urandom(24)
app.config['CORS_HEADERS'] = 'Content-Type,Authorization'


db.init_app(app)
api = Api(app)
jwt = JWTManager(app)

user_parser = reqparse.RequestParser()
user_parser.add_argument("uname", type=str, required=True, help="Username is required")
user_parser.add_argument("mail", type=str, required=False)
user_parser.add_argument("passw", type=str, required=True, help="Password is required")
user_parser.add_argument("country", type=str, required=False, help="Country is required")

movie_search_parser = reqparse.RequestParser()
movie_search_parser.add_argument("query", type=str, required=False)


class Register(Resource):
    def post(self):
        args = user_parser.parse_args()
        uname = args['uname']
        mail = args['mail']
        passw = args['passw']
        country = args['country']

        if User.query.filter_by(username=uname).first() is not None:
            return {"message": "Username already taken"}, 400

        hashed_password = generate_password_hash(passw, method="sha256")
        new_user = User(username=uname, email=mail, password=hashed_password, country=country)
        db.session.add(new_user)
        db.session.commit()

        return {"message": "Registration successful"}, 201


class Login(Resource):
    def post(self):
        args = user_parser.parse_args()
        uname = args["uname"]
        passw = args["passw"]

        user = User.query.filter_by(username=uname).first()
        if user and check_password_hash(user.password, passw):
            access_token = create_access_token(identity=user.id)
            return {"access_token": access_token, "message": "Logged in successfully","user_id":user.id}, 200
        else:
            return {"message": "Invalid credentials"}, 401


class Profile(Resource):
   # @jwt_required()
    def get(self):
        user_id = get_jwt_identity()
        user = User.query.filter_by(id=user_id).first()
        return {
            "id": user.id,
            "username": user.username,
            "email": user.email,
            "country": user.country
        }, 200


class Index(Resource):
    def get(self):
        return {"message": "Welcome to the Movie API!"}, 200


class LikeMovie(Resource):
    #@jwt_required()
    def post(self, movie_id):
        user_id = 1
        user = User.query.filter_by(id=user_id).first()
        movie = Movie.query.get_or_404(movie_id)
        user.liked_movies.append(movie)
        db.session.commit()
        return {"message": f"Movie {movie_id} liked."}, 200


class LikedMovies(Resource):
    #@jwt_required()
    def get(self):
        user_id = 1
        user = User.query.filter_by(id=user_id).first()
        liked_movies = [
            {
                "id": movie.movie_id,
                "title": movie.movie_title,
                # Add other movie attributes here if needed
            }
            for movie in user.liked_movies
        ]
        return {"liked_movies": liked_movies}, 200

class RemoveLikedMovie(Resource):
    #@jwt_required()
    def post(self, movie_id):
        user_id = 1
        user = User.query.filter_by(id=user_id).first()
        movie = Movie.query.get_or_404(movie_id)
        user.liked_movies.remove(movie)
        db.session.commit()
        return {"message": f"Movie {movie_id} removed from liked movies."}, 200

class RemoveDislikedMovie(Resource):
    #@jwt_required()
    def post(self, movie_id):
        user_id = 1
        user = User.query.filter_by(id=user_id).first()
        movie = Movie.query.get_or_404(movie_id)
        user.disliked_movies.remove(movie)
        db.session.commit()
        return {"message": f"Movie {movie_id} removed from disliked movies."}, 200

class DislikeMovie(Resource):
    #@jwt_required()
    def post(self, movie_id):
        user_id = 1
        user = User.query.filter_by(id=user_id).first()
        movie = Movie.query.get_or_404(movie_id)
        user.disliked_movies.append(movie)
        db.session.commit()
        return {"message": f"Movie {movie_id} disliked."}, 200

class DislikedMovies(Resource):
    #@jwt_required()
    def get(self):
        user_id = 1
        user = User.query.filter_by(id=user_id).first()
        disliked_movies = [
            {
                "id": movie.movie_id,
                "title": movie.movie_title,
                # Add other movie attributes here if needed
            }
            for movie in user.disliked_movies
        ]
        return {"disliked_movies": disliked_movies}, 200
    
class SearchMovies(Resource):
    #@jwt_required()
    def get(self):
        query = request.args.get("query")
        print(query)
        if not query:
            return {'message': 'Please provide a search query.'}, 400
        matched_movies = Movie.query.filter(Movie.movie_title.ilike(f'%{query}%')).limit(20).all()
        result = [
            {
                "id": movie.movie_id,
                "title": movie.movie_title,
                # Add other movie attributes here if needed
            }
            for movie in matched_movies
        ]
        return {'matched_movies': result}, 200
    
class Recommendations(Resource):
    def __init__(self) -> None:
        super().__init__()
        self.embeddings = pickle.load(open("embeddings.pkl", "rb"))
    
    def get_liked_movies(self, user_id):
        user_id = 1
        liked_movie_ids = User.query.get(user_id).liked_movies
        return liked_movie_ids
    
    def get_disliked_movies(self, user_id):
        user_id = 1
        disliked_movie_ids = User.query.get(user_id).disliked_movies
        return disliked_movie_ids
    
    def get(self):
        disliked_movie_ids = [movie.movie_id for movie in self.get_disliked_movies(1)]
        liked_movie_ids = [movie.movie_id for movie in self.get_liked_movies(1)]
        liked_movie_df = pd.DataFrame(liked_movie_ids, columns=['movie_id'])
        liked_movie_df['movie_sentence'] = [movie.movie_sentence for movie in Movie.query.filter(Movie.movie_id.in_(liked_movie_ids)).all()]
        all_movies_obj = Movie.query.all()
        all_movie_df = pd.DataFrame(columns=['movie_id', 'movie_title', 'movie_sentence'])
        all_movie_df['movie_id'] = [movie.movie_id for movie in all_movies_obj]
        all_movie_df['movie_title'] = [movie.movie_title for movie in all_movies_obj]
        all_movie_df['movie_sentence'] = [movie.movie_sentence for movie in all_movies_obj]
        all_movie_df['genre'] = [movie.geners for movie in all_movies_obj]
        all_movie_df.genre = all_movie_df.genre.apply(lambda x: eval(x))
        embeddings_df = pd.DataFrame(self.embeddings)
        embeddings_df = embeddings_df.apply(lambda row: row.to_numpy(), axis=1)
        all_movie_df['embeddings'] = embeddings_df[:23922]
        all_movie_df = all_movie_df[~all_movie_df['movie_id'].isin(disliked_movie_ids)]

        recommendations = {'top_10': []}
        all_genre = set()
        for index, row in all_movie_df.iterrows():
            all_genre.update(row['genre'])
        
        for genre in all_genre:
            recommendations[genre] = []

        for movie_id in liked_movie_ids:
            all_movie_df[movie_id] = all_movie_df['embeddings'].apply(lambda x: cosine_similarity([x], [all_movie_df[all_movie_df['movie_id'] == movie_id]['embeddings'].values[0]])[0][0])
        
        all_movie_df['avg_similarity'] = all_movie_df[liked_movie_ids].mean(axis=1)
        all_movie_df = all_movie_df.sort_values(by='avg_similarity', ascending=False)


        ten = 0
        for index, row in all_movie_df.iterrows():
            if ten < 10:
                recommendations['top_10'].append({'id': row['movie_id'], 'title': row['movie_title']})
                ten += 1
            for genre in row['genre']:
                if len(recommendations[genre]) < 10:
                    recommendations[genre].append({'id': row['movie_id'], 'title': row['movie_title']})

        return recommendations, 200

        

# Remove the Logout resource since JWT doesn't have a server-side logout.
# api.add_resource(Logout, "/api/logout")

# Replace UserLoader with Profile.
# api.add_resource(UserLoader, "/api/user_loader")
api.add_resource(Profile, "/api/profile")
api.add_resource(Index, "/api/index")
api.add_resource(Register, "/api/register")
api.add_resource(Login, "/api/login")
#api.add_resource(Profile, "/api/profile")
api.add_resource(LikeMovie, "/api/like/<int:movie_id>")
api.add_resource(DislikeMovie, "/api/dislike/<int:movie_id>")
api.add_resource(LikedMovies, "/api/liked_movies")
api.add_resource(DislikedMovies, "/api/disliked_movies")
api.add_resource(SearchMovies, "/api/search_movies")
api.add_resource(RemoveLikedMovie, "/api/remove_liked/<int:movie_id>")
api.add_resource(RemoveDislikedMovie, "/api/remove_disliked/<int:movie_id>")
api.add_resource(Recommendations, "/api/recommendations")

if __name__ == "__main__":
    # with app.app_context():
    #     db.create_all()
    app.run(debug=True)
