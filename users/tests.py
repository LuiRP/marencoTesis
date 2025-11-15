from django.contrib.auth import get_user_model
from django.test import TestCase


# Create your tests here.
class UsersManagersTest(TestCase):
    def setUp(self):
        self.User = get_user_model()
        self.user = self.User.objects.create_user(
            email="ejemplo@ejemplo.com", password="Ejemplo123%"
        )
        self.admin_user = self.User.objects.create_superuser(
            email="super@user.com", password="Ejemplo123%"
        )

    def test_create_user(self):

        self.assertEqual(self.user.email, "ejemplo@ejemplo.com")
        self.assertTrue(self.user.is_active)
        self.assertFalse(self.user.is_staff)
        self.assertFalse(self.user.is_superuser)
        try:
            self.assertIsNone(self.user.username)
        except AttributeError:
            pass
        with self.assertRaises(TypeError):
            self.User.objects.create_user(email="")
        with self.assertRaises(ValueError):
            self.User.objects.create_user(email="", password="Ejemplo123%")

    def test_create_superuser(self):
        self.assertEqual(self.admin_user.email, "super@user.com")
        self.assertTrue(self.admin_user.is_active)
        self.assertTrue(self.admin_user.is_staff)
        self.assertTrue(self.admin_user.is_superuser)
        try:
            self.assertIsNone(self.admin_user.username)
        except AttributeError:
            pass
        with self.assertRaises(ValueError):
            self.User.objects.create_superuser(
                email="super@user.com",
                password="Ejemplo123%",
                is_superuser=False,
            )
