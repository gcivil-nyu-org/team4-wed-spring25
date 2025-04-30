from django.db import models
from django.contrib.auth import get_user_model
from django.utils.translation import gettext_lazy as _

User = get_user_model()


class ReportCategory(models.TextChoices):
    SPAM = "SPAM", _("Spam or Junk")
    HARASSMENT = "HARASSMENT", _("Harassment or Bullying")
    HATE_SPEECH = "HATE_SPEECH", _("Hate Speech")
    IMPERSONATION = "IMPERSONATION", _("Impersonation")
    INAPPROPRIATE = "INAPPROPRIATE", _("Inappropriate Content")
    OTHER = "OTHER", _("Other (Please specify)")


class UserReport(models.Model):
    report_id = models.AutoField(primary_key=True)
    reporter = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="reports_made"
    )
    user_being_reported = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="reports_received"
    )

    category = models.CharField(
        _("Report Category"),
        max_length=20,
        choices=ReportCategory.choices,
    )

    reason = models.TextField(
        _("Optional details"),
        blank=True,
        help_text=_(
            "You can provide specific details about the report here, if necessary."
        ),
    )

    reported_time = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return (
            f"Report {self.report_id} by {self.reporter} "
            f"against {self.user_being_reported} ({self.get_category_display()})"
        )
