from django.test import TestCase
from .models import Park

class ParkModelTest(TestCase):
    def setUp(self):
        Park.objects.create(name="Central Park", location="New York")

    def test_park_creation(self):
        park = Park.objects.get(name="Central Park")
        self.assertEqual(park.location, "New York")

class DummyTestCase(TestCase):
    def test_dummy(self):
        self.assertTrue(True)
