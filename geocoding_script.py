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

API_KEY = "REMOVED"  # running this script without key will not work
gmaps = googlemaps.Client(key=API_KEY)

# old
# dog_runs_json = "runs.json"  # JSON file with dog run details
# output_file = "coordinates.json"  # Output file

dog_runs_json = "new_runs.json"
output_file = "new_coordinates.json"

with open(dog_runs_json, "r") as file:
    dog_runs = json.load(file)

name_to_coordinates = {}

found = 0
not_found = 0
nf = set()
continued = 0
cs = set()

for run in dog_runs:
    park_name = run["Name"]
    google_name = run["Google_Name"]

    if google_name is None or google_name == "":
        continued += 1
        cs.add(park_name)
        continue

    result = gmaps.geocode(
        google_name, components={"locality": "New York", "country": "US"}
    )

    if result:
        found += 1
        location = result[0]["geometry"]["location"]
        name_to_coordinates[park_name] = (location["lat"], location["lng"])
    else:
        not_found += 1
        print("Not Found")
        nf.add((park_name, google_name))

    time.sleep(0.1)  # 100ms delay to avoid hitting the rate limit

print(f"Found: {found}")
print(f"Not Found: {not_found}")
print(f"Continued: {continued}")
print(f"NF: {nf}")
print(f"CS: {cs}")

# Currently just saving to a file
with open(output_file, "w") as file:
    json.dump(name_to_coordinates, file, indent=4)

print(f"Saved {len(name_to_coordinates)} locations to {output_file}")
