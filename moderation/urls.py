from django.urls import path
from . import views

urlpatterns = [
    path("", views.dashboard, name="moderation_dashboard"),
    path("moderation/action/", views.moderation_action, name="moderation_action"),
]
