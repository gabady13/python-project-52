from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.models import User


class UsersCrudTests(TestCase):
    def test_create_user_redirects_to_login(self):
        """C: регистрация создаёт пользователя и редиректит на /login/"""
        response = self.client.post(reverse("user_create"), {
            "username": "new_user",
            "first_name": "New",
            "last_name": "User",
            "password1": "StrongPass123",
            "password2": "StrongPass123",
        })

        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse("login"))
        self.assertTrue(User.objects.filter(username="new_user").exists())

    def test_update_user_redirects_to_users_list(self):
        """U: успешное изменение себя редиректит на /users/"""
        user = User.objects.create_user(username="u1", password="StrongPass123")
        self.client.login(username="u1", password="StrongPass123")

        response = self.client.post(reverse("user_update", args=[user.id]), {
            "username": "u1",
            "first_name": "Updated",
            "last_name": "Name",
        })

        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse("users_list"))

        user.refresh_from_db()
        self.assertEqual(user.first_name, "Updated")
        self.assertEqual(user.last_name, "Name")

    def test_delete_user_redirects_to_users_list(self):
        """D: успешное удаление себя редиректит на /users/"""
        user = User.objects.create_user(username="u2", password="StrongPass123")
        self.client.login(username="u2", password="StrongPass123")

        response = self.client.post(reverse("user_delete", args=[user.id]))

        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse("users_list"))
        self.assertFalse(User.objects.filter(id=user.id).exists())