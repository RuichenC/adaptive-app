import pandas as pd
from sqlalchemy import create_engine
from app import basedir, app
from models import Movie, db
import os

# Read the CSV file
data = pd.read_csv("movies.csv")
data = data.rename(columns={
    "movie title": "movie_title",
    "Run Time": "run_time",
    "User Rating": "user_rating",
    "Generes": "genres",
    "Top 5 Casts": "top5_cast"
})
# Create an engine to connect to your database
engine = create_engine(f'sqlite:///{os.path.join(basedir, "database.db")}') # Replace with your actual database URI

# Bind the db object to the engine
db.metadata.bind = engine

# Create the tables in the database if they don't exist
with app.app_context():
    db.create_all()

# Insert the data into the table
data.to_sql("movie", engine, if_exists="append", index=False)


