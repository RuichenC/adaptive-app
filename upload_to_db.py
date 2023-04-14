import pandas as pd
import mysql.connector

cnx = mysql.connector.connect(user='root', password='rootpassword',
                              host='130.211.55.25', port='3306',
                              database='movie')
cursor = cnx.cursor()

movies_df = pd.read_csv('movies.csv')

cursor.execute("TRUNCATE TABLE movie.movies")

for index, row in movies_df.iterrows():
    try:
        cursor.execute("INSERT INTO movie.movies (movie_id, movie_title, imdb_rating, geners, overview, plot_keywords, director, top_5_casts, writer, year, movie_sentence) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)", (str(row['movie_id']), row['movie_title'], str(row['imdb_rating']), row['geners'], row['overview'], row['plot_keywords'], row['director'], row['top_5_casts'], row['writer'], str(row['year']), row['movie_sentence']))
        cnx.commit()
    except:
        print("Error: " + str(row['movie_id']))
        break

cursor.close()
cnx.close()
