import pickle
import streamlit as st
import requests
import os
import numpy as np

# Page config
st.set_page_config(page_title="Movie Recommender", layout="wide", initial_sidebar_state="expanded")

# Custom CSS for styling — cinematic movie theme
st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Montserrat:wght@400;700&family=Playfair+Display:wght@700&display=swap');
    :root{
        --bg:#05060a;
        --panel: rgba(255,255,255,0.03);
        --accent:#ffd166; /* warm gold */
        --muted: #9aa6b2;
    }
    html, body, .stApp {
        background: radial-gradient(ellipse at 20% 10%, rgba(255,255,255,0.02) 0%, transparent 20%),
                    linear-gradient(180deg,#001017 0%, #05060a 100%);
        color: #e6eef6;
        font-family: 'Montserrat', system-ui, -apple-system, 'Segoe UI', Roboto, 'Helvetica Neue', Arial;
    }
    .app-title{
        font-family: 'Playfair Display', Georgia, serif;
        font-size:48px; font-weight:700; color: var(--accent);
        letter-spacing:1px; margin-bottom:6px;
        text-shadow: 0 2px 8px rgba(0,0,0,0.6);
    }
    .app-sub{color:var(--muted); margin-top:4px; font-size:15px}
    .card{
        background: linear-gradient(180deg, rgba(255,255,255,0.02), rgba(255,255,255,0.01));
        padding:10px; border-radius:12px; text-align:center;
        box-shadow: 0 6px 20px rgba(2,6,23,0.6);
        border: 1px solid rgba(255,255,255,0.03);
    }
    .movie-title{font-weight:700; color:#fff; margin-top:10px; font-size:16px}
    .small{font-size:13px; color:var(--muted)}
    .sidebar .stButton>button{ background-color: var(--accent); color: #071124; font-weight:700 }

    /* Film-strip top accent */
    .film-strip{
        height:8px; width:100%; background:linear-gradient(90deg, rgba(255,255,255,0.06) 10%, transparent 10% 20% , rgba(255,255,255,0.06) 20% 30%); margin-bottom:18px; border-radius:4px;
    }

    /* Responsive poster */
    .card img{ border-radius:8px; }

    /* Make sidebar headings subtle */
    .css-1aumxhk .stButton>button{
        border-radius:8px;
    }

    </style>
    """,
    unsafe_allow_html=True,
)


def fetch_poster(movie_id):
    """Return poster URL for a TMDb movie id, or a placeholder if unavailable."""
    url = f"https://api.themoviedb.org/3/movie/{movie_id}"

    tmdb_token = os.getenv('TMDB_API_TOKEN')
    if not tmdb_token:
        # return a placeholder image when token missing
        return "https://via.placeholder.com/300x450?text=Poster+Unavailable"

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
    except requests.exceptions.RequestException:
        return "https://via.placeholder.com/300x450?text=Error"


def recommend(movie, topk=5):
    """Return top-k recommended movie titles and poster URLs for a given movie title."""
    index = movies[movies['title'] == movie].index[0]
    top_indices = topk_indices[index]
    recommended_movie_names = []
    recommended_movie_posters = []
    for idx in top_indices:
        if idx == index:
            continue
        movie_id = movies.iloc[idx].movie_id
        recommended_movie_posters.append(fetch_poster(movie_id))
        recommended_movie_names.append(movies.iloc[idx].title)
        if len(recommended_movie_names) >= topk:
            break

    return recommended_movie_names, recommended_movie_posters


# Header with logo
try:
    st.image('logo.svg', width=140)
except Exception:
    # fallback to text title if image fails to load
    pass
st.markdown("<div class='app-title'>Movie Recommender System</div>", unsafe_allow_html=True)
st.markdown("<div class='app-sub'>Find movies similar to your favorites — beautiful UI and poster previews</div>", unsafe_allow_html=True)

# Sidebar
with st.sidebar:
    st.markdown("## Controls")

    # Load movies list
    try:
        movies = pickle.load(open('movie_list.pkl', 'rb'))
    except Exception as e:
        st.error(f"Error loading movie_list.pkl: {e}")
        st.stop()

    movie_list = movies['title'].values
    selected_movie = st.selectbox("Choose a movie", movie_list)

    st.write("")
    token_present = bool(os.getenv('TMDB_API_TOKEN'))
    if not token_present:
        st.warning("TMDb token not set — posters will show placeholders. Add TMDB_API_TOKEN in Render Environment.")

    show_btn = st.button("Show Recommendations")

# Load top-k similarity indices
try:
    topk = np.load('similarity_topk.npz')
    topk_indices = topk['indices']
except Exception as e:
    st.error(f"Error loading similarity_topk.npz: {e}")
    st.stop()

# Main content area
if show_btn:
    with st.spinner('Finding recommendations...'):
        rec_names, rec_posters = recommend(selected_movie, topk=5)

    cols = st.columns(5, gap='large')
    for i, col in enumerate(cols):
        with col:
            if i < len(rec_names):
                name = rec_names[i]
                poster = rec_posters[i]
                st.markdown(
                    f"<div class='card'>\n<img src='{poster}' alt='{name}' style='width:100%; height:350px; object-fit:cover; border-radius:8px'/>\n<div class='movie-title'>{name}</div>\n<div class='small'>Recommendation #{i+1}</div>\n</div>",
                    unsafe_allow_html=True,
                )
            else:
                st.write("")

    st.markdown("<div class='small' style='margin-top:18px'>Posters provided by TMDb</div>", unsafe_allow_html=True)
else:
    st.markdown("<div style='margin-top:24px; color:#cbd5e1'>Select a movie from the sidebar and click 'Show Recommendations' to begin.</div>", unsafe_allow_html=True)




