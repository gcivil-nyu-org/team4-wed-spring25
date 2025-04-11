from django import forms
from .models import Announcement


class AnnouncementForm(forms.ModelForm):
    class Meta:
        model = Announcement
        fields = ["title", "content", "pinned", "expiry_date"]
        widgets = {
            "expiry_date": forms.DateTimeInput(
                attrs={
                    "type": "datetime-local",
                    "class": "form-control",  # optional styling via Bootstrap, etc.
                },
                format="%Y-%m-%dT%H:%M",
            ),
        }

    # Ensure the widget displays the correct format if there's an existing value
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance and self.instance.expiry_date:
            self.fields["expiry_date"].initial = self.instance.expiry_date.strftime(
                "%Y-%m-%dT%H:%M"
            )
