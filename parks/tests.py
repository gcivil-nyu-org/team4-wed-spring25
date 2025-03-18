from django.test import TestCase, Client
from django.urls import reverse

from .models import DogRunNew


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
            image=None,
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
            image=None,
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


# class ParkDetailViewTest(TestCase):
#     def setUp(self):
#         self.client = Client()
#         self.park = DogRunNew.objects.create(
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
        response = self.client.get(
            reverse("park_detail", args=[9999])
        )  # Non-existent ID
        self.assertEqual(response.status_code, 404)

    def test_get_park_detail(self):
        """Set up a test park object."""
        self.client = Client()

        self.park = DogRunNew.objects.create(
            id="1",
            prop_id="1234",
            name="Central Park",
            address="New York, NY",
            dogruns_type="Small",
            accessible="Yes",
            notes="Test park notes",
            image=None,
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

        self.park_detail_url = reverse("park_detail", args=[self.park.id])
        """Test retrieving the park detail page."""
        response = self.client.get(self.park_detail_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "parks/park_detail.html")
        self.assertContains(response, self.park.name)