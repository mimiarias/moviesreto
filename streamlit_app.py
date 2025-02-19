import streamlit as st
import pandas as pd
from google.cloud import firestore
from google.oauth2 import service_account
import json

# Cargar credenciales desde secrets.toml
key_dict = json.loads(st.secrets["textkey"])
creds = service_account.Credentials.from_service_account_info(key_dict)
db = firestore.Client(credentials=creds, project="movies-reto-tlg")

# Referencia a la colección "movies"
dbMovies = db.collection("movies")

st.sidebar.header("Opciones")

# Checkbox para mostrar todos los filmes
show_all = st.sidebar.checkbox("Mostrar todos los filmes")

# Buscar filmes por título
st.sidebar.subheader("Buscar Filme por Título")
search_title = st.sidebar.text_input("Título del filme")
btn_search = st.sidebar.button("Buscar filme")

# Filtrar por director
st.sidebar.subheader("Filtrar por Director")
directors = set(doc.to_dict().get("director", "Desconocido") for doc in dbMovies.stream())
selected_director = st.sidebar.selectbox("Selecciona un director", list(directors))
btn_filter = st.sidebar.button("Filtrar por director")

# Formulario para agregar un nuevo filme
st.sidebar.subheader("Agregar un nuevo filme")
new_title = st.sidebar.text_input("Name")
new_company = st.sidebar.text_input("Company")
new_director = st.sidebar.text_input("Director")
new_genre = st.sidebar.text_input("Genre")
btn_add = st.sidebar.button("Agregar Filme")

# Función para buscar filmes por título
def search_movies_by_title(title):
    title = title.lower()  # Ignorar mayúsculas/minúsculas
    movies_ref = dbMovies.stream()
    results = [doc.to_dict() for doc in movies_ref if title in doc.to_dict().get("title", "").lower()]
    return results

# Función para filtrar por director
def filter_movies_by_director(director):
    movies_ref = dbMovies.where(u'director', u'==', director).stream()
    results = [doc.to_dict() for doc in movies_ref]
    return results

# Función para agregar un nuevo filme
def add_movie(title, company, director, genre):
    dbMovies.add({"title": title, "company":company, "director": director, "genre": genre, })
    st.sidebar.success("Filme agregado exitosamente")

# Mostrar todos los filmes si el checkbox está activado
if show_all:
    all_movies = [doc.to_dict() for doc in dbMovies.stream()]
    st.header("Todos los Filmes")
    st.dataframe(pd.DataFrame(all_movies))

# Buscar y mostrar filmes por título
if btn_search and search_title:
    found_movies = search_movies_by_title(search_title)
    if found_movies:
        st.header(f"Filmes encontrados con '{search_title}'")
        st.dataframe(pd.DataFrame(found_movies))
    else:
        st.warning("No se encontraron filmes con ese título.")

# Filtrar y mostrar filmes por director
if btn_filter and selected_director:
    director_movies = filter_movies_by_director(selected_director)
    st.header(f"Filmes dirigidos por {selected_director} ({len(director_movies)} encontrados)")
    st.dataframe(pd.DataFrame(director_movies))

# Agregar nuevo filme
if btn_add and new_title and new_director and new_genre and new_year:
    add_movie(new_title, new_director, new_genre, new_year)
