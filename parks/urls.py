from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path("list/", views.park_list, name="park_list"),
    path("map/", views.map, name="map"),
    path("combined/", views.park_and_map, name="park_and_map"),
    path("park/<int:id>/", views.park_detail, name="park_detail"),
]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
