from django.db import models
from cloudinary.models import CloudinaryField
from django.contrib.auth.models import User
from django.utils import timezone
from django.utils.text import slugify
from django.urls import reverse


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
    display_name = models.TextField(null=False, blank=False)
    slug = models.SlugField(null=False, blank=False)

    class Meta:
        db_table = "dog_runs_new"

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        combined = f"{self.display_name}-{self.prop_id}"
        self.slug = slugify(combined)
        super().save(*args, **kwargs)

    # function to easily get url of park_detail
    def detail_page_url(self):
        return reverse("park_detail", kwargs={"slug": self.slug, "id": self.id})


class Review(models.Model):
    park = models.ForeignKey(
        DogRunNew, on_delete=models.CASCADE, related_name="reviews"
    )
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="reviews")
    text = models.TextField()
    rating = models.IntegerField()
    created_at = models.DateTimeField(auto_now_add=True)

    # Soft Delete fields
    is_removed = models.BooleanField(default=False)
    removed_at = models.DateTimeField(null=True, blank=True)
    removed_by = models.ForeignKey(
        User,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="removed_reviews",
    )
    is_deleted = models.BooleanField(default=False)

    def has_active_replies(self):
        return self.replies.filter(is_deleted=False).exists()

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
    review = models.ForeignKey(
        "Review", on_delete=models.CASCADE, null=True, blank=True, related_name="images"
    )
    image = CloudinaryField("image")

    # Soft deletion fields:
    is_removed = models.BooleanField(default=False)
    removed_at = models.DateTimeField(null=True, blank=True)
    removed_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="removed_images",
        help_text="Admin who removed the image",
    )

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


class Reply(models.Model):
    review = models.ForeignKey(Review, on_delete=models.CASCADE, related_name="replies")
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    parent_reply = models.ForeignKey(
        "self", on_delete=models.CASCADE, null=True, blank=True, related_name="children"
    )
    text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    is_deleted = models.BooleanField(default=False)

    # Soft Delete fields
    is_removed = models.BooleanField(default=False)
    removed_at = models.DateTimeField(null=True, blank=True)
    removed_by = models.ForeignKey(
        User,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="removed_replies",
    )

    is_removed_permanently = models.BooleanField(default=False)

    def has_active_children(self):
        return self.children.filter(is_deleted=False).exists()

    class Meta:
        ordering = ["created_at"]

    def __str__(self):
        return f"Reply by {self.user.username} on review {self.review.id}"


class ReplyReport(models.Model):
    reply = models.ForeignKey(Reply, on_delete=models.CASCADE, related_name="reports")
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    reason = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)


class ParkPresence(models.Model):
    STATUS_CHOICES = [
        ("Current", "Current"),
        ("On their way", "On their way"),
    ]

    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="park_presences"
    )
    park = models.ForeignKey(
        DogRunNew, on_delete=models.CASCADE, related_name="presences"
    )
    status = models.CharField(max_length=20, choices=STATUS_CHOICES)

    # This is now the proper datetime for scheduled arrival
    time = models.DateTimeField(null=True, blank=True)

    checked_in_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "park_presence"
        unique_together = ("user", "park")
        ordering = ["-checked_in_at"]

    def __str__(self):
        return f"{self.user.username} - {self.park.display_name} ({self.status})"


class Message(models.Model):
    sender = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="sent_messages"
    )
    recipient = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="received_messages"
    )
    content = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["timestamp"]

    def __str__(self):
        return f"From {self.sender} to {self.recipient} at {self.timestamp}"


class ParkInfoReport(models.Model):
    park = models.ForeignKey(
        DogRunNew, on_delete=models.CASCADE, related_name="info_reports"
    )
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    new_dogruns_type = models.CharField(
        max_length=20, choices=[("Off-Leash", "Off-Leash"), ("Run", "Run")]
    )
    new_accessible = models.BooleanField()
    submitted_at = models.DateTimeField(auto_now_add=True)
    is_handled = models.BooleanField(default=False)
