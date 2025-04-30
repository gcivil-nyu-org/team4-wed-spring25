from django import forms
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
from .models import UserReport, ReportCategory


class UserReportForm(forms.ModelForm):
    class Meta:
        model = UserReport
        fields = ["category", "reason"]
        widgets = {
            "category": forms.RadioSelect,
            "reason": forms.Textarea(attrs={"rows": 4}),
        }
        labels = {
            "category": _("Please select a reason for reporting"),
            "reason": _("Optional details"),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["category"].choices = ReportCategory.choices
        self.fields["category"].empty_label = None

    def clean(self):
        cleaned_data = super().clean()
        category = cleaned_data.get("category")
        reason = cleaned_data.get("reason")

        if category == ReportCategory.OTHER:
            if not reason:
                self.add_error(
                    "reason",
                    ValidationError(
                        _("Please provide details when selecting 'Other'."),
                        code="required_if_other",
                    ),
                )

        return cleaned_data
