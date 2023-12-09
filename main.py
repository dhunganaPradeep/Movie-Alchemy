import pickle
import streamlit as st
import requests
import base64
import time
from random import randint

st.set_page_config(page_title='MOVIE ALCHEMY', page_icon=':smiley:')

# Load data for the app
movies = pickle.load(open('movie_list.pkl', 'rb'))
similarity = pickle.load(open('similarity.pkl', 'rb'))

# Data Preprocessing
def fetch_poster(movie_id):
    url = f"https://api.themoviedb.org/3/movie/{movie_id}?api_key=8265bd1679663a7ea12ac168da84d2e8&language=en-US"
    data = requests.get(url).json()
    poster_path = data['poster_path']
    return f"https://image.tmdb.org/t/p/w500/{poster_path}"

def recommend(movie):
    index = movies[movies['title'] == movie].index[0]
    distances = sorted(list(enumerate(similarity[index])), reverse=True, key=lambda x: x[1])
    recommended_movies = []
    for i in distances[1:6]:
        if i[0] < len(movies):
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

# Check if recommendations should be displayed
if show_recommendations and selected_movie:
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
else:
    # Display the "You may Like" and "Featured Movies" sections
    num_posters = 4

    st.header('You may Like')
    with st.container():
        poster_container = st.container()

        # Open a new row
        with poster_container:
            columns = st.columns(num_posters)

            for i in range(num_posters):
                movie = movies.iloc[i]
                poster_url = fetch_poster(movie['movie_id'])
                columns[i].write(
                    f'<img src="{poster_url}" width="170" style="cursor: pointer; margin-bottom: 20px;" class="poster">'
                    , unsafe_allow_html=True)

    # Display the "Featured Movies" section
    st.header('Featured Movies')
    featured_movies = ['Inception', 'The Shawshank Redemption', 'The Dark Knight', 'Pulp Fiction', 'Fight Club']

    for movie_title in featured_movies:
        movie_details = movies[movies['title'] == movie_title].iloc[0]
        st.write(f"## {movie_title}")
        st.image(fetch_poster(movie_details['movie_id']), width=200)
        st.write(f"**Overview:** {' '.join(movie_details['overview'])}")
        st.write(f"**Cast:** {', '.join(movie_details['cast'])}")
        st.write("---")