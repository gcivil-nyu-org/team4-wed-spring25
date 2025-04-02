from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.auth import views as auth_views
from .views import register_view

urlpatterns = [
    path("list/", views.park_list, name="park_list"),
    path("map/", views.map, name="map"),
    path("combined/", views.park_and_map, name="park_and_map"),
    path("park/<int:id>/", views.park_detail, name="park_detail"),
    path("delete_review/<int:review_id>/", views.delete_review, name="delete_review"),
    path("delete_image/<int:image_id>/", views.delete_image, name="delete_image"),
    path("report/image/<int:image_id>/", views.report_image, name="report_image"),
    path("home/", views.home_view, name="home"),
    path("contact/", views.contact_view, name="contact"),
    path("", views.home_view, name="home"),
    path("register/", register_view, name="register"),
    path(
        "login/",
        auth_views.LoginView.as_view(template_name="parks/login.html"),
        name="login",
    ),
    path("logout/", auth_views.LogoutView.as_view(), name="logout"),
]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
