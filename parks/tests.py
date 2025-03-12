from django.test import TestCase, Client
from django.urls import reverse

from .models import DogRun
from parks.utilities import folium_cluster_styling


class ParkModelTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.park = DogRun.objects.create(
            id="1",
            prop_id="1234",
            name="Central Park",
            address="New York, NY",
            dogruns_type="Small",
            accessible="Yes",
            notes="Test park notes",
            image=None,
        )

    def test_park_creation(self):
        self.assertEqual(self.park.name, "Central Park")
        self.assertEqual(self.park.address, "New York, NY")
        self.assertEqual(self.park.notes, "Test park notes")


class ParkListViewTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.park = DogRun.objects.create(
            id="1",
            prop_id="1234",
            name="Central Park",
            address="New York, NY",
            dogruns_type="Small",
            accessible="Yes",
            notes="Test park notes",
            image=None,
        )

    def test_park_list_view(self):
        response = self.client.get(reverse("park_list"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Central Park")


# class ParkDetailViewTest(TestCase):
#     def setUp(self):
#         self.client = Client()
#         self.park = DogRun.objects.create(
#             id="1",
#             prop_id="1234",
#             name="Central Park",
#             address="New York, NY",
#             dogruns_type="Small",
#             accessible="Yes",
#             notes="Test park notes",
#             image=None,
#         )

#     def test_park_detail_view(self):
#         response = self.client.get(reverse("park_detail", args=[self.park.id]))
#         self.assertEqual(response.status_code, 200)
#         self.assertContains(response, "Central Park")


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
    def test_park_detail_not_found(self):
            """Test accessing a non-existent park should return 404."""
            response = self.client.get(reverse("park_detail", args=[9999]))  # Non-existent ID
            self.assertEqual(response.status_code, 404)
    


    def test_get_park_detail(self):
        """Set up a test park object."""
        self.client = Client()

        self.park = DogRun.objects.create(
            id="1",
            prop_id="1234",
            name="Central Park",
            address="New York, NY",
            dogruns_type="Small",
            accessible="Yes",
            notes="Test park notes",
            image=None,
        )


        self.park_detail_url = reverse("park_detail", args=[self.park.id])
        """Test retrieving the park detail page."""
        response = self.client.get(self.park_detail_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "parks/park_detail.html")
        self.assertContains(response, self.park.name)