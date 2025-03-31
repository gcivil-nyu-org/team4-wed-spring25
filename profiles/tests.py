from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from profiles.models import UserProfile, PetProfile


class ProfileViewsTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username="testuser", password="testpass")
        self.profile = UserProfile.objects.create(
            user=self.user,
            location="NYC",
            phone_number="1234567890",
            website="https://example.com",
            bio="I love dogs!",
            signature="Woof life",
        )
        self.pet = PetProfile.objects.create(
            owner=self.profile,
            name="Buddy",
            breed="Golden Retriever",
            age=3,
            personality="Friendly and loyal",
            favorite_food="Chicken",
        )

    def test_profile_view_requires_login(self):
        response = self.client.get(reverse("profile"))
        self.assertEqual(response.status_code, 302)

    def test_profile_view_logged_in(self):
        self.client.login(username="testuser", password="testpass")
        response = self.client.get(reverse("profile"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "profiles/profile.html")
        self.assertContains(response, "Buddy")

    def test_edit_profile_get(self):
        self.client.login(username="testuser", password="testpass")
        response = self.client.get(reverse("edit_profile"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "profiles/edit_profile.html")

    def test_edit_profile_post(self):
        self.client.login(username="testuser", password="testpass")
        response = self.client.post(
            reverse("edit_profile"),
            {
                "location": "Brooklyn",
                "phone_number": "9876543210",
                "website": "https://newsite.com",
                "bio": "New bio text",
                "signature": "Paws up!",
            },
        )
        self.assertEqual(response.status_code, 302)
        self.profile.refresh_from_db()
        self.assertEqual(self.profile.location, "Brooklyn")
        self.assertEqual(self.profile.signature, "Paws up!")

    def test_add_pet_get(self):
        self.client.login(username="testuser", password="testpass")
        response = self.client.get(reverse("add_pet"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "profiles/add_pet.html")

    def test_add_pet_post(self):
        self.client.login(username="testuser", password="testpass")

        response = self.client.post(
            reverse("add_pet"),
            {
                "name": "Milo",
                "breed": "Siamese",
                "age": 2,
                "personality": "Curious and cuddly",
                "favorite_food": "Tuna",
            },
        )
        self.assertEqual(response.status_code, 302)
        self.assertTrue(PetProfile.objects.filter(name="Milo").exists())

    def test_edit_pet_get(self):
        self.client.login(username="testuser", password="testpass")
        response = self.client.get(reverse("edit_pet", args=[self.pet.id]))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "profiles/edit_pet.html")

    def test_edit_pet_post(self):
        self.client.login(username="testuser", password="testpass")
        response = self.client.post(
            reverse("edit_pet", args=[self.pet.id]),
            {
                "name": "Charlie",
                "breed": "Labrador",
                "age": 4,
                "personality": "Playful",
                "favorite_food": "Beef",
            },
        )
        self.assertEqual(response.status_code, 302)
        self.pet.refresh_from_db()
        self.assertEqual(self.pet.name, "Charlie")
        self.assertEqual(self.pet.breed, "Labrador")

    def test_delete_pet_get(self):
        self.client.login(username="testuser", password="testpass")
        response = self.client.get(reverse("delete_pet", args=[self.pet.id]))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "profiles/delete_pet.html")

    def test_delete_pet_post(self):
        self.client.login(username="testuser", password="testpass")
        response = self.client.post(reverse("delete_pet", args=[self.pet.id]))
        self.assertEqual(response.status_code, 302)
        self.assertFalse(PetProfile.objects.filter(id=self.pet.id).exists())

    def test_pet_detail(self):
        self.client.login(username="testuser", password="testpass")
        response = self.client.get(reverse("pet_detail", args=[self.pet.id]))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "profiles/pet_detail.html")
        self.assertContains(response, "Buddy")

    def test_userprofile_str(self):
        self.assertEqual(str(self.profile), "testuser")

    def test_petprofile_str(self):
        self.assertEqual(str(self.pet), "Buddy")

    def test_edit_profile_post_invalid(self):
        self.client.login(username="testuser", password="testpass")
        response = self.client.post(
            reverse("edit_profile"),
            {
                "phone_number": (
                    "invalid-phone-number-exceeding-max-length-beyond-15-digits"
                )
            },
        )
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "profiles/edit_profile.html")
        self.assertContains(response, "form")

    def test_add_pet_post_invalid(self):
        self.client.login(username="testuser", password="testpass")
        response = self.client.post(
            reverse("add_pet"),
            {
                "name": "",  # name is required
            },
        )
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "profiles/add_pet.html")
        self.assertContains(response, "form")

    def test_edit_pet_post_invalid(self):
        self.client.login(username="testuser", password="testpass")
        response = self.client.post(
            reverse("edit_pet", args=[self.pet.id]),
            {
                "name": "",  # required field empty
            },
        )
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "profiles/edit_pet.html")
        self.assertContains(response, "form")
