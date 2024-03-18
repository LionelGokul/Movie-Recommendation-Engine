import requests, os, pandas as pd
from threading import Thread
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.metrics.pairwise import cosine_similarity

api_key = "f9204ba2"
# Step 1: Read CSV File
df = pd.read_csv("movie_dataset.csv")


def get_title_from_index(index):
    return df[df.index == index]["title"].values[0]


def get_index_from_title(title):
    return int(df[df.title == title]["index"].values[0])


def combine_features(row):
    return row['keywords'] + " " + row['cast'] + " " + row["genres"] + " " + row["director"]


def get_similar_movies(movie_user_likes):
    # Select Features

    features = ['keywords', 'cast', 'genres', 'director']

    # Create a column in DF which combines all selected features
    for feature in features:
        df[feature] = df[feature].fillna('')

    df["combined_features"] = df.apply(combine_features, axis=1)

    # Create count matrix from this new combined column
    cv = CountVectorizer()

    count_matrix = cv.fit_transform(df["combined_features"])

    # Compute the Cosine Similarity based on the count_matrix
    user_movie_vector = count_matrix[get_index_from_title(movie_user_likes), :]
    cosine_sim = cosine_similarity(user_movie_vector, count_matrix)

    # Get index of this movie from its title
    movie_index = get_index_from_title(movie_user_likes)

    similar_movies = list(enumerate(cosine_sim[0]))

    # Get a list of similar movies in descending order of similarity score
    sorted_similar_movies = sorted(similar_movies, key=lambda x: x[1], reverse=True)

    similar_movies_details = [{
        'name': get_title_from_index(i[0]),
        'match': i[1] * 100

    } for i in sorted_similar_movies[1:21]]

    return similar_movies_details


def get_autocomplete_suggestion(keyword):
    filtered_rows = df[df['original_title'].str.lower().str.contains(keyword, na=False)]['original_title'].values
    list_filtered_rows = filtered_rows.tolist()

    if len(list_filtered_rows) > 30:
        return list_filtered_rows[:30]

    return list_filtered_rows


def get_movie_poster(movie):
    url = "http://www.omdbapi.com/?apikey=" + api_key
    querystring = {"type": "movie", "t": movie["name"]}
    headers = {
        "Content-Type": "application/json"
    }
    response = requests.request("GET", url, headers=headers, params=querystring).json()
    movie_poster = {}
    movie_details = df[df.title == movie["name"]]

    if "Error" in response:
        movie_poster = {
            "title": movie["name"],
            "image_url": "",
            "plot": movie_details["overview"].values[0],
            "rating": movie_details["vote_average"].values[0],
            "runtime": movie_details['runtime'].values[0],
            "genres": movie_details['genres'].values[0],
            "release_date": movie_details['release_date'].values[0],
            "match": movie["match"]
        }

        return movie_poster
    else:
        movie_poster = {
            "title": movie["name"],
            "image_url": response["Poster"],
            "plot": response["Plot"],
            "rating": response["imdbRating"],
            "runtime": movie_details['runtime'].values[0],
            "genres": movie_details['genres'].values[0],
            "release_date": movie_details['release_date'].values[0],
            "match": movie["match"]
        }
        return movie_poster


def get_recommended_movies(movie_name):
    movie_details = {}
    recommended_movies = []

    if df[df.title == movie_name].empty:
        return recommended_movies

    recom_mov_list = get_similar_movies(movie_name)

    for movie in recom_mov_list:
        df_movie_details = df[df.title == movie["name"]]

        if not df_movie_details['img_url'].any():
            movie_details = get_movie_poster(movie)
        else:
            movie_details = {
                "title": movie["name"],
                "image_url": df_movie_details['img_url'].values[0],
                "plot": df_movie_details['plot'].values[0],
                "rating": df_movie_details['imdb_rating'].values[0],
                "runtime": df_movie_details['runtime'].values[0],
                "genres": df_movie_details['genres'].values[0],
                "release_date": df_movie_details['release_date'].values[0],
                "match": movie["match"]
            }
        recommended_movies.append(movie_details)
    # call async save_details here
    save_details_async = Thread(target=save_details, args=(recommended_movies,))
    save_details_async.start()
    return recommended_movies


def save_details(movie_details):
    del df['combined_features']
    os.remove("movie_dataset.csv")
    for movie_detail in movie_details:
        if df[df.title == movie_detail['title']]['img_url'].isnull().values.any():
            index = df.index[df.title == movie_detail['title']].values[0]
            df.at[index, 'img_url'] = movie_detail["image_url"]
            df.at[index, 'plot'] = movie_detail["plot"]
            df.at[index, 'imdb_rating'] = movie_detail["rating"]
    df.to_csv('movie_dataset.csv')
