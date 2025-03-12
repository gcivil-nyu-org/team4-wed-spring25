from django.db import models


class DogRun(models.Model):
    id = models.AutoField(primary_key=True)
    prop_id = models.CharField(max_length=255, unique=True)
    name = models.CharField(max_length=255)
    address = models.CharField(max_length=255)
    dogruns_type = models.CharField(max_length=100)  # Fix here
    accessible = models.CharField(max_length=50)
    notes = models.TextField(max_length=255)
    image = models.ImageField(upload_to="dogruns/", null=True, blank=True)  # New field

    class Meta:
        db_table = "dog_runs"

    def __str__(self):
        return self.name
