from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from parks.models import DogRunNew, Review, ReviewReport, ImageReport, ParkImage

from django.utils import timezone

from unittest.mock import patch
from cloudinary import config as cloudinary_config


# Create your tests here.


class ModerationTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.admin = User.objects.create_user(username="admin", password="pass")
        self.admin.is_staff = True
        self.admin.save()

        self.user = User.objects.create_user(username="user", password="pass")

        self.park = DogRunNew.objects.create(
            id=1,
            prop_id="p1",
            name="Test Park",
            address="123 Park Ave",
            dogruns_type="All",
            accessible="Yes",
            notes="Test",
            display_name="Test Park",
            slug="test-park",
        )

        self.review = Review.objects.create(
            park=self.park, user=self.user, text="Bad review", rating=1
        )

    def test_dashboard_access_allowed_for_admin(self):
        self.client.login(username="admin", password="pass")
        res = self.client.get(reverse("moderation_dashboard"))
        self.assertEqual(res.status_code, 200)

    def test_dashboard_access_denied_for_non_admin(self):
        self.client.login(username="user", password="pass")
        res = self.client.get(reverse("moderation_dashboard"))
        self.assertEqual(res.status_code, 403)

    def test_remove_review_action(self):
        self.client.login(username="admin", password="pass")
        ReviewReport.objects.create(
            review=self.review, reported_by=self.user, reason="bad"
        )

        res = self.client.post(
            reverse("moderation_action"),
            {"action": "remove_review", "review_id": self.review.id},
        )

        self.assertRedirects(res, reverse("moderation_dashboard"))
        self.review.refresh_from_db()
        self.assertTrue(self.review.is_removed)
        self.assertEqual(self.review.removed_by, self.admin)
        self.assertEqual(ReviewReport.objects.count(), 0)

    def test_dismiss_report_action(self):
        self.client.login(username="admin", password="pass")
        ReviewReport.objects.create(
            review=self.review, reported_by=self.user, reason="meh"
        )
        self.review.is_removed = True
        self.review.save()

        res = self.client.post(
            reverse("moderation_action"),
            {"action": "dismiss_report", "review_id": self.review.id},
        )

        self.assertRedirects(res, reverse("moderation_dashboard"))
        self.review.refresh_from_db()
        self.assertFalse(self.review.is_removed)
        self.assertEqual(ReviewReport.objects.count(), 0)

    def test_invalid_action_does_not_change(self):
        self.client.login(username="admin", password="pass")

        res = self.client.post(
            reverse("moderation_action"),
            {"action": "invalid", "review_id": self.review.id},
        )

        self.assertRedirects(res, reverse("moderation_dashboard"))
        self.review.refresh_from_db()
        self.assertFalse(self.review.is_removed)

    def test_moderation_action_requires_post(self):
        self.client.login(username="admin", password="pass")
        res = self.client.get(reverse("moderation_action"))
        self.assertEqual(res.status_code, 405)

    def test_moderation_action_denied_for_non_admin(self):
        self.client.login(username="user", password="pass")
        res = self.client.post(
            reverse("moderation_action"),
            {"action": "remove_review", "review_id": self.review.id},
        )
        self.assertEqual(res.status_code, 403)

    def test_remove_review_already_removed_shows_warning(self):
        self.client.login(username="admin", password="pass")
        self.review.is_removed = True
        self.review.save()

        response = self.client.post(
            reverse("moderation_action"),
            {"action": "remove_review", "review_id": self.review.id},
            follow=True,
        )

        messages = list(response.context["messages"])
        self.assertTrue(any("already removed" in str(m) for m in messages))

    def test_dismiss_report_with_no_reports_shows_warning(self):
        self.client.login(username="admin", password="pass")

        response = self.client.post(
            reverse("moderation_action"),
            {"action": "dismiss_report", "review_id": self.review.id},
            follow=True,
        )

        messages = list(response.context["messages"])
        self.assertTrue(any("no reports to dismiss" in str(m) for m in messages))

    def test_remove_image_already_removed_shows_warning(self):
        self.client.login(username="admin", password="pass")

        image = ParkImage.objects.create(
            park=self.park,
            user=self.user,
            is_removed=True,
            removed_by=self.admin,
            removed_at=timezone.now(),
        )

        res = self.client.post(
            reverse("image_moderation_action"),
            {"action": "remove_image", "image_id": image.id},
            follow=True,
        )

        messages = list(res.context["messages"])
        self.assertTrue(any("already removed" in str(m) for m in messages))

    def test_dismiss_image_report_with_no_reports_shows_warning(self):
        self.client.login(username="admin", password="pass")

        image = ParkImage.objects.create(
            park=self.park,
            user=self.user,
        )

        res = self.client.post(
            reverse("image_moderation_action"),
            {"action": "dismiss_report", "image_id": image.id},
            follow=True,
        )

        messages = list(res.context["messages"])
        self.assertTrue(any("no reports to dismiss" in str(m) for m in messages))

    def test_invalid_image_action_shows_error(self):
        self.client.login(username="admin", password="pass")

        image = ParkImage.objects.create(
            park=self.park,
            user=self.user,
        )

        res = self.client.post(
            reverse("image_moderation_action"),
            {"action": "bad_action", "image_id": image.id},
            follow=True,
        )

        messages = list(res.context["messages"])
        self.assertTrue(any("Invalid Action" in str(m) for m in messages))


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
class ModerationImageTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.admin = User.objects.create_user(
            username="admin", password="pass", is_staff=True
        )
        self.user = User.objects.create_user(username="user", password="pass")
        self.park = DogRunNew.objects.create(
            id=1,
            prop_id="p1",
            name="Test Park",
            address="123 Park Ave",
            dogruns_type="All",
            accessible="Yes",
            notes="Test",
            display_name="Test Park",
            slug="test-park",
        )
        self.review = Review.objects.create(
            park=self.park, user=self.user, text="Bad review", rating=1
        )
        self.image = ParkImage.objects.create(
            park=self.park,
            user=self.user,
            review=self.review,
            image="test.jpg",
            is_removed=True,
            removed_by=self.admin,
            removed_at=timezone.now(),
        )

    def test_restore_removed_image(self, mock_upload):
        self.client.login(username="admin", password="pass")
        res = self.client.post(
            reverse("removed_image_action"),
            {"action": "restore_image", "image_id": self.image.id},
        )
        self.assertRedirects(res, reverse("moderation_dashboard"))
        self.image.refresh_from_db()
        self.assertFalse(self.image.is_removed)
        self.assertIsNone(self.image.removed_by)

    def test_permanently_delete_image(self, mock_upload):
        self.client.login(username="admin", password="pass")
        res = self.client.post(
            reverse("removed_image_action"),
            {"action": "delete_image", "image_id": self.image.id},
        )
        self.assertRedirects(res, reverse("moderation_dashboard"))
        self.assertFalse(ParkImage.objects.filter(id=self.image.id).exists())

    def test_remove_image_from_report(self, mock_upload):
        cloudinary_config(
            cloud_name="demo",
            api_key="fake_api_key",
            api_secret="fake_api_secret",
        )
        self.image.is_removed = False
        self.image.save()
        ImageReport.objects.create(image=self.image, user=self.user, reason="Bad image")
        self.client.login(username="admin", password="pass")
        res = self.client.post(
            reverse("image_moderation_action"),
            {"action": "remove_image", "image_id": self.image.id},
        )
        self.assertRedirects(res, reverse("moderation_dashboard"))
        self.image.refresh_from_db()
        self.assertTrue(self.image.is_removed)
        self.assertEqual(self.image.removed_by, self.admin)
        self.assertEqual(ImageReport.objects.count(), 0)

    def test_dismiss_image_report(self, mock_upload):
        self.image.is_removed = True
        self.image.save()
        ImageReport.objects.create(image=self.image, user=self.user, reason="Spam")
        self.client.login(username="admin", password="pass")
        res = self.client.post(
            reverse("image_moderation_action"),
            {"action": "dismiss_report", "image_id": self.image.id},
        )
        self.assertRedirects(res, reverse("moderation_dashboard"))
        self.image.refresh_from_db()
        self.assertFalse(self.image.is_removed)
        self.assertEqual(ImageReport.objects.count(), 0)


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
class RemovedContentTests(TestCase):
    def setUp(self):
        self.client = Client()

        self.admin = User.objects.create_user(
            username="admin", password="pass", is_staff=True
        )
        self.user = User.objects.create_user(username="user", password="pass")

        self.park = DogRunNew.objects.create(
            id=123,
            prop_id="123",
            name="Park",
            address="123",
            dogruns_type="All",
            accessible="Yes",
            display_name="Park",
            slug="park-123",
        )

        self.review = Review.objects.create(
            park=self.park,
            user=self.user,
            text="Removed review",
            rating=1,
            is_removed=True,
            removed_by=self.admin,
            removed_at=timezone.now(),
        )

        self.image = ParkImage.objects.create(
            park=self.park,
            user=self.user,
            review=self.review,
            image="test.jpg",
            is_removed=True,
            removed_by=self.admin,
            removed_at=timezone.now(),
        )

    def test_restore_review(self, _):
        cloudinary_config(
            cloud_name="demo",
            api_key="fake_api_key",
            api_secret="fake_api_secret",
        )
        self.client.login(username="admin", password="pass")
        res = self.client.post(
            reverse("removed_review_action"),
            {"action": "restore_review", "review_id": self.review.id},
        )
        self.assertRedirects(res, reverse("moderation_dashboard"))
        self.review.refresh_from_db()
        self.assertFalse(self.review.is_removed)

    def test_restore_review_not_removed(self, _):
        cloudinary_config(
            cloud_name="demo",
            api_key="fake_api_key",
            api_secret="fake_api_secret",
        )
        self.review.is_removed = False
        self.review.save()
        self.client.login(username="admin", password="pass")
        res = self.client.post(
            reverse("removed_review_action"),
            {"action": "restore_review", "review_id": self.review.id},
        )
        self.assertRedirects(res, reverse("moderation_dashboard"))

    def test_invalid_review_action(self, _):
        cloudinary_config(
            cloud_name="demo",
            api_key="fake_api_key",
            api_secret="fake_api_secret",
        )
        self.client.login(username="admin", password="pass")
        res = self.client.post(
            reverse("removed_review_action"),
            {"action": "bad_action", "review_id": self.review.id},
        )
        self.assertRedirects(res, reverse("moderation_dashboard"))

    def test_restore_image(self, _):
        cloudinary_config(
            cloud_name="demo",
            api_key="fake_api_key",
            api_secret="fake_api_secret",
        )
        self.client.login(username="admin", password="pass")
        res = self.client.post(
            reverse("removed_image_action"),
            {"action": "restore_image", "image_id": self.image.id},
        )
        self.assertRedirects(res, reverse("moderation_dashboard"))
        self.image.refresh_from_db()
        self.assertFalse(self.image.is_removed)

    def test_restore_image_not_removed(self, _):
        cloudinary_config(
            cloud_name="demo",
            api_key="fake_api_key",
            api_secret="fake_api_secret",
        )
        self.image.is_removed = False
        self.image.save()
        self.client.login(username="admin", password="pass")
        res = self.client.post(
            reverse("removed_image_action"),
            {"action": "restore_image", "image_id": self.image.id},
        )
        self.assertRedirects(res, reverse("moderation_dashboard"))

    def test_delete_image(self, _):
        self.client.login(username="admin", password="pass")
        res = self.client.post(
            reverse("removed_image_action"),
            {"action": "delete_image", "image_id": self.image.id},
        )
        self.assertRedirects(res, reverse("moderation_dashboard"))
        self.assertFalse(ParkImage.objects.filter(id=self.image.id).exists())

    def test_invalid_image_action(self, _):
        cloudinary_config(
            cloud_name="demo",
            api_key="fake_api_key",
            api_secret="fake_api_secret",
        )
        self.client.login(username="admin", password="pass")
        res = self.client.post(
            reverse("removed_image_action"),
            {"action": "wrong", "image_id": self.image.id},
        )
        self.assertRedirects(res, reverse("moderation_dashboard"))
