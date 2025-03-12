from django.db import models

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

class Review(models.Model):
    park = models.ForeignKey(DogRun, on_delete=models.CASCADE, related_name="reviews")
    text = models.TextField()
    rating = models.IntegerField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "park_reviews"
        ordering = ["-created_at"]

    def __str__(self):
        return f"Review for {self.park.name} ({self.rating} stars)"
