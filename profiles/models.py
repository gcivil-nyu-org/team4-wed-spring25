from django.contrib.auth.models import User
from django.db import models


class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    profile_picture = models.ImageField(
        upload_to="profile_pics/", blank=True, null=True
    )
    location = models.CharField(max_length=100, blank=True, null=True)
    phone_number = models.CharField(max_length=15, blank=True, null=True)
    website = models.URLField(blank=True, null=True)
    bio = models.TextField(blank=True, null=True)
    signature = models.CharField(
        max_length=255, blank=True, null=True, default="Live, Love, Bark!"
    )

    def __str__(self):
        return self.user.username


class PetProfile(models.Model):
    owner = models.ForeignKey(
        UserProfile, on_delete=models.CASCADE, related_name="pets"
    )
    name = models.CharField(max_length=100)
    breed = models.CharField(max_length=100, blank=True, null=True)
    age = models.IntegerField(null=True, blank=True)
    pet_picture = models.ImageField(upload_to="pet_pics/", blank=True, null=True)
    personality = models.CharField(max_length=200, blank=True, null=True)
    favorite_food = models.CharField(max_length=200, blank=True, null=True)

    def __str__(self):
        return self.name
