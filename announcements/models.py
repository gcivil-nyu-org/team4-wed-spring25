from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone


class Announcement(models.Model):
    title = models.CharField(max_length=255)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    pinned = models.BooleanField(default=False)
    expiry_date = models.DateTimeField(null=True, blank=True)

    def is_expired(self):
        return self.expiry_date and timezone.now() > self.expiry_date

    def __str__(self):
        return self.title
