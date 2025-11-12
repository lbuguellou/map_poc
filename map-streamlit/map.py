import streamlit as st
import folium
from streamlit_folium import st_folium
import requests 
import pandas as pd
import json
from dotenv import load_dotenv
import os


# - Use redis
# - Call IA to get some infos on cities
# - Defined criterias with notation
# - Calculed ponderation
# - Check/Use pytest/logging

# Load variables from .env file
load_dotenv()

def map_search():
    # Get coordinates for a location
    geocode = requests.get(f"{os.getenv('API_URL')}/geocode/{city}")
    location = geocode.json() 

    if location :
        st.session_state["address"] = city
        st.session_state["latitude"] = location["latitude"]
        st.session_state["longitude"] = location["longitude"]
        st.session_state["radius"] = radius
        st.session_state["nb_results"] = nb_results

        # Get nearby place for a location
        response_places = requests.get(f"{os.getenv('API_URL')}/nearby_places/?latitude={st.session_state['latitude']}&longitude={st.session_state['longitude']}&radius={st.session_state['radius']}&nb_results={st.session_state['nb_results']}")
        st.session_state["nearby_places"] = response_places.json()


st.set_page_config(page_title="MAP", layout="wide")
st.title("Résultats")
st.subheader("Carte", divider="gray")

#Right sidebar
st.sidebar.header("Recherche")
city = st.sidebar.text_input("Ville", "Bruz")
radius = st.sidebar.slider("Rayon", 0, 50, 10)
nb_results = st.sidebar.slider("Nombre de résultats", 0, 20, 10)
button = st.sidebar.button("Rechercher", on_click=map_search)

if "address" in st.session_state :
    #Display infos for location
    st.sidebar.text(f"Infos : {st.session_state['address']}")
    st.sidebar.text(f"Latitude : {st.session_state['latitude']}")
    st.sidebar.text(f"Longitude : {st.session_state['longitude']}")

    #Display Map with marker
    map = folium.Map(location=(st.session_state["latitude"], st.session_state["longitude"]), zoom_start=12)

    folium.Marker(
        location=[st.session_state["latitude"], st.session_state["longitude"]],
        popup=st.session_state['address'],
        icon=folium.Icon(color="blue")
    ).add_to(map)


    if "nearby_places" in st.session_state :
        for city_item in st.session_state['nearby_places']:
            if st.session_state["address"] != city_item['address']:
                folium.Marker(
                    location=[city_item['latitude'], city_item['longitude']],
                    popup=city_item['address'],
                    icon=folium.Icon(color="green")
                ).add_to(map)

    data = st_folium(map, use_container_width=True)


#Display list nearby places
st.subheader(f"Liste", divider="gray")

if "nearby_places" in st.session_state :
    config = {
        'address' : st.column_config.TextColumn('Nom', width='large'),
        'latitude' : st.column_config.NumberColumn('Latitude'),
        'longitude' : st.column_config.NumberColumn('Longitude')
    }
    df = pd.DataFrame(data=st.session_state["nearby_places"], columns=['address', 'latitude', 'longitude'])
    st.dataframe(df, width='stretch', hide_index=True, column_config=config)


