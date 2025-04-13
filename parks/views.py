from django.shortcuts import render, get_object_or_404, redirect
from django.http import (  # noqa: F401  # Ignore "imported but unused"
    HttpResponseForbidden,
    HttpResponse,
    HttpResponsePermanentRedirect,
)
from django.urls import reverse
from django.db.models import OuterRef, Subquery, CharField, Q, Avg, Count
from django.db.models.functions import Cast
from .models import DogRunNew, Review, ParkImage, ReviewReport, ImageReport
from django.forms.models import model_to_dict
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required

from .forms import RegisterForm

import json
from django.contrib import messages


def register_view(request):
    if request.method == "POST":
        form = RegisterForm(request.POST)
        if form.is_valid():
            # Save but don't commit yet
            user = form.save(commit=False)
            # If they chose Admin, mark them as staff
            if form.cleaned_data["role"] == "admin":
                user.is_staff = True
            user.save()

            # Log the user in immediately
            login(request, user)
            request.session.save()
            return redirect("home")
    else:
        form = RegisterForm()

    return render(request, "parks/register.html", {"form": form})


def home_view(request):
    return render(request, "parks/home.html")


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
        .annotate(
            thumbnail_url=Cast(Subquery(thumbnail), output_field=CharField()),
            average_rating=Avg("reviews__rating"),
            review_count=Count("reviews"),
        )
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


def park_detail(request, slug, id):
    park = get_object_or_404(DogRunNew, id=id)

    # Check slug, if incorrect, redirect to correct one
    if slug != park.slug:
        correct_url = reverse("park_detail", kwargs={"slug": park.slug, "id": park.id})
        return HttpResponsePermanentRedirect(correct_url)

    images = ParkImage.objects.filter(park=park)
    reviews = park.reviews.all()
    average_rating = reviews.aggregate(Avg("rating"))["rating__avg"]

    if request.user.is_authenticated and request.method == "POST":
        form_type = request.POST.get("form_type")

        if form_type == "submit_review":
            review_text = request.POST.get("text", "").strip()
            rating_value = request.POST.get("rating", "").strip()

            if not rating_value.isdigit():
                messages.error(request, "Please select a rating before submitting.")
                return redirect("park_detail", slug=park.slug, id=park.id)

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

            review = Review.objects.create(
                park=park,
                text=review_text if review_text else "",
                rating=rating,
                user=request.user,
            )

            images = request.FILES.getlist("images")

            if images:
                for image in images:
                    ParkImage.objects.create(
                        park=park, image=image, review=review, user=request.user
                    )

            messages.success(request, "Your review was submitted successfully!")
            return redirect("park_detail", slug=park.slug, id=park.id)
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
                messages.success(
                    request, "Your review report was submitted successfully."
                )
                return redirect("park_detail", slug=park.slug, id=park.id)

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
        messages.success(request, "You have successfully deleted the review!")
        return redirect("park_detail", slug=review.park.slug, id=review.park.id)
    else:
        return HttpResponseForbidden("You are not allowed to delete this review.")


@login_required
def delete_image(request, image_id):
    image = get_object_or_404(ParkImage, id=image_id)
    if image.user == request.user:
        park_id = image.park.id
        image.delete()
        messages.success(request, "You have successfully deleted the image!")
        return redirect("park_detail", slug=image.park.slug, id=park_id)
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
            messages.success(request, "You have successfully reported the image!")
            return redirect("park_detail", slug=image.park.slug, id=image.park.id)
    return redirect("park_detail", slug=image.park.slug, id=image.park.id)
