import pickle
import streamlit as st
import requests
import os

def fetch_poster(movie_id):
    url = f"https://api.themoviedb.org/3/movie/{movie_id}"

    tmdb_token = os.getenv('TMDB_API_TOKEN')
    if not tmdb_token:
        st.error("TMDB API Token not found. Please set the TMDB_API_TOKEN environment variable.")
        return "https://via.placeholder.com/300x450?text=API+Token+Missing"
    
    headers = {
        "accept": "application/json",
        "Authorization": f"Bearer {tmdb_token}"
    }

    try:
        response = requests.get(url, headers=headers, timeout=5)
        response.raise_for_status()
        data = response.json()
        poster_path = data.get('poster_path')

        if poster_path:
            full_path = "https://image.tmdb.org/t/p/w500" + poster_path
            return full_path
        else:
            return "https://via.placeholder.com/300x450?text=No+Poster"
    except requests.exceptions.RequestException as e:
        print(f"Error fetching poster: {e}")
        return "https://via.placeholder.com/300x450?text=Error"


def recommend(movie):
    index = movies[movies['title'] == movie].index[0]
    # Use precomputed top-k indices
    top_indices = topk_indices[index]
    recommended_movie_names = []
    recommended_movie_posters = []
    for idx in top_indices:
        if idx == index:
            continue
        movie_id = movies.iloc[idx].movie_id
        recommended_movie_posters.append(fetch_poster(movie_id))
        recommended_movie_names.append(movies.iloc[idx].title)
        if len(recommended_movie_names) >= 5:
            break

    return recommended_movie_names, recommended_movie_posters


st.header('Movie Recommender System')

# Debug: Print current directory and list files
import os
st.write("Current directory:", os.getcwd())
st.write("Files in directory:", os.listdir())

import numpy as np

# Load the data files
try:
    movies = pickle.load(open('movie_list.pkl','rb'))
    st.success("Successfully loaded movie_list.pkl")
except Exception as e:
    st.error(f"Error loading movie_list.pkl: {str(e)}")
try:
    topk = np.load('similarity_topk.npz')
    topk_indices = topk['indices']
    topk_values = topk['values']
    st.success("Successfully loaded similarity_topk.npz")
except Exception as e:
    st.error(f"Error loading similarity_topk.npz: {str(e)}")

movie_list = movies['title'].values
selected_movie = st.selectbox(
    "Type or select a movie from the dropdown",
    movie_list
)

if st.button('Show Recommendation'):
    recommended_movie_names,recommended_movie_posters = recommend(selected_movie)
    col1, col2, col3, col4, col5 = st.columns(5)
    with col1:
        st.text(recommended_movie_names[0])
        st.image(recommended_movie_posters[0])
    with col2:
        st.text(recommended_movie_names[1])
        st.image(recommended_movie_posters[1])

    with col3:
        st.text(recommended_movie_names[2])
        st.image(recommended_movie_posters[2])
    with col4:
        st.text(recommended_movie_names[3])
        st.image(recommended_movie_posters[3])
    with col5:
        st.text(recommended_movie_names[4])
        st.image(recommended_movie_posters[4])




