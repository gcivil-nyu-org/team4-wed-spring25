from django.test import TestCase, Client
from django.urls import reverse


class HealthCheckTest(TestCase):
    def setUp(self):
        self.client = Client()

    def test_health_check(self):
        response = self.client.get(reverse("health_check"))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {"status": "ok"})


# class TestDBConnectionTest(TestCase):
#     def setUp(self):
#         self.client = Client()

#     def test_db_connection(self):
#         response = self.client.get(reverse("test_db_connection"))
#         self.assertEqual(response.status_code, 200)
#         self.assertEqual(response.json()["status"], "success")


class HelloWorldTest(TestCase):
    def setUp(self):
        self.client = Client()

    def test_hello_world(self):
        response = self.client.get(reverse("hello_world"))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content.decode(), "Hello World")
