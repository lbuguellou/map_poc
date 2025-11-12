from fastapi import FastAPI
from geopy.geocoders import Nominatim
from models.address import Address
from dotenv import load_dotenv
import os
import json
import requests 
import redis
from openai import OpenAI

# Load variables from .env file
load_dotenv()

app = FastAPI()
redis_instance = redis.Redis(host=os.getenv("REDIS_HOST"), port=os.getenv("REDIS_PORT"), decode_responses=True)

#def geocode (nominatim) with cache
@app.get("/geocode/{city}")
def geocode(city:str) -> Address:
    
    redis_key_geocode = f"geocode_{city}"

    address = redis_instance.get(redis_key_geocode)

    if address:
        address = json.loads(address)
    else: 
        # Get coordinates for a location
        geolocator = Nominatim(user_agent="MAP")
        location = geolocator.geocode(city)
        address = {
            "address": location.address,
            "latitude": location.latitude,
            "longitude": location.longitude,
            "infos": location.raw
        }
        redis_instance.set(redis_key_geocode, json.dumps(address))
        
    return Address(
        locality = address["infos"]["name"],
        address = address["address"],
        latitude = address["latitude"],
        longitude = address["longitude"],
        infos = address["infos"]
    )


#def nearby_places (googleapi) with cache
@app.get("/nearby_places/")
def nearby_places(latitude: float, longitude: float, radius: int, nb_results: int) -> list[Address]:

    places = []
    redis_key_places = f"places_{latitude}_{longitude}_{radius}_{nb_results}"

    response_places = redis_instance.get(redis_key_places)

    if response_places:
        response_places = json.loads(response_places)
    else: 
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
                redis_instance.set(redis_key_places, json.dumps(response_places))
                
         
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

    redis_key_infos = f"city_infos_{city}"

    response_infos = redis_instance.get(redis_key_infos)

    if response_infos:
        response_infos = json.loads(response_infos)
    else: 
        client_openai = OpenAI()

        system_message = """
    You are a professional researcher 

    DO:
    - Get people number
    - Get list of schools by ages (maternelles, primaires, collèges, lycées, études supérieures)

    GUIDELINES:
    - Return response with a json key:value like {"people_number": 12000, "schools": [{"primaires": [{"name": "école A", "type":"privée"}, {"name": "école B", "type":"publique"}]}]}
    - Get Values of json in french

    """

        response = client_openai.responses.create(
            model="gpt-5",
            tools=[{"type": "web_search"}],
            reasoning={"effort": "medium"},
            instructions=system_message,
            input=f"Get informations of {city}"
        )

        redis_instance.set(redis_key_infos, response.output_text)
        response_infos = json.loads(response.output_text)

    return response_infos
