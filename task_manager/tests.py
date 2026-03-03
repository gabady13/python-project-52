from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.models import User
from django.conf import settings
from task_manager.tasks.models import Task
from task_manager.statuses.models import Status
from task_manager.labels.models import Label


class UsersCrudTests(TestCase):
    def test_create_user_redirects_to_login(self):
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
        user = User.objects.create_user(username="u2", password="StrongPass123")
        self.client.login(username="u2", password="StrongPass123")

        response = self.client.post(reverse("user_delete", args=[user.id]))

        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse("users_list"))
        self.assertFalse(User.objects.filter(id=user.id).exists())


class StatusesCrudTests(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(
            username="u",
            password="StrongPass123",
        )
        self.client.login(username="u", password="StrongPass123")

    def test_statuses_routes_require_login(self):
        self.client.logout()

        urls = [
            "/statuses/",
            "/statuses/create/",
        ]

        status = Status.objects.create(name="S1")
        urls += [
            f"/statuses/{status.id}/update/",
            f"/statuses/{status.id}/delete/",
        ]

        for url in urls:
            response = self.client.get(url)
            self.assertEqual(response.status_code, 302)
            self.assertEqual(response.url, f"{settings.LOGIN_URL}?next={url}")

    def test_create_status(self):
        response = self.client.post("/statuses/create/", {"name": "Новый"})
        self.assertEqual(response.status_code, 302)

        self.assertTrue(Status.objects.filter(name="Новый").exists())

    def test_update_status(self):
        status = Status.objects.create(name="Старое")

        response = self.client.post(
            f"/statuses/{status.id}/update/",
            {"name": "Новое"},
        )
        self.assertEqual(response.status_code, 302)

        status.refresh_from_db()
        self.assertEqual(status.name, "Новое")

    def test_delete_status(self):
        status = Status.objects.create(name="Удаляемый")

        response = self.client.post(f"/statuses/{status.id}/delete/")
        self.assertEqual(response.status_code, 302)

        self.assertFalse(Status.objects.filter(id=status.id).exists())

    def test_cannot_delete_status_if_linked_to_task(self):
        try:
            from task_manager.tasks.models import Task
        except Exception:
            self.skipTest(
                "Task model is not implemented yet in task_manager.models"
            )

        status = Status.objects.create(name="Связанный")
        Task.objects.create(name="T1", status=status, author=self.user)

        response = self.client.post(f"/statuses/{status.id}/delete/")
        self.assertEqual(response.status_code, 302)

        self.assertTrue(Status.objects.filter(id=status.id).exists())


class TasksCrudTests(TestCase):
    def setUp(self):
        self.author = User.objects.create_user(
            username="author",
            password="StrongPass123",
        )

        self.other = User.objects.create_user(
            username="other",
            password="StrongPass123",
        )

        self.executor = User.objects.create_user(
            username="executor",
            password="StrongPass123",
        )

        self.status = Status.objects.create(
            name="Новый",
        )

        self.client.login(
            username="author",
            password="StrongPass123",
        )

    def test_tasks_routes_require_login(self):
        self.client.logout()

        task = Task.objects.create(
            name="T1",
            description="D1",
            status=self.status,
            author=self.author,
            executor=self.executor,
        )

        urls = [
            "/tasks/",
            "/tasks/create/",
            f"/tasks/{task.id}/",
            f"/tasks/{task.id}/update/",
            f"/tasks/{task.id}/delete/",
        ]

        for url in urls:
            response = self.client.get(url)
            self.assertEqual(response.status_code, 302)
            self.assertEqual(
                response.url,
                f"{settings.LOGIN_URL}?next={url}",
            )

    def test_create_task(self):
        response = self.client.post(
            "/tasks/create/",
            {
                "name": "Задача 1",
                "description": "Описание 1",
                "status": self.status.id,
                "executor": self.executor.id,
            },
        )

        self.assertEqual(response.status_code, 302)
        self.assertTrue(
            Task.objects.filter(name="Задача 1").exists()
        )

        created = Task.objects.get(name="Задача 1")
        self.assertEqual(created.description, "Описание 1")
        self.assertEqual(created.status_id, self.status.id)
        self.assertEqual(created.executor_id, self.executor.id)
        self.assertEqual(created.author_id, self.author.id)

    def test_update_task(self):
        task = Task.objects.create(
            name="Старое имя",
            description="Старое описание",
            status=self.status,
            author=self.author,
            executor=self.executor,
        )

        response = self.client.post(
            f"/tasks/{task.id}/update/",
            {
                "name": "Новое имя",
                "description": "Новое описание",
                "status": self.status.id,
                "executor": self.executor.id,
            },
        )

        self.assertEqual(response.status_code, 302)

        task.refresh_from_db()
        self.assertEqual(task.name, "Новое имя")
        self.assertEqual(task.description, "Новое описание")

    def test_view_task(self):
        task = Task.objects.create(
            name="Просмотр",
            description="Текст",
            status=self.status,
            author=self.author,
            executor=self.executor,
        )

        response = self.client.get(f"/tasks/{task.id}/")
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Просмотр")

    def test_only_author_can_delete_task(self):
        task = Task.objects.create(
            name="Del",
            description="",
            status=self.status,
            author=self.author,
            executor=self.executor,
        )

        self.client.logout()
        self.client.login(
            username="other",
            password="StrongPass123",
        )

        response_forbidden = self.client.post(
            f"/tasks/{task.id}/delete/",
        )
        self.assertEqual(response_forbidden.status_code, 302)

        self.assertTrue(
            Task.objects.filter(id=task.id).exists()
        )

        self.client.logout()
        self.client.login(
            username="author",
            password="StrongPass123",
        )

        response_allowed = self.client.post(
            f"/tasks/{task.id}/delete/",
        )

        self.assertEqual(response_allowed.status_code, 302)
        self.assertFalse(
            Task.objects.filter(id=task.id).exists()
        )


class LabelsCrudTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="u1",
            password="pass12345",
        )
        self.status = Status.objects.create(name="S1")

    def test_labels_list_requires_login(self):
        response = self.client.get(reverse("labels_list"))
        self.assertEqual(response.status_code, 302)

    def test_create_label(self):
        self.client.login(username="u1", password="pass12345")

        response = self.client.post(
            reverse("label_create"),
            data={"name": "L1"},
        )
        self.assertEqual(response.status_code, 302)

        self.assertTrue(Label.objects.filter(name="L1").exists())

    def test_update_label(self):
        self.client.login(username="u1", password="pass12345")
        label = Label.objects.create(name="L1")

        response = self.client.post(
            reverse("label_update", args=[label.id]),
            data={"name": "L2"},
        )
        self.assertEqual(response.status_code, 302)

        label.refresh_from_db()
        self.assertEqual(label.name, "L2")

    def test_delete_label_when_not_used(self):
        self.client.login(username="u1", password="pass12345")
        label = Label.objects.create(name="L1")

        response = self.client.post(reverse("label_delete", args=[label.id]))
        self.assertEqual(response.status_code, 302)

        self.assertFalse(Label.objects.filter(id=label.id).exists())

    def test_delete_label_when_used_forbidden(self):
        self.client.login(username="u1", password="pass12345")
        label = Label.objects.create(name="L1")

        task = Task.objects.create(
            name="T1",
            description="D1",
            status=self.status,
            author=self.user,
            executor=self.user,
        )
        task.labels.add(label)

        response = self.client.post(reverse("label_delete", args=[label.id]))
        self.assertEqual(response.status_code, 302)

        self.assertTrue(Label.objects.filter(id=label.id).exists())


class TasksFilterTests(TestCase):
    def setUp(self):
        self.author = User.objects.create_user(
            username="author_f",
            password="StrongPass123",
        )
        self.other_author = User.objects.create_user(
            username="other_f",
            password="StrongPass123",
        )
        self.executor_1 = User.objects.create_user(
            username="exec1_f",
            password="StrongPass123",
        )
        self.executor_2 = User.objects.create_user(
            username="exec2_f",
            password="StrongPass123",
        )

        self.status_1 = Status.objects.create(name="S1_f")
        self.status_2 = Status.objects.create(name="S2_f")

        self.label_1 = Label.objects.create(name="L1_f")
        self.label_2 = Label.objects.create(name="L2_f")

        self.t1 = Task.objects.create(
            name="T1_f",
            description="",
            status=self.status_1,
            author=self.author,
            executor=self.executor_1,
        )
        self.t1.labels.add(self.label_1)

        self.t2 = Task.objects.create(
            name="T2_f",
            description="",
            status=self.status_2,
            author=self.other_author,
            executor=self.executor_2,
        )
        self.t2.labels.add(self.label_2)

    def test_filter_by_status(self):
        self.client.login(username="author_f", password="StrongPass123")
        response = self.client.get("/tasks/", {"status": self.status_1.id})
        self.assertContains(response, "T1_f")
        self.assertNotContains(response, "T2_f")

    def test_filter_by_executor(self):
        self.client.login(username="author_f", password="StrongPass123")
        response = self.client.get("/tasks/", {"executor": self.executor_1.id})
        self.assertContains(response, "T1_f")
        self.assertNotContains(response, "T2_f")

    def test_filter_by_label(self):
        self.client.login(username="author_f", password="StrongPass123")
        response = self.client.get("/tasks/", {"label": self.label_1.id})
        self.assertContains(response, "T1_f")
        self.assertNotContains(response, "T2_f")

    def test_filter_self_tasks(self):
        self.client.login(username="author_f", password="StrongPass123")
        response = self.client.get("/tasks/", {"self_tasks": "on"})
        self.assertContains(response, "T1_f")
        self.assertNotContains(response, "T2_f")