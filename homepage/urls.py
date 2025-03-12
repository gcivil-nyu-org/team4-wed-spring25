from django.urls import path
from . import views

urlpatterns = [
    path("health_check/", views.health_check, name="health_check"),
    path("dbtest/", views.test_db_connection, name="test_db_connection"),
    # path('hello_world/', views.hello_world, name='hello_world'),
    path("", views.hello_world, name="home"),
]
