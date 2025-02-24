import streamlit as st
import pickle
import pandas as pd
import requests
import subprocess

similarity = None
movies_dict = None

try:
    # Try to load the files from local storage
    similarity = pickle.load(open('similarity.pkl', 'rb'))
    movies_dict = pickle.load(open('movie_dict.pkl', 'rb'))

except FileNotFoundError:
    # If files are not found locally, try to fetch them from LFS
    def load_lfs_file(file_path):
        process = subprocess.run(["git", "lfs", "get", file_path], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        if process.returncode != 0:
            print("Error fetching LFS file:", file_path)
            return None

        temp_file_path = f"/tmp/{file_path}"
        with open(temp_file_path, "wb") as f:
            f.write(process.stdout)

        return temp_file_path

    try:
        similarity = pickle.load(open(load_lfs_file('similarity.pkl'), 'rb'))
        movies_dict = pickle.load(open(load_lfs_file('movie_dict.pkl'), 'rb'))

    except Exception as e:
        print("Error loading files:", str(e))

if similarity is None or movies_dict is None:
    st.error("Failed to load files. Please check your GitHub LFS setup.")
else:
    # Load the data into a Pandas DataFrame
    movies = pd.DataFrame(movies_dict)
    movie_names = movies['title'].values

    st.title('Content Based Movie Recommender System')

def recommend(movie):
    movie_idx = movies[movies['title']== movie].index[0]
    movies_list = sorted(list(enumerate(similarity[movie_idx])),reverse=True,key= lambda x:x[1])[1:6]
    recommended_movie_names = []
    recommended_movie_posters = []
    for i in movies_list:
        movie_id =movies.iloc[i[0]].id
        recommended_movie_names.append(movies.iloc[i[0]].title)
        recommended_movie_posters.append(fetch_poster(movie_id))
    return recommended_movie_names,recommended_movie_posters

def fetch_poster(movie_id):
    url = "https://api.themoviedb.org/3/movie/{}?api_key=8265bd1679663a7ea12ac168da84d2e8&language=en-US".format(movie_id)
    data = requests.get(url)
    data = data.json()
    poster_path = data['poster_path']
    full_path = "https://image.tmdb.org/t/p/w500/" + poster_path
    return full_path



selected_movie_name = st.selectbox('Name one of your Favourite movies',movie_names)

if st.button('Recommend Similar Movies'):
    recommended_movie_names,recommended_movie_posters = recommend(selected_movie_name)
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
