from fastapi import FastAPI
from geopy.geocoders import Nominatim
from models.address import Address
from dotenv import load_dotenv
import os
import json
import requests 
import redis
import logging
from openai import OpenAI

# Load variables from .env file
load_dotenv()

app = FastAPI()
redis_instance = redis.Redis(host=os.getenv("REDIS_HOST"), port=os.getenv("REDIS_PORT"), decode_responses=True)
logger = logging.getLogger(__name__)
logging.basicConfig(
    format='%(asctime)s %(levelname)-8s %(message)s',
    level=logging.INFO,
    datefmt='%Y-%m-%d %H:%M:%S',
    filename="map-fastapi.log"
)

#def geocode (nominatim) with cache
@app.get("/geocode/{city}")
def geocode(city:str) -> Address:
    
    redis_key_geocode = f"geocode_{city}"

    address = redis_instance.get(redis_key_geocode)

    if address:
        logger.info(f"Result geocode from Cache for city {city}")
        address = json.loads(address)
    else: 
        logger.info(f"Result geocode from Nominatim for city {city}")
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
        logger.info(f"Result nearby_places from Cache for lat:{latitude}, lon:{longitude}, radius:{radius}, nb_results:{nb_results}")
        response_places = json.loads(response_places)
    else: 
        logger.info(f"Result nearby_places from Google Nearby Places for lat:{latitude}, lon:{longitude}, radius:{radius}, nb_results:{nb_results}")
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

    redis_key_infos = f"infos_{city}"

    response_infos = redis_instance.get(redis_key_infos)

    if response_infos:
        logger.info(f"Result city_infos from Cache for city {city}")
        response_infos = json.loads(response_infos)
    else: 
        logger.info(f"Result city_infos from OpenAI for city {city}")
        client_openai = OpenAI()

    # DO:
    # - Get people number
    # - Get average of noise pollution
    # - Get list of schools by ages (maternelles, primaires, collèges, lycées, études supérieures)

    # GUIDELINES:
    # - Return response with a json key:value like {"people_number": 12000, "noise_pollution": 30, "schools": [{"primaires": [{"name": "école A", "type":"privée"}, {"name": "école B", "type":"publique"}]}]}
    # - Get Values of json in french
    
        system_message = """
    You are a professional researcher 

    DO:
    - Get people number
    - Get average environmental noise level Lden in dB(A) from the strategic noise maps

    GUIDELINES:
    - Return response with a json key:value like {"people_number": 12000, "noise_pollution": 30}
    - Get values of people number and noise pollution in integer or float

    """

        response = client_openai.responses.create(
            model="gpt-5",
            tools=[{"type": "web_search"}],
            reasoning={"effort": "low"},
            instructions=system_message,
            input=f"Get informations of {city}"
        )

        redis_instance.set(redis_key_infos, response.output_text)
        response_infos = json.loads(response.output_text)

    return response_infos
