from flask import Flask, render_template, flash, redirect, url_for, session, logging, request
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from flask_restful import Resource, Api, reqparse

import os
from models import db, User

app = Flask(__name__)
basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{os.path.join(basedir, "database.db")}'
# app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+mysqlconnector://your_username:your_password@your_instance_ip:3306/your_database'
app.config['SECRET_KEY'] = os.urandom(24)

db.init_app(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"



# Initialize the API
api = Api(app)
# Set up an argument parser for user registration and login
user_parser = reqparse.RequestParser()
user_parser.add_argument("uname", type=str, required=True, help="Username is required")
user_parser.add_argument("mail", type=str, required=False)
user_parser.add_argument("passw", type=str, required=True, help="Password is required")


class Register(Resource):
    def post(self):
        args = user_parser.parse_args()
        uname = args['uname']
        mail = args['mail']
        passw = args['passw']

        if User.query.filter_by(username=uname).first() is not None:
            return {"message": "Username already taken"}, 400

        hashed_password = generate_password_hash(passw, method="sha256")
        new_user = User(username=uname, email=mail, password=hashed_password)
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
            login_user(user)
            return {"message": "Logged in successfully"}, 200
        else:
            return {"message": "Invalid credentials"}, 401


class Logout(Resource):
    @login_required
    def post(self):
        logout_user()
        return {"message": "Logged out successfully"}, 200


class Profile(Resource):
    @login_required
    def get(self):
        user = User.query.filter_by(id=current_user.id).first()
        return {
            "id": user.id,
            "username": user.username,
            "email": user.email
        }, 200


class UserLoader(Resource):
    @login_required
    def get(self):
        user = User.query.get(int(current_user.id))
        return {
            "id": user.id,
            "username": user.username,
            "email": user.email
        }


class Index(Resource):
    def get(self):
        if current_user.is_authenticated:
            return {"message": "Welcome, {}!".format(current_user.username)}, 200
        else:
            return {"message": "Welcome, guest!"}, 200


api.add_resource(Index, "/api/index")
api.add_resource(Register, "/api/register")
api.add_resource(Login, "/api/login")
api.add_resource(Logout, "/api/logout")
api.add_resource(Profile, "/api/profile")
api.add_resource(UserLoader, "/api/user_loader")


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=True)
