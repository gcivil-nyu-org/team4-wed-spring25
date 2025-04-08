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

        self.other_user = User.objects.create_user(
            username="otheruser", password="otherpass"
        )
        self.other_user_profile = UserProfile.objects.create(user=self.other_user)
        self.other_pet = PetProfile.objects.create(
            owner=self.other_user_profile, name="OtherPet", breed="Poodle", age=1
        )

        self.profile_url = reverse("profile", args=[self.user.username])
        self.edit_profile_url = reverse("edit_profile")
        self.add_pet_url = reverse("add_pet")
        self.edit_pet_url = reverse("edit_pet", args=[self.pet.id])
        self.delete_pet_url = reverse("delete_pet", args=[self.pet.id])
        self.other_delete_pet_url = reverse("delete_pet", args=[self.other_pet.id])
        self.pet_detail_url = reverse(
            "pet_detail", args=[self.user.username, self.pet.id]
        )
        self.login_url = reverse("login")

    def test_profile_view_requires_login(self):
        response = self.client.get(self.profile_url)
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, f"{self.login_url}?next={self.profile_url}")

    def test_profile_view_logged_in(self):
        self.client.login(username="testuser", password="testpass")
        response = self.client.get(self.profile_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "profiles/profile.html")
        self.assertContains(response, "Buddy")

    def test_edit_profile_get(self):
        self.client.login(username="testuser", password="testpass")
        response = self.client.get(self.edit_profile_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "profiles/edit_profile.html")

    def test_edit_profile_post(self):
        self.client.login(username="testuser", password="testpass")
        update_data = {
            "location": "Brooklyn",
            "phone_number": "9876543210",
            "website": "https://newsite.com",
            "bio": "New bio text",
            "signature": "Paws up!",
        }
        response = self.client.post(self.edit_profile_url, update_data)
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, self.profile_url)
        self.profile.refresh_from_db()
        self.assertEqual(self.profile.location, "Brooklyn")
        self.assertEqual(self.profile.signature, "Paws up!")

    def test_add_pet_get(self):
        self.client.login(username="testuser", password="testpass")
        response = self.client.get(self.add_pet_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "profiles/add_pet.html")

    def test_add_pet_post(self):
        self.client.login(username="testuser", password="testpass")
        initial_pet_count = PetProfile.objects.filter(owner=self.profile).count()
        pet_data = {
            "name": "Milo",
            "breed": "Siamese",
            "age": 2,
            "personality": "Curious and cuddly",
            "favorite_food": "Tuna",
        }
        response = self.client.post(self.add_pet_url, pet_data)
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, self.profile_url)
        self.assertEqual(
            PetProfile.objects.filter(owner=self.profile).count(), initial_pet_count + 1
        )
        self.assertTrue(
            PetProfile.objects.filter(owner=self.profile, name="Milo").exists()
        )

    def test_edit_pet_get(self):
        self.client.login(username="testuser", password="testpass")
        response = self.client.get(self.edit_pet_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "profiles/edit_pet.html")

    def test_edit_pet_post(self):
        self.client.login(username="testuser", password="testpass")
        update_data = {
            "name": "Charlie",
            "breed": "Labrador",
            "age": 4,
            "personality": "Playful",
            "favorite_food": "Beef",
        }
        response = self.client.post(self.edit_pet_url, update_data)
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, self.profile_url)
        self.pet.refresh_from_db()
        self.assertEqual(self.pet.name, "Charlie")
        self.assertEqual(self.pet.breed, "Labrador")

    def test_delete_pet_get_redirects(self):
        """Test GET request to delete_pet URL redirects to profile page."""
        self.client.login(username="testuser", password="testpass")
        response = self.client.get(self.delete_pet_url)
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, self.profile_url)
        self.assertTrue(PetProfile.objects.filter(id=self.pet.id).exists())

    def test_delete_pet_post_non_ajax_redirects(self):
        self.client.login(username="testuser", password="testpass")
        initial_pet_count = PetProfile.objects.count()
        response = self.client.post(self.delete_pet_url)
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, self.profile_url)
        self.assertEqual(PetProfile.objects.count(), initial_pet_count - 1)
        self.assertFalse(PetProfile.objects.filter(id=self.pet.id).exists())

    def test_delete_pet_post_ajax_success(self):
        """Test AJAX POST request deletes pet and returns HTTP 204 No Content."""
        self.client.login(username="testuser", password="testpass")
        initial_pet_count = PetProfile.objects.count()
        response = self.client.post(
            self.delete_pet_url, HTTP_X_REQUESTED_WITH="XMLHttpRequest"
        )
        self.assertEqual(response.status_code, 204)
        self.assertEqual(PetProfile.objects.count(), initial_pet_count - 1)
        self.assertFalse(PetProfile.objects.filter(id=self.pet.id).exists())

    def test_delete_pet_post_ajax_permission_denied(self):
        """Test AJAX POST delete fails (403) when user doesn't own the pet."""
        self.client.login(username="testuser", password="testpass")
        initial_pet_count = PetProfile.objects.count()
        response = self.client.post(
            self.other_delete_pet_url, HTTP_X_REQUESTED_WITH="XMLHttpRequest"
        )
        self.assertEqual(response.status_code, 403)
        self.assertEqual(PetProfile.objects.count(), initial_pet_count)
        self.assertTrue(PetProfile.objects.filter(id=self.other_pet.id).exists())

    def test_delete_pet_get_permission_denied(self):
        """Test GET delete fails (e.g. 403 or redirect) when user doesn't own pet."""
        self.client.login(username="testuser", password="testpass")
        response = self.client.get(self.other_delete_pet_url)
        self.assertEqual(response.status_code, 403)

    def test_delete_pet_unauthenticated(self):
        """Test unauthenticated user is redirected to login for delete URL."""
        response_get = self.client.get(self.delete_pet_url)
        response_post = self.client.post(self.delete_pet_url)
        expected_redirect_url = f"{self.login_url}?next={self.delete_pet_url}"
        self.assertRedirects(response_get, expected_redirect_url)
        self.assertRedirects(response_post, expected_redirect_url)
        self.assertTrue(PetProfile.objects.filter(id=self.pet.id).exists())

    def test_pet_detail(self):
        self.client.login(username="testuser", password="testpass")
        response = self.client.get(self.pet_detail_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "profiles/pet_detail.html")
        self.assertContains(response, "Buddy")

    def test_userprofile_str(self):
        self.assertEqual(str(self.profile), "testuser")

    def test_petprofile_str(self):
        self.assertEqual(str(self.pet), "Buddy")

    def test_edit_profile_post_invalid(self):
        self.client.login(username="testuser", password="testpass")
        response = self.client.post(self.edit_profile_url, {"phone_number": "123" * 20})
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "profiles/edit_profile.html")
        self.assertContains(response, "form")

    def test_add_pet_post_invalid(self):
        self.client.login(username="testuser", password="testpass")
        response = self.client.post(self.add_pet_url, {"name": ""})
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "profiles/add_pet.html")
        self.assertContains(response, "form")

    def test_edit_pet_post_invalid(self):
        self.client.login(username="testuser", password="testpass")
        response = self.client.post(self.edit_pet_url, {"name": ""})
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "profiles/edit_pet.html")
        self.assertContains(response, "form")
