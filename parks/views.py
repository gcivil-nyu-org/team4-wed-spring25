from django.shortcuts import render
from django.shortcuts import get_object_or_404
from django.shortcuts import redirect
from django.http import (  # noqa: F401  # Ignore "imported but unused"
    HttpResponseForbidden,
    HttpResponse,
    JsonResponse,
)
from django.db.models import OuterRef, Subquery, CharField, Q, Avg, Count
from django.db.models.functions import Cast
from .models import (
    DogRunNew,
    Review,
    ParkImage,
    ReviewReport,
    ImageReport,
    ParkPresence,
)
from django.forms.models import model_to_dict
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from .forms import RegisterForm

import json
import datetime
from django.contrib import messages
from django.utils import timezone
from django.utils.timezone import now, localtime
from django.views.decorators.http import require_POST
from django.views.decorators.cache import never_cache
from datetime import timedelta


@login_required
@require_POST
def checkin_view(request):
    data = json.loads(request.body)
    park_id = data.get("park_id")
    park = get_object_or_404(DogRunNew, id=park_id)

    # Remove existing 'current' check-ins from other parks
    ParkPresence.objects.filter(user=request.user, status="current").exclude(
        park=park
    ).delete()

    # Check in to this park
    presence, created = ParkPresence.objects.update_or_create(
        user=request.user,
        park=park,
        defaults={"status": "current", "time": timezone.now()},
    )

    return JsonResponse({"status": "checked in", "new": created})


@login_required
@require_POST
def bethere_view(request):
    try:
        data = json.loads(request.body)
        park_id = data.get("park_id")
        time_str = data.get("time")  # e.g. "17:30"

        if not park_id or not time_str:
            return JsonResponse({"error": "Missing park_id or time"}, status=400)

        # Parse and validate time
        try:
            arrival_time = datetime.datetime.strptime(time_str, "%H:%M").time()
        except ValueError:
            return JsonResponse({"error": "Invalid time format"}, status=400)

        current_datetime = now()
        today = current_datetime.date()
        arrival_datetime = timezone.make_aware(
            datetime.datetime.combine(today, arrival_time)
        )

        if arrival_datetime < current_datetime:
            return JsonResponse({"error": "Cannot select a past time"}, status=400)

        park = get_object_or_404(DogRunNew, id=park_id)

        # ✅ Save the full datetime, not just the time
        presence, created = ParkPresence.objects.update_or_create(
            user=request.user,
            park=park,
            defaults={"status": "On their way", "time": arrival_datetime},
        )

        formatted_time = arrival_datetime.strftime("%I:%M %p")
        return JsonResponse({"status": "on their way", "time": formatted_time})

    except Exception as e:
        import traceback

        print(traceback.format_exc())
        return JsonResponse({"error": str(e)}, status=500)


def expire_old_checkins():
    expiration_time = timezone.now() - timedelta(hours=1)
    ParkPresence.objects.filter(status="current", time__lt=expiration_time).delete()


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


@never_cache
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


@never_cache
def park_detail(request, slug, id):
    park = get_object_or_404(DogRunNew, id=id)
    images = ParkImage.objects.filter(park=park)
    reviews = park.reviews.all()
    average_rating = reviews.aggregate(Avg("rating"))["rating__avg"]

    # Clean up expired "On their way" entries
    now = localtime()
    # Call the function to expire old check-ins
    expire_old_checkins()

    ParkPresence.objects.filter(park=park, status="On their way", time__lt=now).delete()

    # Updated counts after cleanup
    current_count = ParkPresence.objects.filter(park=park, status="current").count()
    on_the_way_count = ParkPresence.objects.filter(
        park=park, status="On their way", time__isnull=False, time__gte=now
    ).count()

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
                        "current_count": current_count,
                        "on_the_way_count": on_the_way_count,
                    },
                )

            review = Review.objects.create(
                park=park,
                text=review_text if review_text else "",
                rating=rating,
                user=request.user,
            )
            images = request.FILES.getlist("images")
            ALLOWED_IMAGE_TYPES = ["image/jpeg", "image/png", "image/webp"]

            invalid_type = any(
                img.content_type not in ALLOWED_IMAGE_TYPES for img in images
            )

            if invalid_type:
                messages.error(request, "Only JPEG, PNG, or WebP images are allowed.")
                review.delete()
                return redirect("park_detail", slug=park.slug, id=park.id)

            MAX_IMAGE_SIZE = 5 * 1024 * 1024  # 5 MB

            invalid_images = [img for img in images if img.size > MAX_IMAGE_SIZE]

            if invalid_images:
                messages.error(request, "Each image must be under 5 MB.")
                review.delete()
                return redirect("park_detail", slug=park.slug, id=park.id)

            # Save valid images
            for image in images:
                ParkImage.objects.create(
                    park=park, image=image, review=review, user=request.user
                )

            messages.success(request, "Your review was submitted successfully!")
            return redirect("park_detail", slug=park.slug, id=park.id)

        elif form_type == "check_in":
            ParkPresence.objects.create(
                user=request.user,
                park=park,
                status="current",
                time=now,
            )

        elif form_type == "be_there_at":
            time_str = request.POST.get("time")
            try:
                arrival_time = timezone.datetime.combine(
                    now.date(), timezone.datetime.strptime(time_str, "%H:%M").time()
                )
                arrival_time = timezone.make_aware(
                    arrival_time
                )  # Make it timezone aware
            except (ValueError, TypeError):
                arrival_time = None

            if arrival_time and arrival_time >= now:
                ParkPresence.objects.create(
                    user=request.user,
                    park=park,
                    status="on_the_way",
                    time=arrival_time,
                )

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
            "current_count": current_count,
            "on_the_way_count": on_the_way_count,
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
