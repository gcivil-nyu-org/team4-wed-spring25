from django.shortcuts import render
from django.shortcuts import get_object_or_404
from django.shortcuts import redirect
from django.http import (  # noqa: F401  # Ignore "imported but unused"
    HttpResponseForbidden,
    HttpResponse,
    JsonResponse,
    HttpResponsePermanentRedirect,
)
from django.urls import reverse  # noqa: F401  # Ignore "imported but unused"
from django.db.models import OuterRef, Subquery, CharField, Q, Avg, Count, Prefetch
from django.db.models.functions import Cast
from .models import (
    DogRunNew,
    Review,
    ParkImage,
    ReviewReport,
    ImageReport,
    ParkPresence,
    Reply,
    ReplyReport,
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

    thumbnail = ParkImage.objects.filter(
        park_id=OuterRef("pk"), is_removed=False, review__is_removed=False
    ).values("image")[:1]

    # Fetch all dog runs from the database
    parks = (
        DogRunNew.objects.all()
        .order_by("id")
        .prefetch_related("images")
        .annotate(
            thumbnail_url=Cast(Subquery(thumbnail), output_field=CharField()),
            average_rating=Avg("reviews__rating", filter=Q(reviews__is_removed=False)),
            review_count=Count("reviews", filter=Q(reviews__is_removed=False)),
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
    # parks_json = json.dumps(list(parks.values()))

    parks_json = json.dumps(
        [
            {
                **model_to_dict(park),
                "thumbnail_url": park.thumbnail_url,
                "average_rating": park.average_rating,
                "review_count": park.review_count,
                "url": park.detail_page_url(),
            }
            for park in parks
        ]
    )

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
    if slug != park.slug:
        return HttpResponsePermanentRedirect(park.detail_page_url())

    images = ParkImage.objects.filter(
        park=park, is_removed=False, review__is_removed=False
    )

    # Prefetch only non-removed images for each review
    visible_images = Prefetch(
        "images",
        queryset=ParkImage.objects.filter(is_removed=False),
        to_attr="visible_images",
    )
    reviews = park.reviews.filter(is_removed=False).prefetch_related(visible_images)

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
                return redirect(park.detail_page_url())

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
            return redirect(park.detail_page_url())

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
        # report reviews
        elif form_type == "report_review":
            if request.user.is_authenticated:
                review_id = request.POST.get("review_id")
                reason = request.POST.get("reason", "").strip()

                if review_id and reason:
                    review = get_object_or_404(Review, id=review_id)

                    # prevent duplicate reports by the same user
                    exists = ReviewReport.objects.filter(
                        review=review, reported_by=request.user
                    ).exists()

                    if exists:
                        messages.error(
                            request, "You have already reported this review before."
                        )
                    else:
                        ReviewReport.objects.create(
                            review=review, reported_by=request.user, reason=reason
                        )
                        messages.success(
                            request, "Your review report was submitted successfully."
                        )
            else:
                messages.error(request, "You must be logged in to report a review.")

            return redirect(park.detail_page_url())

        elif form_type == "submit_reply":
            if request.user.is_authenticated:
                parent_review_id = request.POST.get("parent_review_id")
                reply_text = request.POST.get("reply_text", "").strip()
                parent_reply_id = request.POST.get("parent_reply_id")

                if parent_review_id and reply_text:
                    parent_review = get_object_or_404(Review, id=parent_review_id)

                    parent_reply = None
                    if parent_reply_id:
                        try:
                            parent_reply = Reply.objects.get(id=parent_reply_id)
                        except Reply.DoesNotExist:
                            parent_reply = None  # fallback: just attach to review

                    Reply.objects.create(
                        review=parent_review,
                        user=request.user,
                        text=reply_text,
                        parent_reply=parent_reply,
                    )

                    messages.success(request, "Reply submitted successfully!")
        return redirect(park.detail_page_url())

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
        return redirect(review.park.detail_page_url())
    else:
        return HttpResponseForbidden("You are not allowed to delete this review.")


@login_required
def delete_image(request, image_id):
    image = get_object_or_404(ParkImage, id=image_id)
    if image.user == request.user:
        image.delete()
        messages.success(request, "You have successfully deleted the image!")
        return redirect(image.park.detail_page_url())
    return HttpResponseForbidden("You are not allowed to delete this image.")


def contact_view(request):
    return render(request, "parks/contact.html")


@login_required
def report_image(request, image_id):
    image = get_object_or_404(ParkImage, id=image_id)

    if request.method == "POST":
        reason = request.POST.get("reason", "").strip()
        if reason:
            # Check if this user already reported this image
            already_reported = ImageReport.objects.filter(
                user=request.user, image=image
            ).exists()
            if already_reported:
                messages.error(request, "You have already reported this image before.")
            else:
                ImageReport.objects.create(
                    user=request.user, image=image, reason=reason
                )
                messages.success(request, "You have successfully reported the image!")
        return redirect(image.park.detail_page_url())

    return redirect(image.park.detail_page_url())


@login_required
def delete_reply(request, reply_id):
    reply = get_object_or_404(Reply, id=reply_id)
    if reply.user == request.user:
        reply.delete()
        messages.success(request, "Reply deleted successfully.")
    else:
        messages.error(request, "You can only delete your own replies.")
    return redirect(request.META.get("HTTP_REFERER", "/"))


@login_required
def report_reply(request, reply_id):
    if request.method == "POST":
        reason = request.POST.get("reason", "").strip()
        reply = get_object_or_404(Reply, id=reply_id)
        if reply.user != request.user and reason:
            ReplyReport.objects.create(reply=reply, user=request.user, reason=reason)
            messages.success(request, "Reply reported successfully.")
        else:
            messages.error(request, "You cannot report your own reply.")
    return redirect(request.META.get("HTTP_REFERER", "/"))
