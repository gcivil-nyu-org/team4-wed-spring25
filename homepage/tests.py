from django.test import TestCase, Client
from django.urls import reverse


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

    def test_db_connection(self):
        response = self.client.get(reverse("test_db_connection"))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["status"], "success")
        # else:
        #     self.assertEqual(response.status_code, 500)
        #     self.assertEqual(response.json()["status"], "error")


class HelloWorldTest(TestCase):
    def setUp(self):
        self.client = Client()

    def test_home_page(self):
        response = self.client.get(reverse("home"))
        self.assertEqual(response.status_code, 200)


class ContactPageTest(TestCase):
    def setUp(self):
        self.client = Client()

    def test_contact_page(self):
        response = self.client.get(reverse("contact"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "parks/contact.html")
        self.assertContains(response, "Get in Touch")
        self.assertContains(response, "Have questions or suggestions?")

        # Check if the "Back to Home" button exists
        self.assertContains(
            response,
            'href="' + reverse("home") + '"',
            msg_prefix="Home button is missing",
        )
