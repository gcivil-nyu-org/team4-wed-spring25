# forms.py
from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

ROLE_CHOICES = [
    ("user", "User"),
    ("admin", "Admin"),
]


class RegisterForm(UserCreationForm):
    role = forms.ChoiceField(choices=ROLE_CHOICES, widget=forms.RadioSelect)
    admin_access_code = forms.CharField(
        max_length=50,
        required=False,
        help_text="Enter the admin access code if signing up as an admin.",
    )

    class Meta:
        model = User
        fields = [
            "username",
            "email",
            "password1",
            "password2",
            "role",
            "admin_access_code",
        ]

    def clean(self):
        cleaned_data = super().clean()
        role = cleaned_data.get("role")
        access_code = cleaned_data.get("admin_access_code")

        # Only check the access code if user selected "Admin"
        if role == "admin":
            REQUIRED_CODE = "SUPERDOG123"  # Hardcoded example

            if not access_code or access_code != REQUIRED_CODE:
                self.add_error("admin_access_code", "Invalid admin access code.")

        return cleaned_data
