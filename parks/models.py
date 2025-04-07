from django.db import models
from cloudinary.models import CloudinaryField
from django.contrib.auth.models import User
from django.utils import timezone


class DogRun(models.Model):
    id = models.CharField(max_length=255)
    prop_id = models.CharField(max_length=255, primary_key=True)
    name = models.CharField(max_length=255)
    address = models.CharField(max_length=255)
    dogruns_type = models.CharField(max_length=100)
    accessible = models.CharField(max_length=50)
    notes = models.TextField(max_length=255)
    image = models.ImageField(upload_to="dogruns/", null=True, blank=True)

    class Meta:
        db_table = "dog_runs"

    def __str__(self):
        return self.name


class DogRunNew(models.Model):
    id = models.CharField(max_length=255, primary_key=True)
    prop_id = models.CharField(max_length=255)
    name = models.CharField(max_length=255)
    address = models.CharField(max_length=255)
    dogruns_type = models.CharField(max_length=100)
    accessible = models.CharField(max_length=50)
    notes = models.TextField(max_length=255)
    google_name = models.TextField(null=True, blank=True)
    borough = models.TextField(null=True, blank=True)
    zip_code = models.TextField(null=True, blank=True)
    formatted_address = models.TextField(null=True, blank=True)
    latitude = models.FloatField(null=True, blank=True)
    longitude = models.FloatField(null=True, blank=True)
    additional = models.JSONField(null=True, blank=True)  # PostgreSQL JSONB
    display_name = models.TextField(null=True, blank=True)

    class Meta:
        db_table = "dog_runs_new"

    def __str__(self):
        return self.name


class Review(models.Model):
    park = models.ForeignKey(
        DogRunNew, on_delete=models.CASCADE, related_name="reviews"
    )
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="reviews"
    )  # 添加
    text = models.TextField()
    rating = models.IntegerField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "park_reviews"
        ordering = ["-created_at"]

    def __str__(self):
        return f"Review for {self.park.name} ({self.rating} stars)"


class ParkImage(models.Model):
    park = models.ForeignKey(
        DogRunNew,
        on_delete=models.CASCADE,
        related_name="images",
        to_field="id",
        db_column="park_id",
    )
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="images", null=True, blank=True
    )
    image = CloudinaryField("image")

    def __str__(self):
        return f"Image for {self.park.name}"


class ReviewReport(models.Model):
    review = models.ForeignKey(
        "Review", on_delete=models.CASCADE, related_name="reports"
    )
    reported_by = models.ForeignKey(User, on_delete=models.CASCADE)
    reason = models.TextField()
    reported_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"Reported by {self.reported_by.username} on {self.review.id}"


class ImageReport(models.Model):
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="image_reports"
    )
    image = models.ForeignKey(
        ParkImage, on_delete=models.CASCADE, related_name="reports"
    )
    reason = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Report by {self.user.username} on Image {self.image.id}"
