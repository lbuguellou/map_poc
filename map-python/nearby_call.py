import requests

url_nearby_places = "https://places.googleapis.com/v1/places:searchNearby"
data_nearby_places = {
    "includedPrimaryTypes":["locality"],
    "maxResultCount":10,
    "locationRestriction":
    {
        "circle":
        {
            "center":
            {
                "latitude":48.0245814,
                "longitude":-1.7471629
            },
            "radius":10000
        }
    }
}
headers_nearby_places = {
    'X-Goog-Api-Key': 'AIzaSyCeZX5CzEM17UxbVDhGRXwdvJ6uu0cpYh0',
    'Accept': 'application/json',
    'Content-Type': 'application/json',
    'X-Goog-FieldMask': 'places.displayName,places.formattedAddress,places.location'
}

response = requests.post(url_nearby_places, json=data_nearby_places, headers=headers_nearby_places)
print(response.text)