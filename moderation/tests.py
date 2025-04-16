from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from parks.models import DogRunNew, Review, ReviewReport

# Create your tests here.


class ModerationTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.admin = User.objects.create_user(username="admin", password="pass")
        self.admin.is_staff = True
        self.admin.save()

        self.user = User.objects.create_user(username="user", password="pass")

        self.park = DogRunNew.objects.create(
            id="p1",
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
