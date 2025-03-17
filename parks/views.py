from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponse  # noqa: F401  # Ignore "imported but unused"
from .models import DogRun
import os
from django.conf import settings

import folium
from folium.plugins import MarkerCluster
import json

from .utilities import folium_cluster_styling

from django.shortcuts import render, redirect
from django.contrib.auth import login
from .forms import RegisterForm
from django.contrib.auth import login

def register_view(request):
    if request.method == "POST":
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()  # Save user
            login(request, user)  # Log in the user immediately
            request.session.save()  # Ensure session is updated
            return redirect("home")  # Redirect to homepage
    else:
        form = RegisterForm()
    
    return render(request, "parks/register.html", {"form": form})

def park_list(request):
    parks = DogRun.objects.all()  # Fetch all dog runs from the database
    return render(request, "parks/park_list.html", {"parks": parks})


def home_view(request):
    return render(request, "parks/home.html")


def map(request):

    NYC_LAT_AND_LONG = (40.730610, -73.935242)
    # Create map centered on NYC
    m = folium.Map(location=NYC_LAT_AND_LONG, zoom_start=11)

    icon_create_function = folium_cluster_styling("rgb(0, 128, 0)")

    marker_cluster = MarkerCluster(icon_create_function=icon_create_function).add_to(m)

    # Currently, this data is not in DB.
    # just saved in file, so we hardcode to import it here
    coordinates = os.path.join(settings.BASE_DIR, "new_coordinates.json")
    with open(coordinates, "r") as file:
        coor_dict = json.load(file)

    # Fetch all dog runs from the database
    parks = DogRun.objects.all()

    # Mark every park on the map
    for park in parks:
        park_name = park.name

        # Some park names in the original dataset
        # does not refer to 1 park, but an area
        # of parks. For now just ignore them because there
        # is no google_name for them yet
        if park_name not in coor_dict:
            continue

        coordinates = coor_dict[park_name]

        folium.Marker(
            location=coordinates,
            icon=folium.Icon(icon="dog", prefix="fa", color="green"),
            popup=folium.Popup(park_name, max_width=200),
        ).add_to(marker_cluster)

    # represent map as html
    context = {"map": m._repr_html_()}
    return render(request, "parks/map.html", context)


def park_and_map(request):
    # Get filter values from GET request
    filter_value = request.GET.get("filter", "")
    accessible_value = request.GET.get("accessible", "")

    # Apply filters based on the selected values
    parks = DogRun.objects.all().order_by("id")
    if filter_value:
        parks = parks.filter(dogruns_type__icontains=filter_value)

    if accessible_value:
        parks = parks.filter(accessible=accessible_value)

    NYC_LAT_AND_LONG = (40.712775, -74.005973)

    # Create map centered on NYC
    # f = folium.Figure(height="100")
    m = folium.Map(location=NYC_LAT_AND_LONG, zoom_start=11)

    icon_create_function = folium_cluster_styling("rgb(0, 128, 0)")
    marker_cluster = MarkerCluster(icon_create_function=icon_create_function).add_to(m)

    coordinates = os.path.join(settings.BASE_DIR, "new_coordinates.json")
    with open(coordinates, "r") as file:
        coor_dict = json.load(file)

    # Mark every park on the map
    for park in parks:
        park_name = park.name
        if park_name not in coor_dict:
            continue

        if park_name in coor_dict:
            folium.Marker(
                location=coor_dict[park_name],
                icon=folium.Icon(icon="dog", prefix="fa", color="green"),
                popup=folium.Popup(park_name, max_width=200),
            ).add_to(marker_cluster)

    m = m._repr_html_()
    m = m.replace(
        '<div style="width:100%;">'
        + '<div style="position:relative;width:100%;height:0;padding-bottom:60%;">',
        '<div style="width:100%; height:100%;">'
        + '<div style="position:relative;width:100%;height:100%;>',
        1,
    )

    # Render map as HTML
    return render(request, "parks/combined_view.html", {"parks": parks, "map": m})


def park_detail(request, id):
    park = get_object_or_404(DogRun, id=id)  # Get the park by id

    if request.method == "POST" and request.FILES.get("image"):

        if park.image:
            if os.path.exists(park.image.path):
                os.remove(park.image.path)  # Delete the existing image file
                print(f"Deleted old image: {park.image.name}")
        park.image = request.FILES["image"]
        park.save()
        return redirect("park_detail", id=park.id)

    return render(request, "parks/park_detail.html", {"park": park})


def contact_view(request):
    return render(request, "parks/contact.html")
