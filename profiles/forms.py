from django import forms
import re
from .models import UserProfile, PetProfile


class UserProfileForm(forms.ModelForm):
    website = forms.URLField(
        required=False,
        widget=forms.URLInput(
            attrs={"class": "form-control", "placeholder": "https://..."}
        ),
    )
    phone_number = forms.CharField(
        required=False,
        max_length=15,
        widget=forms.TextInput(
            attrs={
                "class": "form-control",
                "placeholder": "Optional",
                "id": "phone_number",
            }
        ),
    )

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
            "bio": forms.Textarea(attrs={"class": "form-control", "rows": 3}),
            "signature": forms.TextInput(attrs={"class": "form-control"}),
            "profile_picture": forms.ClearableFileInput(
                attrs={"class": "form-control"}
            ),
        }

    def clean_phone_number(self):
        phone_number = self.cleaned_data.get("phone_number")
        if phone_number and phone_number.strip():
            if not re.fullmatch(r"^\d+$", phone_number.strip()):
                raise forms.ValidationError("Phone numbers can only contain numbers!")
        return phone_number


class PetProfileForm(forms.ModelForm):
    age = forms.IntegerField(
        min_value=0,
        required=False,
        widget=forms.NumberInput(attrs={"class": "form-control"}),
    )

    class Meta:
        model = PetProfile
        fields = ["name", "breed", "age", "pet_picture", "personality", "favorite_food"]
        widgets = {
            "name": forms.TextInput(attrs={"class": "form-control"}),
            "breed": forms.TextInput(attrs={"class": "form-control"}),
            "personality": forms.Textarea(attrs={"class": "form-control", "rows": 3}),
            "favorite_food": forms.TextInput(attrs={"class": "form-control"}),
            "pet_picture": forms.ClearableFileInput(attrs={"class": "form-control"}),
        }
