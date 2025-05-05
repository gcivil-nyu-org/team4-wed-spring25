from django import forms
import re
from .models import UserProfile, PetProfile


import re
from django import forms
from .models import UserProfile
import phonenumbers
from phonenumbers import NumberParseException

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
        max_length=20,
        widget=forms.TextInput(
            attrs={
                "class": "form-control",
                "placeholder": "e.g., (123) 456-7890",
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
        phone_number_str = self.cleaned_data.get("phone_number", "").strip()
        if phone_number_str:
            try:
                parsed_number = phonenumbers.parse(phone_number_str, "US")

                if not phonenumbers.is_valid_number(parsed_number):
                    raise forms.ValidationError("Please enter a valid US phone number.")

                national_number = phonenumbers.national_significant_number(parsed_number)
                print(f"DEBUG: national_number is: {repr(national_number)}")
                print(f"DEBUG: len(national_number) is: {len(national_number)}")

                if len(national_number) != 10:
                     raise forms.ValidationError("Please enter a valid 10-digit US phone number.")


                return national_number

            except NumberParseException:
                raise forms.ValidationError("Invalid phone number format entered.")

        return phone_number_str


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
