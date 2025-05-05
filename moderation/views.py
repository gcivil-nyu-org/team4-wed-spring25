from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.shortcuts import render, get_object_or_404, redirect
from parks.models import (
    Review,
    ImageReport,
    ReviewReport,
    ParkImage,
    ParkInfoReport,
    ReplyReport,
    Reply,
)
from django.db.models import Count, Min, Max, Prefetch
from django.contrib import messages
from django.utils import timezone
from django.http import HttpResponseNotAllowed
from itertools import chain
from .forms import UserReportForm
from django.contrib.auth import get_user_model
from django.urls import reverse
from django.utils.http import url_has_allowed_host_and_scheme
from .models import ReportCategory
from django.utils.translation import gettext_lazy as _
from accounts.decorators import ban_protected
from moderation.models import UserReport
from profiles.models import UserProfile


@ban_protected
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
        .filter(report_count__gt=0, is_deleted=False)
        .select_related("user", "park")
        .prefetch_related(
            Prefetch("images", queryset=ParkImage.objects.filter(is_removed=False)),
            "reports",
        )
    )

    image_reports = (
        ParkImage.objects.annotate(
            report_count=Count("reports"),
            first_reported=Min("reports__created_at"),
            latest_reported=Max("reports__created_at"),
        )
        .filter(
            report_count__gt=0,
            is_removed=False,
            review__is_removed=False,
        )
        .select_related("user", "park", "review")
        .prefetch_related("reports")
    )

    reply_reports = (
        Reply.objects.annotate(
            report_count=Count("reports"),
            first_reported=Min("reports__created_at"),
            latest_reported=Max("reports__created_at"),
        )
        .filter(
            report_count__gt=0,
            # is_removed=False,
            review__is_removed=False,
        )
        .select_related("user", "review", "parent_reply")
        .prefetch_related("reports")
    )

    # Removed Content Object
    removed_reviews = (
        Review.objects.filter(is_removed=True, is_deleted=False)
        .select_related("user", "park")
        .prefetch_related(
            Prefetch("images", queryset=ParkImage.objects.filter(is_removed=False)),
            "reports",
        )
    )

    removed_images = ParkImage.objects.filter(is_removed=True).select_related(
        "user", "park", "review"
    )

    removed_replies = Reply.objects.filter(is_removed=True).select_related(
        "review", "user"
    )

    # Tag each item with its type
    tagged_reviews = [
        {"type": "review", "content": review, "removed_at": review.removed_at}
        for review in removed_reviews
    ]
    tagged_images = [
        {"type": "image", "content": image, "removed_at": image.removed_at}
        for image in removed_images
    ]
    tagged_replies = [
        {"type": "reply", "content": reply, "removed_at": reply.removed_at}
        for reply in removed_replies
    ]

    # Combine and sort by removed_at (descending)
    removed_content = sorted(
        chain(tagged_reviews, tagged_images, tagged_replies),
        key=lambda x: x["removed_at"],
        reverse=True,
    )

    # Aggregate user reports
    reported_user_data = (
        UserReport.objects.values("user_being_reported")
        .annotate(
            report_count=Count("report_id"),
            latest_reported=Max("reported_time"),
            first_reported=Min("reported_time"),
        )
        .order_by("-latest_reported")
    )

    reported_users = []
    for entry in reported_user_data:
        user = User.objects.get(id=entry["user_being_reported"])
        profile = UserProfile.objects.get(user=user)
        if profile.is_banned:
            continue
        reports = UserReport.objects.filter(user_being_reported=user).select_related(
            "reporter"
        )
        reported_users.append(
            {
                "user": user,
                "profile": profile,
                "report_count": entry["report_count"],
                "latest_reported": entry["latest_reported"],
                "first_reported": entry["first_reported"],
                "reports": reports,
            }
        )
    park_reports = ParkInfoReport.objects.select_related("park", "user")

    return render(
        request,
        "moderation/dashboard.html",
        {
            "reported_reviews": reported_reviews,
            "image_reports": image_reports,
            "removed_content": removed_content,
            "reported_users": reported_users,
            "park_reports": park_reports,
            "reply_reports": reply_reports,
        },
    )


@ban_protected
@login_required
def moderation_action(request):
    # Deny if not admin
    if not request.user.is_staff:
        raise PermissionDenied

    if request.method != "POST":
        return HttpResponseNotAllowed(["POST"])
    action = request.POST.get("action")

    if "review_id" in request.POST:
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

    elif "report_id" in request.POST:
        from parks.models import ParkInfoReport  # put at top of file if needed

        report = get_object_or_404(ParkInfoReport, id=request.POST.get("report_id"))

        if action == "approve_park_report":
            park = report.park
            park.dogruns_type = report.new_dogruns_type
            park.accessible = report.new_accessible
            park.save()
            report.delete()
            messages.success(request, "Park info updated successfully.")

        elif action == "dismiss_park_report":
            report.delete()
            messages.success(request, "Park info report dismissed.")

        else:
            messages.error(request, "Invalid Action for park info report.")

    else:
        messages.error(request, "Missing review_id or report_id.")

    return redirect("moderation_dashboard")


@ban_protected
@login_required
def image_moderation_action(request):
    # Deny if not admin
    if not request.user.is_staff:
        raise PermissionDenied

    if request.method != "POST":
        return HttpResponseNotAllowed(["POST"])

    action = request.POST.get("action")
    image = get_object_or_404(ParkImage, id=request.POST.get("image_id"))
    reports = ImageReport.objects.filter(image=image)

    if action == "remove_image" and image.is_removed:
        messages.warning(request, "This image is already removed.")
    elif action == "dismiss_image_report" and not reports.exists():
        messages.warning(request, "There are no reports to dismiss.")

    if action == "remove_image":
        image.is_removed = True
        image.removed_at = timezone.now()
        image.removed_by = request.user
        image.save()
        reports.delete()
        messages.success(request, "Image removed.")
    elif action == "dismiss_image_report":
        image.is_removed = False
        image.removed_at = None
        image.removed_by = None
        image.save()
        reports.delete()
        messages.success(request, "Image report dismissed.")
    else:
        messages.error(request, "Invalid Action")

    return redirect("moderation_dashboard")


@ban_protected
@login_required
def reply_moderation_action(request):
    # Deny if not admin
    if not request.user.is_staff:
        raise PermissionDenied

    if request.method != "POST":
        return HttpResponseNotAllowed(["POST"])

    action = request.POST.get("action")
    reply = get_object_or_404(Reply, id=request.POST.get("reply_id"))
    reports = ReplyReport.objects.filter(reply=reply)

    if action == "remove_reply" and reply.is_removed:
        messages.warning(request, "This reply is already removed.")
    elif action == "dismiss_reply_report" and not reports.exists():
        messages.warning(request, "There are no reports to dismiss.")

    if action == "remove_reply":
        reply.is_removed = True
        reply.removed_at = timezone.now()
        reply.removed_by = request.user
        reply.save()
        reports.delete()
        messages.success(request, "Reply removed.")
    elif action == "dismiss_reply_report":
        reply.is_removed = False
        reply.removed_at = None
        reply.removed_by = None
        reply.save()
        reports.delete()
        messages.success(request, "Reply report dismissed.")
    else:
        messages.error(request, "Invalid Action")

    return redirect("moderation_dashboard")


@ban_protected
@login_required
def removed_review_action(request):
    # Deny if not admin
    if not request.user.is_staff:
        raise PermissionDenied

    if request.method != "POST":
        return HttpResponseNotAllowed(["POST"])

    action = request.POST.get("action")
    review = get_object_or_404(Review, id=request.POST.get("review_id"))

    if action == "restore_review" and not review.is_removed:
        messages.warning(
            request, "This review is not reported or has already been restored."
        )

    if action == "restore_review":
        review.is_removed = False
        review.removed_by = None
        review.removed_at = None
        review.save()
        messages.success(request, "Review Restored")
    elif action == "delete_review":
        if review.replies.filter(is_deleted=False).exists():
            # if review has replies, remove the text, set it to is_deleted
            review.text = ""
            review.is_deleted = True
            review.is_removed = False
            review.removed_by = None
            review.removed_at = None
            review.save()
        else:
            # Delete associated images (if any), then delete the review
            review.images.all().delete()
            review.delete()
        messages.success(request, "Review Permanently Deleted")
    else:
        messages.error(request, "Invalid Action")

    return redirect("moderation_dashboard")


@ban_protected
@login_required
def removed_image_action(request):
    # Deny if not admin
    if not request.user.is_staff:
        raise PermissionDenied

    if request.method != "POST":
        return HttpResponseNotAllowed(["POST"])

    action = request.POST.get("action")
    image = get_object_or_404(ParkImage, id=request.POST.get("image_id"))

    if action == "restore_image" and not image.is_removed:
        messages.warning(
            request, "This image is not reported or has already been restored."
        )

    if action == "restore_image":
        image.is_removed = False
        image.removed_by = None
        image.removed_at = None
        image.save()
        messages.success(request, "Image Restored")
    elif action == "delete_image":
        image.delete()
        messages.success(request, "Image Permanently Deleted")
    else:
        messages.error(request, "Invalid Action")

    return redirect("moderation_dashboard")


@ban_protected
@login_required
def removed_reply_action(request):
    # Deny if not admin
    if not request.user.is_staff:
        raise PermissionDenied

    if request.method != "POST":
        return HttpResponseNotAllowed(["POST"])

    action = request.POST.get("action")
    reply = get_object_or_404(Reply, id=request.POST.get("reply_id"))

    if action == "restore_reply" and not reply.is_removed:
        messages.warning(
            request, "This reply is not reported or has already been restored."
        )

    if action == "restore_reply":
        reply.is_removed = False
        reply.removed_by = None
        reply.removed_at = None
        reply.save()
        messages.success(request, "Reply Restored")
    elif action == "delete_reply":
        reply.text = ""
        reply.is_removed = False
        reply.removed_by = None
        reply.removed_at = None

        reply.is_removed_permanently = True
        reply.save()

        messages.success(request, "Reply Permanently Deleted")
    else:
        messages.error(request, "Invalid Action")

    return redirect("moderation_dashboard")


User = get_user_model()


@login_required
def report_user(request, user_id):
    reported_user = get_object_or_404(User, id=user_id)

    next_param = request.GET.get("next") or request.POST.get("next")
    default_next_url = reverse(
        "profiles:profile", kwargs={"username": reported_user.username}
    )

    if next_param and url_has_allowed_host_and_scheme(
        url=next_param,
        allowed_hosts={request.get_host()},
        require_https=request.is_secure(),
    ):
        next_url = next_param
    else:
        next_url = default_next_url

    if request.method == "POST":
        form = UserReportForm(request.POST)
        if form.is_valid():
            try:
                report = form.save(commit=False)
                report.reporter = request.user
                report.user_being_reported = reported_user
                report.save()
                messages.success(
                    request, _("Your report has been submitted successfully.")
                )
                return redirect(next_url)
            except Exception as e:
                # Consider logging the error e
                messages.error(
                    request,
                    _("An error occurred while submitting the report: %(error)s")
                    % {"error": e},
                )
    else:
        form = UserReportForm()
    context = {
        "form": form,
        "reported_user": reported_user,
        "next": next_url,
        "ReportCategory": ReportCategory,
    }
    return render(request, "moderation/report_user.html", context)


@ban_protected
@login_required
def ban_user_action(request):
    if not request.user.is_staff:
        raise PermissionDenied

    if request.method != "POST":
        return HttpResponseNotAllowed(["POST"])

    user_id = request.POST.get("user_id")
    profile = get_object_or_404(UserProfile, user__id=user_id)

    if profile.is_banned:
        messages.warning(request, f"User {profile.user.username} is already banned.")
    else:
        profile.is_banned = True
        profile.save()
        messages.success(request, f"User {profile.user.username} has been banned.")

    return redirect("moderation_dashboard")


@ban_protected
@login_required
def dismiss_user_report(request):
    if not request.user.is_staff:
        raise PermissionDenied

    if request.method != "POST":
        return HttpResponseNotAllowed(["POST"])

    user_id = request.POST.get("user_id")
    reported_user = get_object_or_404(User, id=user_id)

    # Delete all user reports for this user
    UserReport.objects.filter(user_being_reported=reported_user).delete()

    messages.success(
        request, f"Reports for user {reported_user.username} have been dismissed."
    )
    return redirect("moderation_dashboard")
