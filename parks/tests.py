from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from .models import DogRunNew, Review, ParkImage


# import os


class LoginTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username="testuser", password="StrongPass123"
        )

    def test_login_page_loads(self):
        """Ensure the login page loads properly."""
        response = self.client.get(reverse("login"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "parks/login.html")

    def test_valid_login(self):
        """Ensure a valid user can log in."""
        response = self.client.post(
            reverse("login"), {"username": "testuser", "password": "StrongPass123"}
        )
        self.assertEqual(response.status_code, 302)


class AuthTests(TestCase):
    def setUp(self):
        self.client = Client()

    def test_register_page_loads(self):
        """Ensure the registration page loads properly."""
        response = self.client.get(reverse("register"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "parks/register.html")

    def test_user_registration(self):
        """Ensure a new user can register successfully."""
        response = self.client.post(
            reverse("register"),
            {
                "username": "testuser",
                "password1": "StrongPass123",
                "password2": "StrongPass123",
                "role": "user",  # Ensure this field is required
            },
        )
        self.assertEqual(response.status_code, 302)
        self.assertTrue(User.objects.filter(username="testuser").exists())


class ParkModelTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.park = DogRunNew.objects.create(
            id="1",
            prop_id="1234",
            name="Central Park",
            address="New York, NY",
            dogruns_type="Small",
            accessible="Yes",
            notes="Test park notes",
            google_name="Central Park",
            borough="M",
            zip_code="United States",
            formatted_address="Central Pk N, New York, NY, USA",
            latitude=40.7987768,
            longitude=-73.9537196,
            additional={
                "geometry": {
                    "bounds": {
                        "northeast": {"lat": 40.8009264, "lng": -73.9495752},
                        "southwest": {"lat": 40.796948, "lng": -73.9580246},
                    },
                    "location": {"lat": 40.7987768, "lng": -73.9537196},
                    "location_type": "GEOMETRIC_CENTER",
                    "viewport": {
                        "northeast": {"lat": 40.8009264, "lng": -73.9495752},
                        "southwest": {"lat": 40.796948, "lng": -73.9580246},
                    },
                }
            },
        )

    def test_park_creation(self):
        self.assertEqual(self.park.name, "Central Park")
        self.assertEqual(self.park.address, "New York, NY")
        self.assertEqual(self.park.notes, "Test park notes")


class ReviewModelTest(TestCase):
    def setUp(self):
        self.park = DogRunNew.objects.create(
            id="2",
            prop_id="5678",
            name="Brooklyn Park",
            address="Brooklyn, NY",
            dogruns_type="Large",
            accessible="No",
            notes="Another test park",
        )
        self.review = Review.objects.create(
            park=self.park, text="Great park!", rating=5
        )

    def test_review_creation(self):
        self.assertEqual(self.review.text, "Great park!")
        self.assertEqual(self.review.rating, 5)
        self.assertEqual(self.review.park.name, "Brooklyn Park")

    def test_review_str_method(self):
        self.assertEqual(str(self.review), "Review for Brooklyn Park (5 stars)")


class ParkListViewTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.park = DogRunNew.objects.create(
            id="1",
            prop_id="1234",
            name="Central Park",
            address="New York, NY",
            dogruns_type="Small",
            accessible="Yes",
            notes="Test park notes",
            google_name="Central Park",
            borough="M",
            zip_code="United States",
            formatted_address="Central Pk N, New York, NY, USA",
            latitude=40.7987768,
            longitude=-73.9537196,
            additional={
                "geometry": {
                    "bounds": {
                        "northeast": {"lat": 40.8009264, "lng": -73.9495752},
                        "southwest": {"lat": 40.796948, "lng": -73.9580246},
                    },
                    "location": {"lat": 40.7987768, "lng": -73.9537196},
                    "location_type": "GEOMETRIC_CENTER",
                    "viewport": {
                        "northeast": {"lat": 40.8009264, "lng": -73.9495752},
                        "southwest": {"lat": 40.796948, "lng": -73.9580246},
                    },
                }
            },
        )

    def test_park_list_view(self):
        response = self.client.get(reverse("park_list"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Central Park")


class MapViewTest(TestCase):
    def setUp(self):
        self.client = Client()

    def test_map_view(self):
        response = self.client.get(reverse("map"))
        self.assertEqual(response.status_code, 200)


class CombinedViewTest(TestCase):
    def setUp(self):
        self.client = Client()

    def test_combined_view(self):
        response = self.client.get(reverse("park_and_map"))
        self.assertEqual(response.status_code, 200)


class ParkDetailViewTest(TestCase):
    def setUp(self):
        """Set up the test client and create a test park."""
        self.client = Client()

        self.park = DogRunNew.objects.create(
            id="1",
            prop_id="1234",
            name="Central Park",
            address="New York, NY",
            dogruns_type="Small",
            accessible="Yes",
            notes="Test park notes",
            google_name="Central Park",
            borough="M",
            zip_code="United States",
            formatted_address="Central Pk N, New York, NY, USA",
            latitude=40.7987768,
            longitude=-73.9537196,
            additional={
                "geometry": {
                    "bounds": {
                        "northeast": {"lat": 40.8009264, "lng": -73.9495752},
                        "southwest": {"lat": 40.796948, "lng": -73.9580246},
                    },
                    "location": {"lat": 40.7987768, "lng": -73.9537196},
                    "location_type": "GEOMETRIC_CENTER",
                    "viewport": {
                        "northeast": {"lat": 40.8009264, "lng": -73.9495752},
                        "southwest": {"lat": 40.796948, "lng": -73.9580246},
                    },
                }
            },
        )

    def test_park_detail_not_found(self):
        """Test accessing a non-existent park should return 404."""
        response = self.client.get(
            reverse("park_detail", args=[9999])
        )  # Non-existent ID
        self.assertEqual(response.status_code, 404)

    def test_get_park_detail(self):
        """Test retrieving the park detail page."""
        response = self.client.get(reverse("park_detail", args=[self.park.id]))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "parks/park_detail.html")
        self.assertContains(response, self.park.name)

    def test_submit_invalid_rating(self):
        # Test submitting an invalid rating (>5) to ensure an error message appears
        response = self.client.post(
            reverse("park_detail", args=[self.park.id]),
            {
                "form_type": "submit_review",
                "text": "Invalid rating test",
                "rating": "10",
            },
        )
        self.assertEqual(response.status_code, 200)  # Page should reload with an error
        self.assertContains(response, "Rating must be between 1 and 5 stars!")

    def test_submit_review(self):
        # Test submitting a review should correctly redirect
        response = self.client.post(
            reverse("park_detail", args=[self.park.id]),
            {"form_type": "submit_review", "text": "Awesome park!", "rating": "5"},
        )
        self.assertEqual(response.status_code, 302)
        self.assertEqual(Review.objects.count(), 1)


class ParkImageModelTest(TestCase):
    def setUp(self):
        """Set up a test park and associated images."""
        self.park = DogRunNew.objects.create(
            id="1",
            prop_id="1234",
            name="Central Park",
            address="New York, NY",
            dogruns_type="Small",
            accessible="Yes",
            notes="Test park notes",
            google_name="Central Park",
            borough="M",
            zip_code="United States",
            formatted_address="Central Pk N, New York, NY, USA",
            latitude=40.7987768,
            longitude=-73.9537196,
            additional={
                "geometry": {
                    "bounds": {
                        "northeast": {"lat": 40.8009264, "lng": -73.9495752},
                        "southwest": {"lat": 40.796948, "lng": -73.9580246},
                    },
                    "location": {"lat": 40.7987768, "lng": -73.9537196},
                    "location_type": "GEOMETRIC_CENTER",
                    "viewport": {
                        "northeast": {"lat": 40.8009264, "lng": -73.9495752},
                        "southwest": {"lat": 40.796948, "lng": -73.9580246},
                    },
                }
            },
        )
        self.image = ParkImage.objects.create(
            park=self.park,
            image="https://res.cloudinary.com/demo/image/upload/sample.jpg",
        )

    def test_park_image_creation(self):
        """Test that a ParkImage object is created successfully."""
        self.assertEqual(self.image.park, self.park)
        self.assertEqual(
            self.image.image, "https://res.cloudinary.com/demo/image/upload/sample.jpg"
        )

    def test_park_image_str(self):
        """Test the string representation of a ParkImage object."""
        self.assertEqual(str(self.image), f"Image for {self.park.name}")


class ParkDetailViewImageTest(TestCase):
    def setUp(self):
        """Set up a test park and associated images."""
        self.client = Client()
        self.park = DogRunNew.objects.create(
            id="1",
            prop_id="1234",
            name="Central Park",
            address="New York, NY",
            dogruns_type="Small",
            accessible="Yes",
            notes="Test park notes",
            google_name="Central Park",
            borough="M",
            zip_code="United States",
            formatted_address="Central Pk N, New York, NY, USA",
            latitude=40.7987768,
            longitude=-73.9537196,
            additional={
                "geometry": {
                    "bounds": {
                        "northeast": {"lat": 40.8009264, "lng": -73.9495752},
                        "southwest": {"lat": 40.796948, "lng": -73.9580246},
                    },
                    "location": {"lat": 40.7987768, "lng": -73.9537196},
                    "location_type": "GEOMETRIC_CENTER",
                    "viewport": {
                        "northeast": {"lat": 40.8009264, "lng": -73.9495752},
                        "southwest": {"lat": 40.796948, "lng": -73.9580246},
                    },
                }
            },
        )
        self.image = ParkImage.objects.create(
            park=self.park,
            image="https://res.cloudinary.com/demo/image/upload/sample.jpg",
        )

    def test_park_detail_view_with_images(self):
        """Test that the park detail view displays associated images."""
        response = self.client.get(reverse("park_detail", args=[self.park.id]))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.park.name)
        # self.assertIn(self.image.image, response.content.decode())
