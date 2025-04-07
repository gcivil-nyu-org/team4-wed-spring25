from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from .models import DogRunNew, Review, ParkImage, ReviewReport, ImageReport
from django.core import mail


# import os
class UniqueEmailTests(TestCase):
    def setUp(self):
        self.client = Client()
        User.objects.create_user(
            username="existinguser",
            email="duplicate@pawpark.com",
            password="SomeStrongPassword1",
        )
        self.register_url = reverse("register")

    def test_duplicate_email_registration(self):
        """
        Attempting to register a new user with an email that already exists should
        re-render the form with an error message.
        """
        response = self.client.post(
            self.register_url,
            {
                "username": "newuser",
                "email": "duplicate@pawpark.com",
                "password1": "StrongPass123",
                "password2": "StrongPass123",
                "role": "user",
                "admin_access_code": "",
            },
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "A user with that email address already exists.")
        self.assertFalse(User.objects.filter(username="newuser").exists())


class WeakPasswordTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.register_url = reverse("register")

    def test_too_short_password(self):
        response = self.client.post(
            self.register_url,
            {
                "username": "weakuser",
                "password1": "123",
                "password2": "123",
                "role": "user",
            },
        )
        self.assertEqual(response.status_code, 200)
        self.assertFalse(User.objects.filter(username="weakuser").exists())
        self.assertContains(response, "must contain at least 8 characters")

    def test_entirely_numeric_password(self):
        response = self.client.post(
            self.register_url,
            {
                "username": "numericuser",
                "password1": "12345678",
                "password2": "12345678",
                "role": "user",
            },
        )
        self.assertEqual(response.status_code, 200)
        self.assertFalse(User.objects.filter(username="numericuser").exists())
        self.assertContains(response, "can’t be entirely numeric")


class PasswordResetTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            "resetuser", "reset@pawpark.com", "Pass123456"
        )

    def test_password_reset_page_loads(self):
        url = reverse("password_reset")
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "registration/password_reset_form.html")

    def test_password_reset_flow(self):
        """
        Ensure that posting an email to password_reset sends the user to password_reset_done,
        and optionally check that an email was "sent" (console backend or etc.)
        """
        url = reverse("password_reset")
        response = self.client.post(url, {"email": "reset@pawpark.com"})
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse("password_reset_done"))

        self.assertEqual(len(mail.outbox), 1)
        self.assertIn("resetuser", mail.outbox[0].body)


class AdminSignUpTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.register_url = reverse("register")

    def test_admin_signup_with_correct_code(self):
        """
        Signing up as admin with correct access code should create a staff user.
        """
        response = self.client.post(
            self.register_url,
            {
                "username": "adminuser",
                "password1": "StrongAdminPass123",
                "password2": "StrongAdminPass123",
                "role": "admin",
                "admin_access_code": "SUPERDOG123",
            },
        )
        self.assertEqual(response.status_code, 302)
        self.assertTrue(User.objects.filter(username="adminuser").exists())
        user = User.objects.get(username="adminuser")
        self.assertTrue(user.is_staff)

    def test_admin_signup_with_wrong_code(self):
        """
        Signing up as admin with wrong code should fail and not create staff user.
        """
        response = self.client.post(
            self.register_url,
            {
                "username": "fakeadmin",
                "password1": "StrongAdminPass123",
                "password2": "StrongAdminPass123",
                "role": "admin",
                "admin_access_code": "WRONGCODE",
            },
        )
        self.assertEqual(response.status_code, 200)
        self.assertFalse(User.objects.filter(username="fakeadmin").exists())

    def test_signup_as_normal_user_ignores_access_code(self):
        """
        If someone chooses 'user' role, the admin_access_code is irrelevant.
        """
        response = self.client.post(
            self.register_url,
            {
                "username": "normaluser",
                "password1": "StrongPass456",
                "password2": "StrongPass456",
                "role": "user",
                "admin_access_code": "SUPERDOG123",
            },
        )
        self.assertEqual(response.status_code, 302)
        self.assertTrue(User.objects.filter(username="normaluser").exists())
        user = User.objects.get(username="normaluser")
        self.assertFalse(user.is_staff)


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
        self.user = User.objects.create_user(username="testuser", password="123456abc")
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
            park=self.park, text="Great park!", rating=5, user=self.user
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
    def test_combined_view(self):
        response = self.client.get(reverse("park_and_map"))
        self.assertEqual(response.status_code, 200)

    def setUp(self):
        self.client = Client()
        # One park in Manhattan
        self.park_manhattan = DogRunNew.objects.create(
            id="1",
            prop_id="1234",
            name="Central Park",
            address="New York, NY",
            dogruns_type="Small",
            accessible="Yes",
            notes="Manhattan park",
            google_name="Central Park",
            borough="M",
            zip_code="10024",
            latitude=40.7987768,
            longitude=-73.9537196,
        )
        # One park in Brooklyn
        self.park_brooklyn = DogRunNew.objects.create(
            id="2",
            prop_id="5678",
            name="Brooklyn Bridge Park",
            address="Brooklyn, NY",
            dogruns_type="Large",
            accessible="Yes",
            notes="Brooklyn park",
            google_name="Brooklyn Bridge Park",
            borough="B",
            zip_code="11201",
            latitude=40.700292,
            longitude=-73.996123,
        )

    def test_combined_view_filters_by_borough(self):
        response = self.client.get(reverse("park_and_map"), {"borough": "M"})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Central Park")
        self.assertNotContains(response, "Brooklyn Bridge Park")


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


class ReportFunctionalityTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username="reporter", password="testpass123"
        )
        self.other_user = User.objects.create_user(
            username="uploader", password="testpass123"
        )

        self.park = DogRunNew.objects.create(
            id="10",
            prop_id="9999",
            name="Test Park",
            address="Test Address",
            dogruns_type="All",
            accessible="Yes",
            formatted_address="Test Address",
            latitude=40.0,
            longitude=-73.0,
        )

        self.image = ParkImage.objects.create(
            park=self.park,
            image="https://res.cloudinary.com/demo/image/upload/sample.jpg",
            user=self.other_user,
        )

        self.review = Review.objects.create(
            park=self.park, text="Nice place!", rating=4, user=self.other_user
        )

        self.client.login(username="reporter", password="testpass123")

    def test_report_image_creates_record(self):
        response = self.client.post(
            reverse("report_image", args=[self.image.id]),
            {"reason": "Inappropriate image"},
        )
        self.assertEqual(response.status_code, 302)
        self.assertEqual(self.image.reports.count(), 1)
        report = self.image.reports.first()
        self.assertEqual(report.reason, "Inappropriate image")
        self.assertEqual(report.user, self.user)

    def test_report_review_creates_record(self):
        response = self.client.post(
            reverse("park_detail", args=[self.park.id]),
            {
                "form_type": "report_review",
                "review_id": self.review.id,
                "reason": "Offensive content",
            },
        )
        self.assertEqual(response.status_code, 302)
        self.assertEqual(self.review.reports.count(), 1)
        report = self.review.reports.first()
        self.assertEqual(report.reason, "Offensive content")
        self.assertEqual(report.reported_by, self.user)

    def test_submit_review(self):
        response = self.client.post(
            reverse("park_detail", args=[self.park.id]),
            {"form_type": "submit_review", "text": "Another review!", "rating": "5"},
        )
        self.assertEqual(response.status_code, 302)
        self.assertEqual(Review.objects.filter(park=self.park).count(), 2)

    def test_review_report_str(self):
        report = ReviewReport.objects.create(
            review=self.review, reported_by=self.user, reason="Inappropriate content"
        )
        self.assertIn("Reported by", str(report))
        self.assertIn(str(self.review.id), str(report))

    def test_image_report_str(self):
        report = ImageReport.objects.create(
            image=self.image, user=self.user, reason="Offensive image"
        )
        self.assertIn("Report by", str(report))
        self.assertIn(str(self.image.id), str(report))

    def test_missing_reason_does_not_create_report(self):
        self.client.login(username="user2", password="testpass")
        response = self.client.post(
            reverse("report_image", args=[self.image.id]),
            {"reason": ""},
        )
        self.assertEqual(ImageReport.objects.count(), 0)
        self.assertEqual(response.status_code, 302)


class DeleteTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username="deleter", password="123pass")
        self.client.login(username="deleter", password="123pass")

        self.park = DogRunNew.objects.create(
            id="22",
            prop_id="9988",
            name="Del Park",
            address="Somewhere",
            dogruns_type="All",
            accessible="Yes",
            formatted_address="Addr",
            latitude=40.0,
            longitude=-73.0,
        )
        self.review = Review.objects.create(
            park=self.park, text="Review", rating=4, user=self.user
        )
        self.image = ParkImage.objects.create(
            park=self.park,
            image="https://res.cloudinary.com/demo/image/upload/sample.jpg",
            user=self.user,
        )

    def test_delete_review(self):
        response = self.client.post(reverse("delete_review", args=[self.review.id]))
        self.assertEqual(response.status_code, 302)
        self.assertFalse(Review.objects.filter(id=self.review.id).exists())

    def test_delete_image(self):
        response = self.client.post(reverse("delete_image", args=[self.image.id]))
        self.assertEqual(response.status_code, 302)
        self.assertFalse(ParkImage.objects.filter(id=self.image.id).exists())


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
