from django.urls import path
from . import views

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
]
