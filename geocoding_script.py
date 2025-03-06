"""
    This script takes the dog run data set and runs the park name
    through Google Maps Geocoding API to get the latitude and 
    longitude information for the dog run.

    It puts it in a Python dict where the name is the key and the value
    is a tuple of the coordinates, saves this to a coordinates.json
"""

import googlemaps
import json
import time 

API_KEY = "REMOVED_FOR_SAFETY" # running this script without key will not work
gmaps = googlemaps.Client(key=API_KEY)

dog_runs_json = "runs.json"  # JSON file with dog run details
output_file = "coordinates.json"  # Output file

with open(dog_runs_json, "r") as file:
    dog_runs = json.load(file)

name_to_coordinates = {}


for run in dog_runs:
    park_name = run["Name"]

    result = gmaps.geocode(park_name, components={"locality": "New York", "country": "US"})

    if result:
        print(park_name)
        location = result[0]["geometry"]["location"]
        print(f"Latitude: {location['lat']}, Longitude: {location['lng']}")
        name_to_coordinates[park_name] = (location['lat'], location['lng'])
    else:
        print("Not Found")

    time.sleep(0.1)  # 100ms delay to avoid hitting the rate limit


# Currently just saving to a file
with open(output_file, "w") as file:
    json.dump(name_to_coordinates, file, indent=4)

print(f"Saved {len(name_to_coordinates)} locations to {output_file}")