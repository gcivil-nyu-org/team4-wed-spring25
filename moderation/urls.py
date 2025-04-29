from django.urls import path
from . import views


urlpatterns = [
    path("", views.dashboard, name="moderation_dashboard"),
    path("review-action/", views.moderation_action, name="moderation_action"),
    path(
        "image-action/", views.image_moderation_action, name="image_moderation_action"
    ),
    path(
        "removed-review-action",
        views.removed_review_action,
        name="removed_review_action",
    ),
    path(
        "removed-image-action", views.removed_image_action, name="removed_image_action"
    ),
    path("report/<int:user_id>/", views.report_user, name="report_user"),
]
