from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.shortcuts import render, get_object_or_404, redirect
from parks.models import Review, ImageReport, ReviewReport
from django.db.models import Count, Min, Max
from django.contrib import messages
from django.utils import timezone
from django.http import HttpResponseNotAllowed


@login_required
def dashboard(request):
    # Deny if user not admin
    if not request.user.is_staff:
        raise PermissionDenied

    reported_reviews = (
        Review.objects.annotate(
            report_count=Count("reports"),
            first_reported=Min("reports__reported_at"),
            latest_reported=Max("reports__reported_at"),
        )
        .filter(report_count__gt=0)
        .select_related("user", "park")
        .prefetch_related("images", "reports")
    )

    image_reports = ImageReport.objects.select_related("image", "user")

    return render(
        request,
        "moderation/dashboard.html",
        {
            "reported_reviews": reported_reviews,
            "image_reports": image_reports,
        },
    )


@login_required
def moderation_action(request):
    # Deny if not admin
    if not request.user.is_staff:
        raise PermissionDenied

    if request.method != "POST":
        return HttpResponseNotAllowed(["POST"])

    if request.method == "POST":
        action = request.POST.get("action")
        review = get_object_or_404(Review, id=request.POST.get("review_id"))
        reports = ReviewReport.objects.filter(review=review)

        if action == "remove_review" and review.is_removed:
            messages.warning(request, "This review is already removed.")
        elif action == "dismiss_report" and not reports.exists():
            messages.warning(request, "There are no reports to dismiss.")

        if action == "remove_review":
            review.is_removed = True
            review.removed_at = timezone.now()
            review.removed_by = request.user
            review.save()
            # Remove all reports
            reports.delete()
            messages.success(request, "Review removed.")

        elif action == "dismiss_report":
            review.is_removed = False
            review.removed_at = None
            review.removed_by = None
            review.save()
            reports.delete()
            messages.success(request, "Report Dismissed.")
        else:
            messages.error(request, "Invalid Action")

    return redirect("moderation_dashboard")
