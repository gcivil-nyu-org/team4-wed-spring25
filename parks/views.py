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


from django.shortcuts import render
from .models import DogRun
import folium
import json
import os
from django.conf import settings

def park_and_map(request):
    # Get filter values from GET request
    filter_value = request.GET.get('filter', '')
    accessible_value = request.GET.get('accessible', '')

    # Apply filters based on the selected values
    parks = DogRun.objects.all()

    if filter_value:
        parks = parks.filter(dogruns_type__icontains=filter_value)
    
    if accessible_value:
        parks = parks.filter(accessible=accessible_value)

    NYC_LAT_AND_LONG = (40.730610, -73.935242)

    # Create map centered on NYC
    m = folium.Map(location=NYC_LAT_AND_LONG, zoom_start=11)

    coordinates = os.path.join(settings.BASE_DIR, "coordinates.json")
    with open(coordinates, "r") as file:
        coor_dict = json.load(file)

    # Mark every park on the map
    for park in parks:
        park_name = park.name
        if park_name in coor_dict:
            folium.Marker(
                location=coor_dict[park_name],
                popup=park_name,
            ).add_to(m)

    # Render map as HTML
    return render(request, "parks/combined_view.html", {"parks": parks, "map": m._repr_html_()})

