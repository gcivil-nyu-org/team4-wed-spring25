from django.test import TestCase, Client
from django.urls import reverse
from .models import DogRun
from django.contrib.auth.models import User

class LoginTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username="testuser", password="StrongPass123")

    def test_login_page_loads(self):
        """Ensure the login page loads properly."""
        response = self.client.get(reverse('login'))  # Ensure this matches your URL name
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "parks/login.html")

    def test_valid_login(self):
        """Ensure a valid user can log in."""
        response = self.client.post(reverse('login'), {
            'username': 'testuser',
            'password': 'StrongPass123'
        })
        self.assertEqual(response.status_code, 302)  


class AuthTests(TestCase):
    def setUp(self):
        self.client = Client()

    def test_register_page_loads(self):
        """Ensure the registration page loads properly."""
        response = self.client.get(reverse('register'))  # Ensure this matches your URL name
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "parks/register.html")

    def test_user_registration(self):
        """Ensure a new user can register successfully."""
        response = self.client.post(reverse('register'), {
        'username': 'testuser',
        'password1': 'StrongPass123',
        'password2': 'StrongPass123',
        'role': 'user'  # Make sure this field is required in the form
        })

        # Print response content for debugging
        print(f"Response status: {response.status_code}")
        print(f"Response content: {response.content.decode()}")

        # Check if the response is a redirect (302)
        self.assertEqual(response.status_code, 302, f"Response text: {response.content.decode()}")

        # Ensure the user was actually created in the database
        self.assertTrue(User.objects.filter(username="testuser").exists())



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
        response = self.client.get(
            reverse("park_detail", args=[9999])
        )  # Non-existent ID
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
