from django.urls import path
from . import views


urlpatterns = [
    path('list/', views.park_list, name='park_list'),
]
