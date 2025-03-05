from django.db import models

class DogRun(models.Model):

  id = models.CharField(max_length=255)
  prop_id = models.CharField(max_length=255, primary_key=True)
  name = models.CharField(max_length=255)
  address = models.CharField(max_length=255)
  dogruns_type = models.CharField()
  accessible = models.CharField(max_length=50)
  notes = models.TextField(max_length=255)

  class Meta:
      db_table = "dog_runs"

  def __str__(self):
    return self.name
