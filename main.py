import pickle
import streamlit as st
import pandas as pd
import os
# import ast
import requests
import base64

st.set_page_config(page_title='MOVIE ALCHEMY', page_icon=':smiley:')

# Load data for the app
movies = pickle.load(open('movie_list.pkl', 'rb'))
similarity = pickle.load(open('similarity.pkl', 'rb'))


# Data Preprocessing
def fetch_poster(movie_id):
    url = "https://api.themoviedb.org/3/movie/{}?api_key=8265bd1679663a7ea12ac168da84d2e8&language=en-US".format(movie_id)
    data = requests.get(url)
    data = data.json()
    poster_path = data['poster_path']
    full_path = "https://image.tmdb.org/t/p/w500/" + poster_path
    return full_path


def recommend(movie):
    index = movies[movies['title'] == movie].index[0]
    distances = sorted(list(enumerate(similarity[index])), reverse=True, key=lambda x: x[1])
    recommended_movies = []
    for i in distances[1:6]:
        if i[0] < len(movies):  # Check if the index is within bounds
            movie_details = movies.iloc[i[0]]
            recommended_movie = {   
                'title': movie_details['title'],
                'poster': fetch_poster(movie_details['movie_id']),
                'overview': " ".join(movie_details['overview']),
                'cast': ", ".join(movie_details['cast']),
            }
            recommended_movies.append(recommended_movie)

    return recommended_movies

# Streamlit app
st.title('Movie Alchemy')

# Sidebar for selecting genre
genre_list = sorted(movies['genres'].explode().astype(str).unique())
selected_genre = st.sidebar.selectbox(
    "Choose a genre",
    genre_list
)

# Filter movies based on selected genre
genre_movies = movies[movies['genres'].apply(lambda x: selected_genre in x)]

# Sidebar for selecting movie within the chosen genre
selected_movie = st.sidebar.selectbox(
    "Type or select a movie from the dropdown",
    genre_movies['title'].values
)
show_recommendations = st.sidebar.button('Show Recommendations')

if show_recommendations and selected_movie:
    # Show recommendations only if 'Show Recommendations' button is clicked and a movie is selected
    st.title(f'List of recommended movies for {selected_movie}')
    recommended_movies = recommend(selected_movie)

    if recommended_movies:
        for movie in recommended_movies:
            st.write(movie['title'])
            st.image(movie['poster'], width=150)
            st.write("Overview:", movie['overview'])
            st.write("Cast:", movie['cast'])
            st.write("-------------------------------")
    else:
        st.write("No recommendations found.")
