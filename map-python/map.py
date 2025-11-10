import streamlit as st
import folium
from geopy.geocoders import Nominatim
from streamlit_folium import st_folium
import requests 
import pandas as pd
import redis
import json


# - Use env variables 
# - Clean code
# - Call IA to get some infos on cities
# - Defined criterias with notation
# - Calculed ponderation
# - Check/Use FastAPI
# - Check/Use pytest/logging
# - Check/Use Django
# - Send to Github


geolocator = Nominatim(user_agent="MAP")
redis_instance = redis.Redis(host='redis', port=6379, decode_responses=True)

def map_search():
    # Get coordinates for a location
    location = geolocator.geocode(city)
    #reverse = geolocator.reverse(query=(location.latitude, location.longitude), exactly_one=False, zoom=10)

    if location :

        st.session_state["address"] = location.address
        st.session_state["latitude"] = location.latitude
        st.session_state["longitude"] = location.longitude
        st.session_state["location"] = location.raw
        st.session_state["radius"] = radius
        st.session_state["nb_results"] = nb_results

        redis_key_places = f"places_{st.session_state['latitude']}_{st.session_state['longitude']}_{st.session_state['radius']}_{st.session_state['nb_results']}"
        
        cache_places = redis_instance.get(redis_key_places)
        if cache_places :
            st.session_state["cities"] = json.loads(cache_places)
            st.session_state["places_from_cache"] = True
        else :
            #Get nearby places for coordinates and distance from cache or api google
            url_nearby_places = "https://places.googleapis.com/v1/places:searchNearby"
            data_nearby_places = {
                "includedPrimaryTypes":["locality"],
                "maxResultCount": st.session_state['nb_results'],
                "rankPreference": "DISTANCE",
                "locationRestriction":
                {
                    "circle":
                    {
                        "center":
                        {
                            "latitude": st.session_state['latitude'],
                            "longitude": st.session_state['longitude']
                        },
                        "radius": st.session_state['radius'] * 1000,
                    }
                },
            }
            headers_nearby_places = {
                'X-Goog-Api-Key': 'AIzaSyCeZX5CzEM17UxbVDhGRXwdvJ6uu0cpYh0',
                'Accept': 'application/json',
                'Content-Type': 'application/json',
                'X-Goog-FieldMask': 'places.displayName,places.formattedAddress,places.location,places.addressDescriptor'
            }

            response = requests.post(url_nearby_places, json=data_nearby_places, headers=headers_nearby_places)
        
            if response.ok : 
                redis_instance.set(redis_key_places, json.dumps(response.json()["places"]))
                st.session_state["cities"] = response.json()["places"]
                st.session_state["places_from_cache"] = False
                
    #if reverse :
        #st.session_state["cities"] = reverse
        




st.set_page_config(page_title="MAP", layout="wide")
st.title("Résultats")
st.subheader("Carte", divider="gray")

#Right sidebar
st.sidebar.header("Recherche")
city = st.sidebar.text_input("Ville", "Bruz, France")
radius = st.sidebar.slider("Rayon", 0, 50, 10)
nb_results = st.sidebar.slider("Nombre de résultats", 0, 20, 10)
button = st.sidebar.button("Rechercher", on_click=map_search)

if "address" in st.session_state :

    #Display infos for location
    st.sidebar.text(f"Infos : {st.session_state['address']}")
    st.sidebar.text(f"Latitude : {st.session_state['latitude']}")
    st.sidebar.text(f"Longitude : {st.session_state['longitude']}")
    st.sidebar.text(f"Raw : {st.session_state['location']}")

    #Display Map with marker
    map = folium.Map(location=(st.session_state["latitude"], st.session_state["longitude"]), zoom_start=12)

    folium.Marker(
        location=[st.session_state["latitude"], st.session_state["longitude"]],
        popup=st.session_state['address'],
    ).add_to(map)

    if "cities" in st.session_state :

        #Format list nearby places and display markers
        data_cities = []
        for city_item in st.session_state['cities']:
            
            if "displayName" in city_item and "text" in city_item["displayName"] and "location" in city_item:
                data_cities.append({
                    "name": city_item['displayName']['text'],
                    "latitude": city_item['location']['latitude'],
                    "longitude": city_item['location']['longitude']
                })
                st.session_state["data_cities"] = data_cities

                if st.session_state["location"]["name"] != city_item['displayName']['text']:
                    folium.Marker(
                        location=[city_item['location']['latitude'], city_item['location']['longitude']],
                        popup=city_item['displayName']['text'],
                        icon=folium.Icon(color="green")
                    ).add_to(map)

    data = st_folium(map, use_container_width=True)
    #st.text(f"Données : {data}") 


#Display list nearby places
st.subheader(f"Liste", divider="gray")

if "places_from_cache" in st.session_state: 
    st.text(st.session_state['places_from_cache'])

if "data_cities" in st.session_state:
    config = {
        'name' : st.column_config.TextColumn('Nom', width='large'),
        'latitude' : st.column_config.NumberColumn('Latitude'),
        'longitude' : st.column_config.NumberColumn('Longitude')
    }
    df = pd.DataFrame(data=st.session_state["data_cities"], columns=['name', 'latitude', 'longitude'])
    st.dataframe(df, use_container_width=True, hide_index=True, column_config=config)
