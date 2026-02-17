from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.models import User
from django.conf import settings
from task_manager.models import Status 


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

    
class StatusesCrudTests(TestCase):
    
    def setUp(self):
        self.user = User.objects.create_user(username="u", password="StrongPass123")
        self.client.login(username="u", password="StrongPass123")

    # ---------- Access control ----------
    def test_statuses_routes_require_login(self):
        """Все страницы статусов доступны только залогиненным."""
        self.client.logout()

        urls = [
            "/statuses/",
            "/statuses/create/",
        ]

        # для update/delete нужен pk — создадим статус напрямую (когда модель будет)
        status = Status.objects.create(name="S1")
        urls += [
            f"/statuses/{status.id}/update/",
            f"/statuses/{status.id}/delete/",
        ]

        for url in urls:
            response = self.client.get(url)
            self.assertEqual(response.status_code, 302)
            self.assertEqual(response.url, f"{settings.LOGIN_URL}?next={url}")

    # ---------- Create ----------
    def test_create_status(self):
        """C: создание статуса через POST /statuses/create/"""
        response = self.client.post("/statuses/create/", {"name": "Новый"})
        self.assertEqual(response.status_code, 302)

        self.assertTrue(Status.objects.filter(name="Новый").exists())

    # ---------- Update ----------
    def test_update_status(self):
        """U: обновление статуса через POST /statuses/<pk>/update/"""
        status = Status.objects.create(name="Старое")

        response = self.client.post(f"/statuses/{status.id}/update/", {"name": "Новое"})
        self.assertEqual(response.status_code, 302)

        status.refresh_from_db()
        self.assertEqual(status.name, "Новое")

    # ---------- Delete (allowed) ----------
    def test_delete_status(self):
        """D: удаление статуса через POST /statuses/<pk>/delete/ если не связан с задачами"""
        status = Status.objects.create(name="Удаляемый")

        response = self.client.post(f"/statuses/{status.id}/delete/")
        self.assertEqual(response.status_code, 302)

        self.assertFalse(Status.objects.filter(id=status.id).exists())

    # ---------- Delete (forbidden if linked) ----------
    def test_cannot_delete_status_if_linked_to_task(self):
        """
        Статус нельзя удалить, если он связан хотя бы с одной задачей.
        Тест включится автоматически, когда в task_manager.models появится Task(status=FK).
        """
        try:
            from task_manager.models import Task  # ожидаем модель Task в этом же app
        except Exception:
            self.skipTest("Task model is not implemented yet in task_manager.models")

        status = Status.objects.create(name="Связанный")
        Task.objects.create(name="T1", status=status)  # поля Task могут отличаться — подгони под свою модель

        response = self.client.post(f"/statuses/{status.id}/delete/")
        self.assertEqual(response.status_code, 302)

        # статус остался
        self.assertTrue(Status.objects.filter(id=status.id).exists())