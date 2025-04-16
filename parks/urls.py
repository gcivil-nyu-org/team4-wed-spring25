from django.urls import path
from . import views
from django.contrib.auth import views as auth_views
from .views import register_view

urlpatterns = [
    path("parks/", views.park_and_map, name="park_and_map"),
    path("parks/<slug:slug>-<int:id>/", views.park_detail, name="park_detail"),
    path("delete_review/<int:review_id>/", views.delete_review, name="delete_review"),
    path("delete_image/<int:image_id>/", views.delete_image, name="delete_image"),
    path("report/image/<int:image_id>/", views.report_image, name="report_image"),
    path("delete_reply/<int:reply_id>/", views.delete_reply, name="delete_reply"),
    path("report_reply/<int:reply_id>/", views.report_reply, name="report_reply"),
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
    path(
        "password_reset/",
        auth_views.PasswordResetView.as_view(
            template_name="registration/password_reset_form.html",
            email_template_name="registration/password_reset_email.html",
            subject_template_name="registration/password_reset_subject.txt",
        ),
        name="password_reset",
    ),
    path(
        "password_reset/done/",
        auth_views.PasswordResetDoneView.as_view(
            template_name="registration/password_reset_done.html"
        ),
        name="password_reset_done",
    ),
    path(
        "reset/<uidb64>/<token>/",
        auth_views.PasswordResetConfirmView.as_view(
            template_name="registration/password_reset_confirm.html"
        ),
        name="password_reset_confirm",
    ),
    path(
        "reset/done/",
        auth_views.PasswordResetCompleteView.as_view(
            template_name="registration/password_reset_complete.html"
        ),
        name="password_reset_complete",
    ),
]
