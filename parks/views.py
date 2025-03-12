from django.shortcuts import render, get_object_or_404, redirect
from django.core.files.storage import FileSystemStorage
from .models import DogRun, Review
from django.http import HttpResponse  # noqa: F401  # Ignore "imported but unused"
#from .models import DogRun
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
    return render(
        request, "parks/combined_view.html", {"parks": parks, "map": m._repr_html_()}
    )

"""
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
"""


def park_detail(request, id):
    park = get_object_or_404(DogRun, id=id)  # get park info

    if request.method == "POST":
        # get review content
        review_text = request.POST.get("text", "").strip()
        rating_value = request.POST.get("rating", "").strip()

        # make sure rating not empty，also legal rating numbers
        if not rating_value.isdigit():
            return render(
                request,
                "parks/park_detail.html",
                {
                    "park": park,
                    "error_message": "Please select a valid rating!"
                }
            )

        # transfer rating
        rating = int(rating_value)
        if rating < 1 or rating > 5:
            return render(
                request,
                "parks/park_detail.html",
                {
                    "park": park,
                    "error_message": "Rating must be between 1 and 5 stars!"
                }
            )

        # create and store Review 
        Review.objects.create(park=park, text=review_text, rating=rating)

        return redirect("park_detail", id=park.id)  # refresh the page

    # get all reviews
    reviews = park.reviews.all()

    return render(request, "parks/park_detail.html", {"park": park, "reviews": reviews})
