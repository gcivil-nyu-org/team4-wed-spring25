from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from .models import DogRunNew, Review, ParkImage, ReviewReport, ImageReport, Reply
from parks.templatetags.display_rating import render_stars
from parks.templatetags import image_filters
from django.utils.text import slugify
from django.core import mail
from django.contrib.messages import get_messages

from django.utils import timezone
from datetime import timedelta
from parks.models import ParkPresence

from unittest.mock import patch
from django.core.files.uploadedfile import SimpleUploadedFile

from cloudinary import config as cloudinary_config


@patch(
    "cloudinary.uploader.upload",
    return_value={
        "asset_id": "dummy_asset_id",
        "public_id": "dummy_id",
        "version": "1234567890",
        "signature": "dummy_signature",
        "width": 800,
        "height": 600,
        "format": "jpg",
        "resource_type": "image",
        "type": "upload",
        "secure_url": "https://res.cloudinary.com/demo/image/upload/sample.jpg",
        "url": "https://res.cloudinary.com/demo/image/upload/sample.jpg",
    },
)
class ErrorPageTests(TestCase):
    def test_trigger_400(self):
        response = self.client.get("/test400/")
        self.assertEqual(response.status_code, 400)
        self.assertTemplateUsed(response, "400.html")

    def test_trigger_403(self):
        response = self.client.get("/test403/")
        self.assertEqual(response.status_code, 403)
        self.assertTemplateUsed(response, "403.html")

    def test_trigger_404(self):
        response = self.client.get("/test404/")
        self.assertEqual(response.status_code, 404)
        self.assertTemplateUsed(response, "404.html")

    def test_trigger_500(self):
        response = self.client.get("/test500/")
        self.assertEqual(response.status_code, 500)
        self.assertTemplateUsed(response, "500.html")


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
        Ensure that posting an email to password_reset
        sends the user to password_reset_done,
        and optionally check that an email was
        "sent" (console backend or etc.)
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
            display_name="Central Park",
            slug=slugify(f"{'Central Park'}-{'1234'}"),
        )

    def test_park_creation(self):
        self.assertEqual(self.park.name, "Central Park")
        self.assertEqual(self.park.address, "New York, NY")
        self.assertEqual(self.park.notes, "Test park notes")
        self.assertEqual(self.park.slug, "central-park-1234")


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
            display_name="Brooklyn Park",
            slug=slugify(f"{'Brooklyn Park'}-{'5678'}"),
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
            display_name="Central Park",
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
            display_name="Brooklyn Bridge Park",
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
            display_name="Central Park",
            slug="central-park-1234",
        )

        self.park2 = DogRunNew.objects.create(
            id="2",
            prop_id="4321",
            name="Allison Pond Park",
            address="Staten Island",
            dogruns_type="Small",
            accessible="Yes",
            notes="Test park notes",
            google_name="Allison Pond Park",
            borough="Q",
            zip_code="United States",
            formatted_address="Allison Pond Park, Staten Island, NY 10301, USA",
            latitude=40.7987768,
            longitude=-73.9537196,
            display_name="Allison Pond Park",
            slug="allison-pond-park-4321",
        )

    def test_park_detail_page_loads(self):
        url = self.park.detail_page_url()
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "parks/park_detail.html")
        self.assertContains(response, "Central Park")

    def test_redirect_on_wrong_slug(self):
        url = reverse("park_detail", kwargs={"slug": "wrong-slug", "id": self.park.id})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 301)

        correct_response = url = reverse(
            "park_detail", kwargs={"slug": self.park.slug, "id": self.park.id}
        )

        self.assertRedirects(response, correct_response, status_code=301)

    def test_404_on_nonexistent_id(self):
        url = reverse("park_detail", kwargs={"slug": "central-park", "id": "-4"})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)

    def test_redirect_on_wrong_id_right_slug(self):
        url = reverse(
            "park_detail", kwargs={"slug": "central-park", "id": self.park2.id}
        )
        response = self.client.get(url)

        self.assertEqual(response.status_code, 301)

        expected_url = reverse(
            "park_detail", kwargs={"slug": self.park2.slug, "id": self.park2.id}
        )
        self.assertRedirects(
            response, expected_url, status_code=301, target_status_code=200
        )

    from django.contrib.messages import get_messages


def test_submit_review_non_integer_rating(self):
    self.client.login(username="testuser", password="testpass")

    response = self.client.post(
        self.park.detail_page_url(),
        {
            "form_type": "submit_review",
            "text": "This should not go through.",
            "rating": "abc",
        },
        follow=True,
    )

    self.assertEqual(response.status_code, 200)

    messages = list(get_messages(response.wsgi_request))
    self.assertTrue(
        any("Please select a rating before submitting." in str(m) for m in messages),
        "Expected error message not found in messages.",
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
            reverse("park_detail", args=[self.park.slug, self.park.id]),
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
            reverse("park_detail", args=[self.park.slug, self.park.id]),
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

    def test_duplicate_review_report(self):
        # First report
        response1 = self.client.post(
            reverse("park_detail", args=[self.park.slug, self.park.id]),
            {
                "form_type": "report_review",
                "review_id": self.review.id,
                "reason": "Spam",
            },
        )
        self.assertEqual(response1.status_code, 302)
        self.assertEqual(self.review.reports.count(), 1)

        # Second report by same user
        response2 = self.client.post(
            reverse("park_detail", args=[self.park.slug, self.park.id]),
            {
                "form_type": "report_review",
                "review_id": self.review.id,
                "reason": "Still spam",
            },
        )
        self.assertEqual(response2.status_code, 302)
        self.assertEqual(self.review.reports.count(), 1)  # should still be 1

    def test_duplicate_image_report(self):
        # First report
        response1 = self.client.post(
            reverse("report_image", args=[self.image.id]),
            {"reason": "Bad image"},
        )
        self.assertEqual(response1.status_code, 302)
        self.assertEqual(self.image.reports.count(), 1)

        # Second report by same user
        response2 = self.client.post(
            reverse("report_image", args=[self.image.id]),
            {"reason": "Still bad"},
        )
        self.assertEqual(response2.status_code, 302)
        self.assertEqual(self.image.reports.count(), 1)  # should still be 1


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
        response = self.client.get(
            reverse("park_detail", args=[self.park.slug, self.park.id])
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.park.name)
        # self.assertIn(self.image.image, response.content.decode())


class ParkDetailDisplayedReviewsTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username="reviewer", password="pass123")

        self.park = DogRunNew.objects.create(
            id="10",
            prop_id="PARK100",
            name="Test Park",
            address="100 Test St",
            dogruns_type="Run",
            accessible="Yes",
            notes="Some notes",
            google_name="Test Park",
            borough="M",
            zip_code="10001",
            formatted_address="100 Test St, New York, NY",
            latitude=40.7128,
            longitude=-74.0060,
            display_name="Test Park",
            slug=slugify("Test Park-PARK100"),
        )

        # One visible review
        self.review_visible = Review.objects.create(
            park=self.park,
            user=self.user,
            text="This park is great!",
            rating=5,
            is_removed=False,
        )

        # One soft-deleted review
        self.review_removed = Review.objects.create(
            park=self.park,
            user=self.user,
            text="This review should be hidden",
            rating=1,
            is_removed=True,
        )

    def test_only_visible_reviews_displayed(self):
        url = reverse("park_detail", args=[self.park.slug, self.park.id])
        response = self.client.get(url)

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.review_visible.text)
        self.assertNotContains(response, self.review_removed.text)

    def test_average_rating_excludes_removed_reviews(self):
        url = reverse("park_detail", args=[self.park.slug, self.park.id])
        response = self.client.get(url)

        # Ensure the average is based only on the 5-star review
        self.assertContains(response, "5.0")


class RenderStarsTests(TestCase):
    def test_int_stars(self):
        size = 20
        result = render_stars(4, size)
        self.assertEqual(result["filled_stars"], 4)
        self.assertEqual(result["half_stars"], 0)
        self.assertEqual(result["empty_stars"], 1)
        self.assertEqual(result["size"], size)

    def test_full_stars(self):
        size = 15
        result = render_stars(5, size)
        self.assertEqual(result["filled_stars"], 5)
        self.assertEqual(result["half_stars"], 0)
        self.assertEqual(result["empty_stars"], 0)
        self.assertEqual(result["size"], size)

    def test_no_stars(self):
        size = 10
        result = render_stars(0, size)
        self.assertEqual(result["filled_stars"], 0)
        self.assertEqual(result["half_stars"], 0)
        self.assertEqual(result["empty_stars"], 5)
        self.assertEqual(result["size"], size)

    def test_half_stars(self):
        size = 20
        result = render_stars(2.5, size)
        self.assertEqual(result["filled_stars"], 2)
        self.assertEqual(result["half_stars"], 1)
        self.assertEqual(result["empty_stars"], 2)
        self.assertEqual(result["size"], size)

    # >= X.25 -> one half star
    def test_round_up_to_half(self):
        size = 20
        result = render_stars(4.25, size)
        self.assertEqual(result["filled_stars"], 4)
        self.assertEqual(result["half_stars"], 1)
        self.assertEqual(result["empty_stars"], 0)
        self.assertEqual(result["size"], size)

    # < X.25 -> round down to whole
    def test_round_down_to_whole(self):
        size = 20
        result = render_stars(3.24, size)
        self.assertEqual(result["filled_stars"], 3)
        self.assertEqual(result["half_stars"], 0)
        self.assertEqual(result["empty_stars"], 2)
        self.assertEqual(result["size"], size)

    # < X.75 -> one half star
    def test_round_down_to_half(self):
        size = 20
        result = render_stars(2.74, size)
        self.assertEqual(result["filled_stars"], 2)
        self.assertEqual(result["half_stars"], 1)
        self.assertEqual(result["empty_stars"], 2)
        self.assertEqual(result["size"], size)

    # >= X.75 -> round up to next whole
    def test_round_up_to_whole(self):
        size = 20
        result = render_stars(4.75, size)
        self.assertEqual(result["filled_stars"], 5)
        self.assertEqual(result["half_stars"], 0)
        self.assertEqual(result["empty_stars"], 0)
        self.assertEqual(result["size"], size)


class ParkPresenceTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username="tester", password="testpass")
        self.park = DogRunNew.objects.create(
            id="5",
            prop_id="5566",
            name="Test Dog Park",
            address="Test Location",
            dogruns_type="All",
            accessible="Yes",
            formatted_address="Test Address",
            latitude=40.0,
            longitude=-73.0,
            display_name="Test Dog Park",
            slug="test-dog-park-5566",
        )
        self.client.login(username="tester", password="testpass")

    def test_user_check_in_creates_presence(self):
        self.client.post(
            reverse("park_detail", args=[self.park.slug, self.park.id]),
            {"form_type": "check_in"},
        )
        presences = ParkPresence.objects.filter(user=self.user, park=self.park)
        self.assertEqual(presences.count(), 1)
        self.assertEqual(presences.first().status, "current")

    def test_user_be_there_at_creates_presence(self):
        future_time = (timezone.now() + timedelta(minutes=20)).strftime("%H:%M")
        self.client.post(
            reverse("park_detail", args=[self.park.slug, self.park.id]),
            {"form_type": "be_there_at", "time": future_time},
        )
        presences = ParkPresence.objects.filter(user=self.user, park=self.park)
        self.assertEqual(presences.count(), 1)
        self.assertEqual(presences.first().status, "on_the_way")


@patch(
    "cloudinary.uploader.upload",
    return_value={
        "asset_id": "dummy_asset_id",
        "public_id": "dummy_id",
        "version": "1234567890",
        "signature": "dummy_signature",
        "width": 800,
        "height": 600,
        "format": "jpg",
        "resource_type": "image",
        "type": "upload",
        "secure_url": "https://dummy.cloudinary.com/image.jpg",
        "url": "http://dummy.cloudinary.com/image.jpg",
    },
)
class ImageUploadTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username="uploader", password="pass123")
        self.client.login(username="uploader", password="pass123")
        self.park = DogRunNew.objects.create(
            id="20",
            prop_id="8888",
            name="Mock Park",
            address="123",
            dogruns_type="All",
            accessible="Yes",
            formatted_address="123",
            latitude=40.0,
            longitude=-73.0,
            slug="mock-park-8888",
            display_name="Mock Park",
        )

    def test_upload_image_with_review(self, mock_upload):
        cloudinary_config(
            cloud_name="demo",
            api_key="fake_api_key",
            api_secret="fake_api_secret",
        )

        image = SimpleUploadedFile(
            "test.jpg", b"file_content", content_type="image/jpeg"
        )

        response = self.client.post(
            reverse("park_detail", args=[self.park.slug, self.park.id]),
            {
                "form_type": "submit_review",
                "text": "Nice park!",
                "rating": "5",
                "images": image,
            },
            follow=True,
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(ParkImage.objects.count(), 1)


class ModalInteractionTests(TestCase):
    def test_modal_js_is_present(self):
        client = Client()
        park = DogRunNew.objects.create(
            id="7",
            prop_id="3344",
            name="Modal Park",
            address="JSville",
            dogruns_type="Small",
            accessible="Yes",
            formatted_address="JS Road",
            latitude=42.0,
            longitude=-75.0,
            display_name="Modal Park",
            slug="modal-park-3344",
        )
        response = client.get(reverse("park_detail", args=[park.slug, park.id]))
        self.assertContains(response, "function openCarouselImageModal")
        self.assertContains(response, "imagePreviewModal")
        self.assertContains(response, "modalImage")


class ReplaceFilterTests(TestCase):
    def test_replace_basic(self):
        result = image_filters.replace("hello world", "world,there")
        self.assertEqual(result, "hello there")

    def test_replace_partial_match(self):
        result = image_filters.replace("abcabcabc", "a,x")
        self.assertEqual(result, "xbcxbcxbc")

    def test_replace_only_first_comma_splits(self):
        result = image_filters.replace("one,two,three", "two,2")
        self.assertEqual(result, "one,2,three")

    def test_replace_with_comma_in_replacement(self):
        result = image_filters.replace("item1,item2", "item1,x,y")
        self.assertEqual(result, "x,y,item2")  # Splits only on first comma

    def test_replace_no_match(self):
        result = image_filters.replace("hello", "z,x")
        self.assertEqual(result, "hello")


class ReplyViewTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username="testuser", password="testpass")
        self.park = DogRunNew.objects.create(
            id="99",
            prop_id="9999",
            name="Reply Park",
            address="Somewhere",
            dogruns_type="All",
            accessible="Yes",
            formatted_address="Reply Address",
            latitude=40.0,
            longitude=-73.0,
            slug="reply-park-9999",
        )
        self.review = Review.objects.create(
            park=self.park, text="Original Review", rating=4, user=self.user
        )
        self.park_detail_url = reverse(
            "park_detail", args=[self.park.slug, self.park.id]
        )

    def test_submit_reply_to_review(self):
        self.client.login(username="testuser", password="testpass")
        response = self.client.post(
            self.park_detail_url,
            {
                "form_type": "submit_reply",
                "parent_review_id": self.review.id,
                "reply_text": "This is a reply to a review.",
            },
        )
        self.assertEqual(response.status_code, 302)
        self.assertTrue(
            Reply.objects.filter(
                review=self.review, text="This is a reply to a review."
            ).exists()
        )

    def test_submit_nested_reply_to_reply(self):
        parent_reply = Reply.objects.create(
            review=self.review, user=self.user, text="Parent reply"
        )
        self.client.login(username="testuser", password="testpass")
        response = self.client.post(
            self.park_detail_url,
            {
                "form_type": "submit_reply",
                "parent_review_id": self.review.id,
                "parent_reply_id": parent_reply.id,
                "reply_text": "Child reply",
            },
        )
        self.assertEqual(response.status_code, 302)
        self.assertTrue(
            Reply.objects.filter(parent_reply=parent_reply, text="Child reply").exists()
        )

    def test_submit_reply_with_invalid_parent_reply_id(self):
        self.client.login(username="testuser", password="testpass")
        response = self.client.post(
            self.park_detail_url,
            {
                "form_type": "submit_reply",
                "parent_review_id": self.review.id,
                "parent_reply_id": 9999,
                "reply_text": "Fallback to review",
            },
        )
        self.assertEqual(response.status_code, 302)
        reply = Reply.objects.get(text="Fallback to review")
        self.assertIsNone(reply.parent_reply)

    def test_submit_reply_without_text(self):
        self.client.login(username="testuser", password="testpass")
        response = self.client.post(
            self.park_detail_url,
            {
                "form_type": "submit_reply",
                "parent_review_id": self.review.id,
                "reply_text": "   ",
            },
        )
        self.assertEqual(response.status_code, 302)
        self.assertEqual(Reply.objects.filter(review=self.review).count(), 0)

    def test_submit_reply_unauthenticated(self):
        response = self.client.post(
            self.park_detail_url,
            {
                "form_type": "submit_reply",
                "parent_review_id": self.review.id,
                "reply_text": "Unauthorized reply",
            },
        )
        self.assertEqual(response.status_code, 200)
        self.assertNotIn("Reply submitted successfully", response.content.decode())

    def test_delete_own_reply(self):
        self.client.login(username="testuser", password="testpass")
        reply = Reply.objects.create(
            review=self.review, user=self.user, text="To be deleted"
        )
        response = self.client.post(reverse("delete_reply", args=[reply.id]))
        self.assertEqual(response.status_code, 302)
        self.assertFalse(Reply.objects.filter(id=reply.id).exists())

    def test_delete_others_reply_forbidden(self):
        other = User.objects.create_user(username="other", password="pass")
        reply = Reply.objects.create(review=self.review, user=other, text="Not yours")
        self.client.login(username="testuser", password="testpass")
        response = self.client.post(reverse("delete_reply", args=[reply.id]))
        self.assertEqual(response.status_code, 302)
        self.assertTrue(Reply.objects.filter(id=reply.id).exists())

    def test_report_reply_success(self):
        other = User.objects.create_user(username="other", password="pass")
        reply = Reply.objects.create(review=self.review, user=other, text="Report me")
        self.client.login(username="testuser", password="testpass")
        response = self.client.post(
            reverse("report_reply", args=[reply.id]), {"reason": "Spam"}
        )
        self.assertEqual(response.status_code, 302)
        self.assertTrue(reply.reports.exists())

    def test_report_own_reply_fails(self):
        reply = Reply.objects.create(
            review=self.review, user=self.user, text="Self report"
        )
        self.client.login(username="testuser", password="testpass")
        response = self.client.post(
            reverse("report_reply", args=[reply.id]), {"reason": "Oops"}
        )
        self.assertEqual(response.status_code, 302)
        self.assertEqual(reply.reports.count(), 0)
