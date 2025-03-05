from django.shortcuts import render
from django.http import HttpResponse
from django.shortcuts import render
from .models import DogRun

import os
from django.conf import settings

import folium
import json

def park_list(request):
    parks = DogRun.objects.all()  # Fetch all dog runs from the database
    return render(request, "parks/park_list.html", {"parks": parks})

def map(request):

    NYC_LAT_AND_LONG = (40.730610, -73.935242)
    # Create map centered on NYC
    m = folium.Map(location=NYC_LAT_AND_LONG, zoom_start=11) 

    # Currently, this data is not in DB. 
    # just saved in file, so we hardcode to import it here
    coordinates = os.path.join(settings.BASE_DIR, "coordinates.json")
    with open(coordinates, "r") as file:
        coor_dict = json.load(file)
    

    # Fetch all dog runs from the database
    parks = DogRun.objects.all() 

    # Mark every park on the map
    for park in parks:
        park_name = park.name
        coordinates = coor_dict[park_name]

        folium.Marker(
            location=coordinates,
            popup=park_name,
        ).add_to(m)

    # represent map as html
    context = {'map': m._repr_html_()}
    return render(request, "parks/map.html", context)


