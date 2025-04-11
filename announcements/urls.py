from django.urls import path
from . import views

urlpatterns = [
    path("", views.announcements_list, name="announcements_list"),
    path("create/", views.create_announcement, name="create_announcement"),
    path("<int:pk>/edit/", views.edit_announcement, name="edit_announcement"),
    path("<int:pk>/delete/", views.delete_announcement, name="delete_announcement"),
]

