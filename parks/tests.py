from django.test import TestCase, Client
from django.urls import reverse

# from .models import DogRun

# class ParkModelTest(TestCase):
#     def setUp(self):
#         self.park = DogRun.objects.create(
#             name="Central Park",
#             location="New York, NY",
#             description="A large public park in New York City."
#         )

#     def test_park_creation(self):
#         self.assertEqual(self.park.name, "Central Park")
#         self.assertEqual(self.park.location, "New York, NY")
#         self.assertEqual(self.park.description, "A large public park.")

# class ParkListViewTest(TestCase):
#     def setUp(self):
#         self.client = Client()
#         self.park = DogRun.objects.create(
#             name="Central Park",
#             location="New York, NY",
#             description="A large public park in New York City."
#         )

#     def test_park_list_view(self):
#         response = self.client.get(reverse("park_list"))
#         self.assertEqual(response.status_code, 200)
#         self.assertContains(response, "Central Park")

# class ParkDetailViewTest(TestCase):
#     def setUp(self):
#         self.client = Client()
#         self.park = DogRun.objects.create(
#             name="Central Park",
#             location="New York, NY",
#             description="A large public park in New York City."
#         )

#     def test_park_detail_view(self):
#         response = self.client.get(reverse("park_detail", args=[self.park.id]))
#         self.assertEqual(response.status_code, 200)
#         self.assertContains(response, "Central Park")
#         self.assertContains(response, "New York, NY")
#         self.assertContains(response, "A large public park in New York City.")

# class MapViewTest(TestCase):
#     def setUp(self):
#         self.client = Client()

#     def test_map_view(self):
#         response = self.client.get(reverse("map"))
#         self.assertEqual(response.status_code, 200)


class CombinedViewTest(TestCase):
    def setUp(self):
        self.client = Client()

    def test_combined_view(self):
        response = self.client.get(reverse("park_and_map"))
        self.assertEqual(response.status_code, 200)
