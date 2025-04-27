from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from django.core import mail

from accounts.utils import is_user_banned


class UniqueEmailTests(TestCase):
    def setUp(self):
        self.client = Client()
        User.objects.create_user(
            username="existinguser",
            email="duplicate@pawpark.com",
            password="SomeStrongPassword1",
        )
        self.register_url = reverse("register")

    def test_duplicate_email_registration(self):
        """
        Attempting to register a new user with an email that already exists should
        re-render the form with an error message.
        """
        response = self.client.post(
            self.register_url,
            {
                "username": "newuser",
                "email": "duplicate@pawpark.com",
                "password1": "StrongPass123",
                "password2": "StrongPass123",
                "role": "user",
                "admin_access_code": "",
            },
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "A user with that email address already exists.")
        self.assertFalse(User.objects.filter(username="newuser").exists())


class WeakPasswordTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.register_url = reverse("register")

    def test_too_short_password(self):
        response = self.client.post(
            self.register_url,
            {
                "username": "weakuser",
                "password1": "123",
                "password2": "123",
                "role": "user",
            },
        )
        self.assertEqual(response.status_code, 200)
        self.assertFalse(User.objects.filter(username="weakuser").exists())
        self.assertContains(response, "must contain at least 8 characters")

    def test_entirely_numeric_password(self):
        response = self.client.post(
            self.register_url,
            {
                "username": "numericuser",
                "password1": "12345678",
                "password2": "12345678",
                "role": "user",
            },
        )
        self.assertEqual(response.status_code, 200)
        self.assertFalse(User.objects.filter(username="numericuser").exists())
        self.assertContains(response, "can’t be entirely numeric")


class PasswordResetTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            "resetuser", "reset@pawpark.com", "Pass123456"
        )

    def test_password_reset_page_loads(self):
        url = reverse("password_reset")
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "registration/password_reset_form.html")

    def test_password_reset_flow(self):
        """
        Ensure that posting an email to password_reset
        sends the user to password_reset_done,
        and optionally check that an email was
        "sent" (console backend or etc.)
        """
        url = reverse("password_reset")
        response = self.client.post(url, {"email": "reset@pawpark.com"})
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse("password_reset_done"))

        self.assertEqual(len(mail.outbox), 1)
        self.assertIn("resetuser", mail.outbox[0].body)


class AdminSignUpTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.register_url = reverse("register")

    def test_admin_signup_with_correct_code(self):
        """
        Signing up as admin with correct access code should create a staff user.
        """
        response = self.client.post(
            self.register_url,
            {
                "username": "adminuser",
                "password1": "StrongAdminPass123",
                "password2": "StrongAdminPass123",
                "role": "admin",
                "admin_access_code": "SUPERDOG123",
            },
        )
        self.assertEqual(response.status_code, 302)
        self.assertTrue(User.objects.filter(username="adminuser").exists())
        user = User.objects.get(username="adminuser")
        self.assertTrue(user.is_staff)

    def test_admin_signup_with_wrong_code(self):
        """
        Signing up as admin with wrong code should fail and not create staff user.
        """
        response = self.client.post(
            self.register_url,
            {
                "username": "fakeadmin",
                "password1": "StrongAdminPass123",
                "password2": "StrongAdminPass123",
                "role": "admin",
                "admin_access_code": "WRONGCODE",
            },
        )
        self.assertEqual(response.status_code, 200)
        self.assertFalse(User.objects.filter(username="fakeadmin").exists())

    def test_signup_as_normal_user_ignores_access_code(self):
        """
        If someone chooses 'user' role, the admin_access_code is irrelevant.
        """
        response = self.client.post(
            self.register_url,
            {
                "username": "normaluser",
                "password1": "StrongPass456",
                "password2": "StrongPass456",
                "role": "user",
                "admin_access_code": "SUPERDOG123",
            },
        )
        self.assertEqual(response.status_code, 302)
        self.assertTrue(User.objects.filter(username="normaluser").exists())
        user = User.objects.get(username="normaluser")
        self.assertFalse(user.is_staff)


class LoginTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username="testuser", password="StrongPass123"
        )

    def test_login_page_loads(self):
        """Ensure the login page loads properly."""
        response = self.client.get(reverse("login"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "accounts/login.html")

    def test_valid_login(self):
        """Ensure a valid user can log in."""
        response = self.client.post(
            reverse("login"), {"username": "testuser", "password": "StrongPass123"}
        )
        self.assertEqual(response.status_code, 302)

    def test_banned_user_login(self):
        self.user.userprofile.is_banned = True
        self.user.userprofile.save()

        response = self.client.post(
            reverse("login"),
            {"username": "testuser", "password": "StrongPass123"},
            follow=True,  # follow redirects to see the page
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Your account has been banned.")


class AuthTests(TestCase):
    def setUp(self):
        self.client = Client()

    def test_register_page_loads(self):
        """Ensure the registration page loads properly."""
        response = self.client.get(reverse("register"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "accounts/register.html")

    def test_user_registration(self):
        """Ensure a new user can register successfully."""
        response = self.client.post(
            reverse("register"),
            {
                "username": "testuser",
                "password1": "StrongPass123",
                "password2": "StrongPass123",
                "role": "user",  # Ensure this field is required
            },
        )
        self.assertEqual(response.status_code, 302)
        self.assertTrue(User.objects.filter(username="testuser").exists())


class IsUserBannedTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="testuser", password="pass123")
        self.user_profile = self.user.userprofile

    def test_user_not_banned(self):
        self.user_profile.is_banned = False
        self.user_profile.save()
        self.assertFalse(is_user_banned(self.user))

    def test_user_banned(self):
        self.user_profile.is_banned = True
        self.user_profile.save()
        self.assertTrue(is_user_banned(self.user))

    def test_missing_profile(self):
        self.user_profile.delete()
        self.assertFalse(is_user_banned(self.user))
