from django.urls import path
from .views import profile_view, edit_profile, add_pet, edit_pet, delete_pet, pet_detail

urlpatterns = [
    path('', profile_view, name='profile'),
    path('edit/', edit_profile, name='edit_profile'),
    path('pet/add/', add_pet, name='add_pet'),
    path('pet/edit/<int:pet_id>/', edit_pet, name='edit_pet'),
    path('pet/delete/<int:pet_id>/', delete_pet, name='delete_pet'),
    path('pet/<int:pet_id>/', pet_detail, name='pet_detail'),
]
