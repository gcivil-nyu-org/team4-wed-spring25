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


class DogRunNew(models.Model):
    id = models.CharField(max_length=255, primary_key=True)
    prop_id = models.CharField(max_length=255)
    name = models.CharField(max_length=255)
    address = models.CharField(max_length=255)
    dogruns_type = models.CharField(max_length=100)
    accessible = models.CharField(max_length=50)
    notes = models.TextField(max_length=255)
    image = models.ImageField(upload_to="dogruns/", null=True, blank=True)
    google_name = models.TextField(null=True, blank=True)
    borough = models.TextField(null=True, blank=True)
    zip_code = models.TextField(null=True, blank=True)
    formatted_address = models.TextField(null=True, blank=True)
    latitude = models.FloatField(null=True, blank=True)
    longitude = models.FloatField(null=True, blank=True)
    additional = models.JSONField(null=True, blank=True)  # PostgreSQL JSONB

    class Meta:
        db_table = "dog_runs_new"

    def __str__(self):
        return self.name
