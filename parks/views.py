from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponse  # noqa: F401  # Ignore "imported but unused"
from django.db.models import OuterRef, Subquery, CharField
from django.db.models.functions import Cast
from .models import DogRunNew, Review, ParkImage, ReviewReport, ImageReport
from django.forms.models import model_to_dict

import folium
from folium.plugins import MarkerCluster

from .utilities import folium_cluster_styling

from django.contrib.auth import login
from .forms import RegisterForm
import json
from django.db.models import Q  # Import Q for complex queries

from django.contrib.auth.decorators import login_required
from django.db.models import Avg
from django.http import HttpResponseForbidden


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
    query = request.GET.get("query", "")
    parks = DogRunNew.objects.all()  # Fetch all dog runs from the database

    if query:
        parks = parks.filter(
            Q(name__icontains=query)
            | Q(google_name__icontains=query)
            | Q(zip_code__icontains=query)
        )

    return render(request, "parks/park_list.html", {"parks": parks, "query": query})


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
    query = request.GET.get("query", "").strip()
    filter_value = request.GET.get("filter", "").strip()
    accessible_value = request.GET.get("accessible", "").strip()
    borough_value = request.GET.get("borough", "").strip().upper()

    thumbnail = ParkImage.objects.filter(park_id=OuterRef("pk")).values("image")[:1]

    # Fetch all dog runs from the database
    parks = (
        DogRunNew.objects.all()
        .order_by("id")
        .prefetch_related("images")
        .annotate(thumbnail_url=Cast(Subquery(thumbnail), output_field=CharField()))
    )

    # Search by ZIP, name, or Google name
    if query:
        parks = parks.filter(
            Q(name__icontains=query)
            | Q(google_name__icontains=query)
            | Q(zip_code__icontains=query)
        )

    # Filter by park type (e.g., "Off-Leash")
    if filter_value:
        parks = parks.filter(dogruns_type__iexact=filter_value)

    # Filter by accessibility only if explicitly set to "True" or "False"
    if accessible_value == "True":
        parks = parks.filter(accessible=True)
    elif accessible_value == "False":
        parks = parks.filter(accessible=False)

    if borough_value:
        parks = parks.filter(borough=borough_value)
    # Convert parks to JSON (for JS use)
    parks_json = json.dumps(list(parks.values()))

    # Render the template
    return render(
        request,
        "parks/combined_view.html",
        {
            "parks": parks,
            "parks_json": parks_json,
            "query": query,
            "selected_type": filter_value,
            "selected_accessible": accessible_value,
            "selected_borough": borough_value,
        },
    )


def park_detail(request, id):
    park = get_object_or_404(DogRunNew, id=id)
    images = ParkImage.objects.filter(park=park)
    reviews = park.reviews.all()
    average_rating = reviews.aggregate(Avg("rating"))["rating__avg"]

    if request.user.is_authenticated and request.method == "POST":
        form_type = request.POST.get("form_type")

        if form_type == "upload_image" and request.FILES.getlist("images"):
            for image in request.FILES.getlist("images"):
                ParkImage.objects.create(park=park, image=image, user=request.user)
            return redirect("park_detail", id=park.id)

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
                        "average_rating": average_rating,
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
                        "average_rating": average_rating,
                    },
                )

            Review.objects.create(
                park=park, text=review_text, rating=rating, user=request.user
            )
            return redirect("park_detail", id=park.id)
        # report reviews
        elif form_type == "report_review":
            if request.user.is_authenticated:
                review_id = request.POST.get("review_id")
                reason = request.POST.get("reason", "").strip()
            if review_id and reason:
                review = get_object_or_404(Review, id=review_id)
                ReviewReport.objects.create(
                    review=review, reported_by=request.user, reason=reason
                )
                return redirect("park_detail", id=park.id)

    park_json = json.dumps(model_to_dict(park))

    return render(
        request,
        "parks/park_detail.html",
        {
            "park": park,
            "images": images,
            "reviews": reviews,
            "park_json": park_json,
            "average_rating": average_rating,
        },
    )


@login_required
def delete_review(request, review_id):
    review = get_object_or_404(Review, id=review_id)
    if request.user == review.user:
        review.delete()
        return redirect("park_detail", id=review.park.id)
    else:
        return HttpResponseForbidden("You are not allowed to delete this review.")


@login_required
def delete_image(request, image_id):
    image = get_object_or_404(ParkImage, id=image_id)
    if image.user == request.user:
        park_id = image.park.id
        image.delete()
        return redirect("park_detail", id=park_id)
    return HttpResponseForbidden("You are not allowed to delete this image.")


def contact_view(request):
    return render(request, "parks/contact.html")


@login_required
def report_image(request, image_id):
    image = get_object_or_404(ParkImage, id=image_id)
    if request.method == "POST":
        reason = request.POST.get("reason", "").strip()
        if reason:
            ImageReport.objects.create(user=request.user, image=image, reason=reason)
            return redirect("park_detail", id=image.park.id)
    return redirect("park_detail", id=image.park.id)
