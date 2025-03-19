from django import forms
from .models import UserProfile, PetProfile

class UserProfileForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ['profile_picture', 'location', 'phone_number', 'website', 'bio', 'signature']

class PetProfileForm(forms.ModelForm):
    class Meta:
        model = PetProfile
        fields = ['name', 'breed', 'age', 'pet_picture', 'personality', 'favorite_food']

