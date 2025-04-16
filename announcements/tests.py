from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from django.utils import timezone
from .models import Announcement


class AnnouncementModelTest(TestCase):
    def setUp(self):
        self.admin_user = User.objects.create_user(
            username="adminuser", password="AdminPass123", is_staff=True
        )
        self.announcement = Announcement.objects.create(
            title="Test Announcement",
            content="This is a test announcement.",
            author=self.admin_user,
            pinned=True,
            expiry_date=timezone.now() + timezone.timedelta(days=7),
        )

    def test_announcement_str(self):
        """Ensure the string representation returns the title."""
        self.assertEqual(str(self.announcement), "Test Announcement")


class AnnouncementViewTests(TestCase):
    def setUp(self):
        self.client = Client()
        # Create an admin and a normal user
        self.admin_user = User.objects.create_user(
            username="adminuser", password="AdminPass123", is_staff=True
        )
        self.normal_user = User.objects.create_user(
            username="normaluser", password="NormalPass123", is_staff=False
        )
        # Create an announcement by admin
        self.announcement = Announcement.objects.create(
            title="Admin Announcement",
            content="Announcement content",
            author=self.admin_user,
            pinned=False,
            expiry_date=timezone.now() + timezone.timedelta(days=2),
        )

    def test_announcements_list_view_as_anonymous(self):
        """
        The announcements list should be accessible by any user (even anonymous).
        """
        url = reverse("announcements_list")
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.announcement.title)

    def test_create_announcement_view_as_admin(self):
        """
        Admin users should be able to create an announcement.
        """
        self.client.login(username="adminuser", password="AdminPass123")
        url = reverse("create_announcement")
        expiry = (timezone.now() + timezone.timedelta(days=3)).strftime(
            "%Y-%m-%dT%H:%M"
        )
        data = {
            "title": "New Announcement",
            "content": "New announcement content",
            "pinned": True,
            "expiry_date": expiry,
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, 302)
        self.assertTrue(Announcement.objects.filter(title="New Announcement").exists())

    def test_create_announcement_view_as_non_admin(self):
        """
        Normal (non-admin) users should not have access to create announcements.
        """
        self.client.login(username="normaluser", password="NormalPass123")
        url = reverse("create_announcement")
        response = self.client.get(url)
        self.assertEqual(response.status_code, 403)

    def test_edit_announcement_view(self):
        """
        Admin users should be able to edit announcements.
        """
        self.client.login(username="adminuser", password="AdminPass123")
        url = reverse("edit_announcement", args=[self.announcement.id])
        new_expiry = (timezone.now() + timezone.timedelta(days=5)).strftime(
            "%Y-%m-%dT%H:%M"
        )
        data = {
            "title": "Edited Announcement",
            "content": "Edited content",
            "pinned": False,
            "expiry_date": new_expiry,
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, 302)
        self.announcement.refresh_from_db()
        self.assertEqual(self.announcement.title, "Edited Announcement")

    def test_delete_announcement_view(self):
        """
        Admin users should be able to delete an announcement.
        """
        self.client.login(username="adminuser", password="AdminPass123")
        url = reverse("delete_announcement", args=[self.announcement.id])
        response = self.client.post(url)
        self.assertEqual(response.status_code, 302)
        self.assertFalse(Announcement.objects.filter(id=self.announcement.id).exists())
