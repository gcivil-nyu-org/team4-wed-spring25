from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from profiles.templatetags.custom_filters import replace
from profiles.models import PetProfile
from parks.models import Review, ParkImage, DogRunNew


class ProfileViewsTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username="testuser", password="testpass")
        self.profile = self.user.userprofile

        self.profile.location = "NYC"
        self.profile.phone_number = "1234567890"
        self.profile.website = "https://example.com"
        self.profile.bio = "I love dogs!"
        self.profile.signature = "Woof life"
        self.profile.save()

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
        self.other_user_profile = self.other_user.userprofile
        self.other_pet = PetProfile.objects.create(
            owner=self.other_user_profile, name="OtherPet", breed="Poodle", age=1
        )

        self.profile_url = reverse("profiles:profile", args=[self.user.username])
        self.edit_profile_url = reverse("profiles:edit_profile")
        self.add_pet_url = reverse("profiles:add_pet")
        self.edit_pet_url = reverse("profiles:edit_pet", args=[self.pet.id])
        self.delete_pet_url = reverse("profiles:delete_pet", args=[self.pet.id])
        self.other_delete_pet_url = reverse(
            "profiles:delete_pet", args=[self.other_pet.id]
        )
        self.pet_detail_url = reverse(
            "profiles:pet_detail", args=[self.user.username, self.pet.id]
        )
        self.login_url = reverse("login")
        self.park = DogRunNew.objects.create(
            id=123,
            prop_id="prop-123",
            name="Central Park",
            address="123 Park Ave",
            dogruns_type="Off-Leash",
            accessible="Yes",
            notes="A big park",
            display_name="Central Park",
            slug="central-park",
        )

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
            "phone_number": "(929) 654-3210",
            "website": "https://newsite.com",
            "bio": "New bio text",
            "signature": "Paws up!",
        }
        response = self.client.post(self.edit_profile_url, update_data)

        self.assertEqual(response.status_code, 200)

        json_response = response.json()
        self.assertIn("success", json_response)
        self.assertTrue(json_response["success"])
        self.assertIn("redirect_url", json_response)

        expected_redirect_url = self.profile_url
        self.assertEqual(json_response["redirect_url"], expected_redirect_url)

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
            "gender": "male",
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

    # def test_edit_pet_post(self):
    #     self.client.login(username="testuser", password="testpass")
    #     update_data = {
    #         "name": "Charlie",
    #         "breed": "Labrador",
    #         "age": 4,
    #         "gender": "male",
    #         "personality": "Playful",
    #         "favorite_food": "Beef",
    #     }
    #     response = self.client.post(self.edit_pet_url, update_data)
    #     self.assertEqual(response.status_code, 302)
    #     self.assertRedirects(response, self.profile_url)
    #     self.pet.refresh_from_db()
    #     self.assertEqual(self.pet.name, "Charlie")
    #     self.assertEqual(self.pet.breed, "Labrador")

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
        invalid_data = {
            "location": "Brooklyn",
            "phone_number": "invalid-phone",
            "website": "https://newsite.com",
            "bio": "New bio text",
            "signature": "Paws up!",
        }
        response = self.client.post(self.edit_profile_url, invalid_data)

        self.assertEqual(response.status_code, 400)

        json_response = response.json()
        self.assertIn("phone_number", json_response)
        self.assertIsInstance(json_response["phone_number"], list)
        self.assertIn(
            "Invalid phone number format entered.", json_response["phone_number"]
        )

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

    def test_profile_view_filters_deleted_review_images(self):
        self.client.login(username="testuser", password="testpass")

        # Create review with attached image
        review = Review.objects.create(
            user=self.user, park=self.park, rating=4, text="Nice place!"
        )
        image = ParkImage.objects.create(
            user=self.user, review=review, park=self.park, image="upload/sample.jpg"
        )

        # Soft-delete the review
        review.is_deleted = True
        review.save()

        response = self.client.get(self.profile_url)

        # The image should not appear in user_images (deleted review)
        self.assertNotIn(image, response.context["user_images"])

    def test_profile_view_includes_images_without_review(self):
        self.client.login(username="testuser", password="testpass")

        # Create an image not attached to any review
        image = ParkImage.objects.create(
            user=self.user, park=self.park, image="upload/standalone.jpg"
        )

        response = self.client.get(self.profile_url)

        # The image should be included
        self.assertIn(image, response.context["user_images"])

    def test_profile_view_includes_images_attached_to_visible_review(self):
        self.client.login(username="testuser", password="testpass")

        review = Review.objects.create(
            user=self.user, park=self.park, rating=5, text="Great!"
        )
        image = ParkImage.objects.create(
            user=self.user, review=review, park=self.park, image="upload/clean.jpg"
        )

        response = self.client.get(self.profile_url)

        # Image should be visible because the review is not deleted
        self.assertIn(image, response.context["user_images"])


class CustomFilterTests(TestCase):
    def test_replace_filter_basic(self):
        result = replace("upload/image.jpg", "upload/,upload/w_300/")
        self.assertEqual(result, "upload/w_300/image.jpg")

    def test_replace_filter_with_extra_path(self):
        result = replace("upload/abc/xyz.jpg", "upload/,upload/w_600,q_auto/")
        self.assertEqual(result, "upload/w_600,q_auto/abc/xyz.jpg")

    def test_replace_filter_with_missing_comma(self):
        with self.assertRaises(ValueError):
            replace("upload/a", "justonevalue")  # missing comma

    def test_replace_filter_with_multiple_commas(self):
        result = replace("upload/a", "upload/,upload/w_300,q_auto,f_auto/")
        self.assertEqual(result, "upload/w_300,q_auto,f_auto/a")

    def test_replace_filter_with_empty_string(self):
        result = replace("", "upload/,upload/w_300/")
        self.assertEqual(result, "")

    def test_replace_filter_no_match(self):
        result = replace("media/a", "upload/,upload/w_300/")
        self.assertEqual(result, "media/a")
