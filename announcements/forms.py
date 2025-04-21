# announcements/forms.py

from django import forms
from .models import Announcement


class AnnouncementForm(forms.ModelForm):
    expiry_date = forms.DateTimeField(
        widget=forms.DateTimeInput(
            attrs={"type": "datetime-local", "class": "form-control"}
        ),
        required=False,  # allows you to leave it blank
    )

    class Meta:
        model = Announcement
        fields = ["title", "content", "expiry_date", "pinned"]  # ← use 'content' here
        widgets = {
            "title": forms.TextInput(attrs={"class": "form-control"}),
            "content": forms.Textarea(attrs={"class": "form-control", "rows": 4}),
            "pinned": forms.CheckboxInput(attrs={"class": "form-check-input"}),
        }
