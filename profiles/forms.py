from django import forms
from .models import UserProfile, PetProfile


class UserProfileForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = [
            "profile_picture",
            "location",
            "phone_number",
            "website",
            "bio",
            "signature",
        ]
        widgets = {
            "location": forms.TextInput(attrs={"class": "form-control"}),
            "phone_number": forms.TextInput(
                attrs={"class": "form-control", "placeholder": "Optional"}
            ),
            "website": forms.URLInput(
                attrs={"class": "form-control", "placeholder": "https://..."}
            ),
            "bio": forms.Textarea(attrs={"class": "form-control", "rows": 3}),
            "signature": forms.TextInput(attrs={"class": "form-control"}),
        }


class PetProfileForm(forms.ModelForm):
    class Meta:
        model = PetProfile
        fields = ["name", "breed", "age", "pet_picture", "personality", "favorite_food"]
        widgets = {
            "name": forms.TextInput(attrs={"class": "form-control"}),
            "breed": forms.TextInput(attrs={"class": "form-control"}),
            "age": forms.NumberInput(attrs={"class": "form-control"}),
            "personality": forms.Textarea(attrs={"class": "form-control", "rows": 3}),
            "favorite_food": forms.TextInput(attrs={"class": "form-control"}),
        }
