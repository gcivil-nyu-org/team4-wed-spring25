from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponse  # noqa: F401  # Ignore "imported but unused"
from .models import DogRunNew, Review, ParkImage

import folium
from folium.plugins import MarkerCluster

from .utilities import folium_cluster_styling

from django.contrib.auth import login
from .forms import RegisterForm


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
    parks = DogRunNew.objects.all()  # Fetch all dog runs from the database
    return render(request, "parks/park_list.html", {"parks": parks})


def home_view(request):
    return render(request, "parks/home.html")


def map(request):

    NYC_LAT_AND_LONG = (40.730610, -73.935242)
    # Create map centered on NYC
    m = folium.Map(location=NYC_LAT_AND_LONG, zoom_start=11)

    icon_create_function = folium_cluster_styling("rgb(0, 128, 0)")

    marker_cluster = MarkerCluster(icon_create_function=icon_create_function).add_to(m)

    # Fetch all dog runs from the database
    parks = DogRunNew.objects.all()

    # Mark every park on the map
    for park in parks:
        park_name = park.name

        folium.Marker(
            location=(park.latitude, park.longitude),
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

    # Fetch all dog runs from the database
    parks = DogRunNew.objects.all().order_by("id")

    if filter_value:
        parks = parks.filter(dogruns_type__icontains=filter_value)

    if accessible_value:
        parks = parks.filter(accessible=accessible_value)

    NYC_LAT_AND_LONG = (40.712775, -74.005973)

    # Create map centered on NYC
    # f = folium.Figure(height="100")
    m = folium.Map(location=NYC_LAT_AND_LONG, zoom_start=11)

    icon_create_function = folium_cluster_styling("rgba(0, 128, 0, 0.7)")
    marker_cluster = MarkerCluster(
        icon_create_function=icon_create_function,
        # maxClusterRadius=10,
    ).add_to(m)

    # Mark every park on the map
    for park in parks:
        park_name = park.name

        folium.Marker(
            location=(park.latitude, park.longitude),
            icon=folium.Icon(icon="dog", prefix="fa", color="green"),
            popup=folium.Popup(park_name, max_width=200),
        ).add_to(marker_cluster)

    m = m._repr_html_()
    m = m.replace(
        '<div style="width:100%;">'
        + '<div style="position:relative;width:100%;height:0;padding-bottom:60%;">',
        '<div style="width:100%; height:100vh;">'
        + '<div style="position:relative;width:100%;height:100%;>',
        1,
    )

    # Render map as HTML
    return render(request, "parks/combined_view.html", {"parks": parks, "map": m})


def park_detail(request, id):
    park = get_object_or_404(DogRunNew, id=id)  # Get the park by id
    images = ParkImage.objects.filter(
        park=park
    )  # Retrieve all images related to this park
    reviews = park.reviews.all()  # Retrieve all reviews related to this park

    if request.method == "POST":
        form_type = request.POST.get("form_type")  # Determine which form is submitted

        # Handle multiple image uploads
        if form_type == "upload_image" and request.FILES.getlist("images"):
            for image in request.FILES.getlist("images"):
                ParkImage.objects.create(park=park, image=image)
            return redirect("park_detail", id=park.id)  # Redirect after upload

        # Handle review submission separately
        elif form_type == "submit_review":
            review_text = request.POST.get("text", "").strip()
            rating_value = request.POST.get("rating", "").strip()

            if not rating_value.isdigit():
                return render(
                    request,
                    "parks/park_detail.html",
                    {
                        "park": park,
                        "images": images,
                        "reviews": reviews,
                        "error_message": "Please select a valid rating!",
                    },
                )

            rating = int(rating_value)
            if rating < 1 or rating > 5:
                return render(
                    request,
                    "parks/park_detail.html",
                    {
                        "park": park,
                        "images": images,
                        "reviews": reviews,
                        "error_message": "Rating must be between 1 and 5 stars!",
                    },
                )

            Review.objects.create(park=park, text=review_text, rating=rating)
            return redirect(
                "park_detail", id=park.id
            )  # Redirect after review submission

    return render(
        request,
        "parks/park_detail.html",
        {"park": park, "images": images, "reviews": reviews},
    )


def contact_view(request):
    return render(request, "parks/contact.html")
