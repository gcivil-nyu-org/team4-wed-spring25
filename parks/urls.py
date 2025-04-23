from . import views
from django.contrib.auth import views as auth_views
from django.urls import path, reverse_lazy


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
    path("api/checkin/", views.checkin_view, name="checkin"),
    path("api/bethere/", views.bethere_view, name="bethere"),
    path("messages/", views.all_messages_view, name="all_messages"),
    path("chat/<str:username>/", views.chat_view, name="chat_view"),
    path(
        "delete_conversation/<str:sender_username>/",
        views.delete_conversation,
        name="delete_conversation",
    ),
    path(
        "password-reset/",
        auth_views.PasswordResetView.as_view(
            template_name="registration/password_reset_form.html",
            email_template_name="registration/password_reset_email.html",
            subject_template_name="registration/password_reset_subject.txt",
            success_url=reverse_lazy("password_reset_done"),
        ),
        name="password_reset",
    ),
    # Password reset: email sent confirmation
    path(
        "password-reset/done/",
        auth_views.PasswordResetDoneView.as_view(
            template_name="registration/password_reset_done.html"
        ),
        name="password_reset_done",
    ),
    # Password reset: link with token
    path(
        "reset/<uidb64>/<token>/",
        auth_views.PasswordResetConfirmView.as_view(
            template_name="registration/password_reset_confirm.html",
            success_url=reverse_lazy("password_reset_complete"),
        ),
        name="password_reset_confirm",
    ),
    # Password reset: complete
    path(
        "reset/done/",
        auth_views.PasswordResetCompleteView.as_view(
            template_name="registration/password_reset_complete.html"
        ),
        name="password_reset_complete",
    ),
    path(
        "password-change/",
        auth_views.PasswordResetView.as_view(
            template_name="registration/password_change_email_form.html",
            email_template_name="registration/password_change_email.html",
            subject_template_name="registration/password_change_subject.txt",
            success_url=reverse_lazy("password_change_done"),
        ),
        name="password_change_email",
    ),
    # 2) “Check your inbox” confirmation
    path(
        "password-change/done/",
        auth_views.PasswordResetDoneView.as_view(
            template_name="registration/password_change_done.html"
        ),
        name="password_change_done",
    ),
    # 3) Link with token → new‑password form
    path(
        "password-change-confirm/<uidb64>/<token>/",
        auth_views.PasswordResetConfirmView.as_view(
            template_name="registration/password_change_confirm.html",
            success_url=reverse_lazy("password_change_complete"),
        ),
        name="password_change_confirm",
    ),
    # 4) Final “your password has been changed” page
    path(
        "password-change-complete/",
        auth_views.PasswordResetCompleteView.as_view(
            template_name="registration/password_change_complete.html"
        ),
        name="password_change_complete",
    ),
]
