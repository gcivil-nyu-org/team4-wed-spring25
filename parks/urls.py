from django.urls import path
from . import views


urlpatterns = [
    path('list/', views.park_list, name='park_list'),
    # Temp url for map
    path('map/', views.map, name='map'),
]
