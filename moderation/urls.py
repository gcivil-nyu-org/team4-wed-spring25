from django.urls import path
from . import views


urlpatterns = [
    path("", views.dashboard, name="moderation_dashboard"),
    path("review-action/", views.moderation_action, name="moderation_action"),
    path(
        "image-action/", views.image_moderation_action, name="image_moderation_action"
    ),
    path(
        "reply-action/", views.reply_moderation_action, name="reply_moderation_action"
    ),
    path(
        "removed-review-action",
        views.removed_review_action,
        name="removed_review_action",
    ),
    path(
        "removed-image-action", views.removed_image_action, name="removed_image_action"
    ),
    path(
        "removed-reply-action", views.removed_reply_action, name="removed_reply_action"
    ),
    path("report/<int:user_id>/", views.report_user, name="report_user"),
    path("moderation/ban_user/", views.ban_user_action, name="ban_user"),
    path("dismiss-user-report/", views.dismiss_user_report, name="dismiss_user_report"),
]
