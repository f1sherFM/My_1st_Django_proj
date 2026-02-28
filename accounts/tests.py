import shutil
import tempfile

from django.test import TestCase, override_settings
from django.urls import reverse

from accounts.models import Profile, User

TEMP_MEDIA_ROOT = tempfile.mkdtemp()


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class RegistrationTests(TestCase):
    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    def test_register_creates_user_and_profile(self):
        response = self.client.post(
            reverse("register"),
            {
                "username": "new_user",
                "email": "new@example.com",
                "password1": "StrongPass123!!",
                "password2": "StrongPass123!!",
            },
        )

        self.assertRedirects(response, reverse("blog:post_list"))
        user = User.objects.get(username="new_user")
        self.assertEqual(user.email, "new@example.com")
        self.assertTrue(Profile.objects.filter(user=user).exists())

    def test_register_duplicate_email_shows_form_error(self):
        User.objects.create_user(username="existing", email="same@example.com", password="pass12345")

        response = self.client.post(
            reverse("register"),
            {
                "username": "another",
                "email": "same@example.com",
                "password1": "StrongPass123!!",
                "password2": "StrongPass123!!",
            },
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Пользователь с таким email уже зарегистрирован.")


class ProfileViewTests(TestCase):
    def test_profile_requires_authentication(self):
        user = User.objects.create_user(username="anna", email="anna@example.com", password="testpass123")
        response = self.client.get(reverse("profile", kwargs={"username": user.username}))
        self.assertEqual(response.status_code, 302)
        self.assertIn(reverse("login"), response.url)

    def test_authenticated_user_can_open_profile(self):
        user = User.objects.create_user(username="anna", email="anna@example.com", password="testpass123")
        self.client.login(username="anna", password="testpass123")

        response = self.client.get(reverse("profile", kwargs={"username": user.username}))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "anna")
