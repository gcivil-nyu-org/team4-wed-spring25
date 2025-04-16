from django import forms
import re
from .models import UserProfile, PetProfile


class UserProfileForm(forms.ModelForm):
    BOROUGH_CHOICES = [
        ("", "Choose your location"),
        ("Manhattan", "Manhattan"),
        ("Brooklyn", "Brooklyn"),
        ("Queens", "Queens"),
        ("Bronx", "Bronx"),
        ("Staten Island", "Staten Island"),
    ]

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
    location = forms.ChoiceField(
        choices=BOROUGH_CHOICES,
        required=False,
        widget=forms.Select(attrs={"class": "form-select"}),
    )

    class Meta:
        model = UserProfile
        fields = [
            "name",
            "bio",
            "profile_picture",
            "location",
            "website",
            "phone_number",
            "signature",
        ]
        widgets = {
            "name": forms.TextInput(attrs={"class": "form-control"}),
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


ALLOWED_BREEDS = [
    "Beagle",
    "Border Collie",
    "Boston Terrier",
    "Boxer",
    "Bulldog",
    "Chihuahua",
    "Cocker Spaniel",
    "Dachshund",
    "Dalmatian",
    "Doberman",
    "French Bulldog",
    "German Shepherd",
    "Golden Retriever",
    "Great Dane",
    "Labrador Retriever",
    "Maltese",
    "Miniature Schnauzer",
    "Pembroke Welsh Corgi",
    "Pomeranian",
    "Poodle",
    "Pug",
    "Rottweiler",
    "Samoyed",
    "Shiba Inu",
    "Shih Tzu",
    "Siberian Husky",
    "Yorkshire Terrier",
    "Abyssinian",
    "American Shorthair",
    "Bengal",
    "Birman",
    "British Shorthair",
    "Exotic Shorthair",
    "Maine Coon",
    "Persian",
    "Ragdoll",
    "Russian Blue",
    "Scottish Fold",
    "Siamese",
    "Sphynx",
]
breeds = sorted(ALLOWED_BREEDS)


class PetProfileForm(forms.ModelForm):
    breed = forms.ChoiceField(
        choices=[(breed, breed) for breed in breeds],
        required=False,
        widget=forms.Select(attrs={"class": "form-select"}),
    )

    class Meta:
        model = PetProfile
        fields = [
            "name",
            "age",
            "gender",
            "breed",
            "pet_picture",
            "personality",
            "favorite_food",
        ]
        widgets = {
            "name": forms.TextInput(attrs={"class": "form-control"}),
            "age": forms.NumberInput(attrs={"class": "form-control"}),
            "gender": forms.Select(attrs={"class": "form-select"}),
            "pet_picture": forms.ClearableFileInput(attrs={"class": "form-control"}),
            "personality": forms.TextInput(attrs={"class": "form-control"}),
            "favorite_food": forms.TextInput(attrs={"class": "form-control"}),
        }
