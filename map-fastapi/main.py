from fastapi import FastAPI
from geopy.geocoders import Nominatim
from models.address import Address
from dotenv import load_dotenv
import os
import json
import requests 
from openai import OpenAI

# Load variables from .env file
load_dotenv()

app = FastAPI()

#def geocode (nominatim) with cache
@app.get("/geocode/{city}")
def geocode(city:str) -> Address:

    # Get coordinates for a location
    geolocator = Nominatim(user_agent="MAP")
    location = geolocator.geocode(city)
    return Address(
        locality = city,
        address = location.address,
        latitude = location.latitude,
        longitude = location.longitude,
        infos = location.raw
    )


#def nearby_places (googleapi) with cache
@app.get("/nearby_places/")
def nearby_places(latitude: float, longitude: float, radius: int, nb_results: int) -> list[Address]:

    places = []

    #Get nearby places for coordinates and distance from cache or api google
    url_nearby_places = os.getenv("GOOGLE_NEARBY_PLACES_URL")
    data_nearby_places = {
        "includedPrimaryTypes":["locality"],
        "maxResultCount": nb_results,
        "rankPreference": "DISTANCE",
        "locationRestriction":
        {
            "circle":
            {
                "center":
                {
                    "latitude": latitude,
                    "longitude": longitude
                },
                "radius": radius * 1000,
            }
        },
    }
    headers_nearby_places = {
        'X-Goog-Api-Key': os.getenv("GOOGLE_API_KEY"),
        'Accept': 'application/json',
        'Content-Type': 'application/json',
        'X-Goog-FieldMask': 'places.displayName,places.formattedAddress,places.location,places.addressDescriptor'
    }

    response = requests.post(url_nearby_places, json=data_nearby_places, headers=headers_nearby_places)

    if response.ok : 
        
        response_places = response.json()["places"]
        if response_places :
            for place in response_places:
                places.append(
                    Address(
                        locality = place["displayName"]["text"],
                        address = place["formattedAddress"],
                        latitude = place["location"]["latitude"],
                        longitude = place["location"]["longitude"],
                        infos = place
                    )
                )

    return places

#def city_infos (openai) with cache
@app.get("/city_infos/{city}")
def city_infos(city:str):
    client_openai = OpenAI()
    response = client_openai.responses.create(
        model="gpt-5",
        input="Get people number of {city}"
    )
    return response.output_text
