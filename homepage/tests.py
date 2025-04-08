from django.test import TestCase, Client
from django.urls import reverse
from unittest.mock import patch

class HealthCheckTest(TestCase):
    def setUp(self):
        self.client = Client()

    def test_health_check(self):
        response = self.client.get(reverse("health_check"))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {"status": "ok"})


class TestDBConnectionTest(TestCase):
    def setUp(self):
        self.client = Client()

    def test_db_connection_success(self):
        response = self.client.get(reverse("test_db_connection"))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["status"], "success")

    def test_db_connection_failure(self):
        with patch("homepage.views.connection.cursor") as mock_cursor:
            mock_cursor.side_effect = Exception("Simulated DB failure")
            response = self.client.get(reverse("test_db_connection"))
            self.assertEqual(response.status_code, 500)
            self.assertEqual(response.json()["status"], "error")
            self.assertIn("Simulated DB failure", response.json()["message"])

class ContactPageTest(TestCase):
    def setUp(self):
        self.client = Client()

    def test_contact_page(self):
        response = self.client.get(reverse("contact"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "parks/contact.html")
        self.assertContains(response, "Get in Touch")
        self.assertContains(response, "Have questions or suggestions?")
        self.assertContains(response, "info@pawpark.com")
        self.assertContains(response, "+1 (234) 567-890")
        self.assertContains(response, "NYC, USA")

        # Check if the "Back to Home" button exists
        self.assertContains(
            response,
            'href="' + reverse("home") + '"',
            msg_prefix="Home button is missing",
        )
