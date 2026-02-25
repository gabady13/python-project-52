from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.models import User
from django.conf import settings
from task_manager.models import Status, Task, Label


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
        Task.objects.create(name="T1", status=status, author=self.user)  # поля Task могут отличаться — подгони под свою модель

        response = self.client.post(f"/statuses/{status.id}/delete/")
        self.assertEqual(response.status_code, 302)

        # статус остался
        self.assertTrue(Status.objects.filter(id=status.id).exists())

class TasksCrudTests(TestCase):  # набор тестов CRUD для сущности Task (Задачи)
    def setUp(self):  # метод выполняется перед каждым тестом (готовим данные)
        self.author = User.objects.create_user(  # создаём пользователя-автора задач
            username="author",  # логин автора
            password="StrongPass123",  # пароль автора (для логина в тест-клиенте)
        )  # конец создания пользователя-автора

        self.other = User.objects.create_user(  # создаём второго пользователя (для проверок прав)
            username="other",  # логин второго пользователя
            password="StrongPass123",  # пароль второго пользователя
        )  # конец создания второго пользователя

        self.executor = User.objects.create_user(  # создаём пользователя-исполнителя (назначаемого на задачи)
            username="executor",  # логин исполнителя
            password="StrongPass123",  # пароль исполнителя
        )  # конец создания пользователя-исполнителя

        self.status = Status.objects.create(  # создаём обязательный статус для задач
            name="Новый",  # имя статуса
        )  # конец создания статуса

        self.client.login(  # логинимся тест-клиентом (по умолчанию работаем как автор)
            username="author",  # логин под которым логинимся
            password="StrongPass123",  # пароль
        )  # конец логина

    def test_tasks_routes_require_login(self):  # проверяем: все CRUD-страницы задач требуют авторизации
        self.client.logout()  # разлогиниваемся, чтобы имитировать гостя

        task = Task.objects.create(  # создаём задачу напрямую в БД, чтобы получить pk для url detail/update/delete
            name="T1",  # имя задачи
            description="D1",  # описание задачи
            status=self.status,  # обязательный FK на статус
            author=self.author,  # обязательный автор (в задаче автор обязателен)
            executor=self.executor,  # необязательный исполнитель (в этом тесте заполняем)
        )  # конец создания задачи

        urls = [  # список URL, которые должны редиректить на логин
            "/tasks/",  # список задач
            "/tasks/create/",  # форма создания
            f"/tasks/{task.id}/",  # просмотр конкретной задачи
            f"/tasks/{task.id}/update/",  # форма редактирования
            f"/tasks/{task.id}/delete/",  # подтверждение удаления
        ]  # конец списка url

        for url in urls:  # прогоняемся по всем url
            response = self.client.get(url)  # делаем GET как незалогиненный пользователь
            self.assertEqual(response.status_code, 302)  # ожидаем редирект (не пускают без логина)
            self.assertEqual(  # сравниваем целевой редирект
                response.url,  # фактический url редиректа
                f"{settings.LOGIN_URL}?next={url}",  # ожидаем: /login/?next=<страница>
            )  # конец проверки редиректа

    def test_create_task(self):  # проверяем: создание задачи работает и автор ставится автоматически (в реализации)
        response = self.client.post(  # отправляем POST на создание
            "/tasks/create/",  # маршрут создания (по ТЗ)
            {  # данные формы (имена полей должны совпасть с формой в проекте)
                "name": "Задача 1",  # имя задачи
                "description": "Описание 1",  # описание задачи
                "status": self.status.id,  # статус как id (так Django формы обычно принимают FK)
                "executor": self.executor.id,  # исполнитель как id (может быть пустым в реальной форме)
            },  # конец данных формы
        )  # конец POST

        self.assertEqual(response.status_code, 302)  # после успешного создания ожидаем редирект
        self.assertTrue(  # проверяем что задача реально появилась в БД
            Task.objects.filter(name="Задача 1").exists()  # ищем по имени (достаточно для smoke-проверки)
        )  # конец проверки существования

        created = Task.objects.get(name="Задача 1")  # получаем созданную задачу из БД
        self.assertEqual(created.description, "Описание 1")  # проверяем описание
        self.assertEqual(created.status_id, self.status.id)  # проверяем что статус привязан верно
        self.assertEqual(created.executor_id, self.executor.id)  # проверяем что исполнитель привязан верно
        self.assertEqual(created.author_id, self.author.id)  # критично: автор должен быть текущий пользователь

    def test_update_task(self):  # проверяем: редактирование задачи работает для залогиненного пользователя
        task = Task.objects.create(  # создаём задачу как исходное состояние
            name="Старое имя",  # старое имя
            description="Старое описание",  # старое описание
            status=self.status,  # статус
            author=self.author,  # автор (текущий залогиненный)
            executor=self.executor,  # исполнитель
        )  # конец создания задачи

        response = self.client.post(  # делаем POST на обновление
            f"/tasks/{task.id}/update/",  # маршрут редактирования (по ТЗ)
            {  # новые данные формы
                "name": "Новое имя",  # новое имя
                "description": "Новое описание",  # новое описание
                "status": self.status.id,  # статус (оставим тот же)
                "executor": self.executor.id,  # исполнитель (оставим тот же)
            },  # конец данных формы
        )  # конец POST

        self.assertEqual(response.status_code, 302)  # после update ожидаем редирект

        task.refresh_from_db()  # перечитываем объект из БД, чтобы увидеть изменения
        self.assertEqual(task.name, "Новое имя")  # проверяем обновление имени
        self.assertEqual(task.description, "Новое описание")  # проверяем обновление описания

    def test_view_task(self):  # проверяем: страница просмотра задачи доступна залогиненному пользователю
        task = Task.objects.create(  # создаём задачу для просмотра
            name="Просмотр",  # имя
            description="Текст",  # описание
            status=self.status,  # статус
            author=self.author,  # автор
            executor=self.executor,  # исполнитель
        )  # конец создания задачи

        response = self.client.get(  # делаем GET на страницу просмотра
            f"/tasks/{task.id}/",  # маршрут просмотра (по ТЗ)
        )  # конец GET

        self.assertEqual(response.status_code, 200)  # ожидаем 200 OK
        self.assertContains(response, "Просмотр")  # ожидаем что имя задачи есть на странице (минимальная проверка)

    def test_delete_task_only_author_can_delete(self):  # проверяем ключевое правило: удалить может только автор
        task = Task.objects.create(  # создаём задачу, автором будет self.author
            name="Удаление",  # имя
            description="Текст",  # описание
            status=self.status,  # статус
            author=self.author,  # автор
            executor=self.executor,  # исполнитель
        )  # конец создания задачи

        self.client.logout()  # выходим из текущей сессии (автора)
        self.client.login(  # логинимся вторым пользователем (не автором)
            username="other",  # логин другого
            password="StrongPass123",  # пароль другого
        )  # конец логина другим пользователем

        response_forbidden = self.client.post(  # пытаемся удалить задачу чужим пользователем
            f"/tasks/{task.id}/delete/",  # маршрут удаления (по ТЗ)
        )  # конец POST удаления

        self.assertEqual(response_forbidden.status_code, 302)  # обычно делают редирект + flash (как в демо-проекте)
        self.assertTrue(  # задача должна остаться
            Task.objects.filter(id=task.id).exists()  # проверяем что запись в БД не исчезла
        )  # конец проверки что задача осталась

        self.client.logout()  # выходим из сессии другого пользователя
        self.client.login(  # возвращаемся под автором
            username="author",  # логин автора
            password="StrongPass123",  # пароль автора
        )  # конец логина автором

        response_allowed = self.client.post(  # удаляем задачу автором
            f"/tasks/{task.id}/delete/",  # маршрут удаления
        )  # конец POST удаления автором

        self.assertEqual(response_allowed.status_code, 302)  # ожидаем редирект после удаления
        self.assertFalse(  # задача должна быть удалена
            Task.objects.filter(id=task.id).exists()  # проверяем отсутствие в БД
        )  # конец проверки удаления


class LabelsCrudTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="u1", password="pass12345")
        self.status = Status.objects.create(name="S1")

    def test_labels_list_requires_login(self):
        response = self.client.get(reverse("labels_list"))
        self.assertEqual(response.status_code, 302)

    def test_create_label(self):
        self.client.login(username="u1", password="pass12345")

        response = self.client.post(reverse("label_create"), data={"name": "L1"})
        self.assertEqual(response.status_code, 302)

        self.assertTrue(Label.objects.filter(name="L1").exists())

    def test_update_label(self):
        self.client.login(username="u1", password="pass12345")
        label = Label.objects.create(name="L1")

        response = self.client.post(reverse("label_update", args=[label.id]), data={"name": "L2"})
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
        self.author = User.objects.create_user(username="author_f", password="StrongPass123")
        self.other_author = User.objects.create_user(username="other_f", password="StrongPass123")
        self.executor_1 = User.objects.create_user(username="exec1_f", password="StrongPass123")
        self.executor_2 = User.objects.create_user(username="exec2_f", password="StrongPass123")

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
            author=self.author,
            executor=self.executor_2,
        )
        self.t2.labels.add(self.label_2)

        self.t3 = Task.objects.create(
            name="T3_f",
            description="",
            status=self.status_1,
            author=self.other_author,
            executor=self.executor_1,
        )
        self.t3.labels.add(self.label_2)

        self.client.login(username="author_f", password="StrongPass123")

    def test_filter_by_status(self):
        response = self.client.get("/tasks/", {"status": self.status_1.id})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "T1_f")
        self.assertContains(response, "T3_f")
        self.assertNotContains(response, "T2_f")

    def test_filter_by_executor(self):
        response = self.client.get("/tasks/", {"executor": self.executor_2.id})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "T2_f")
        self.assertNotContains(response, "T1_f")
        self.assertNotContains(response, "T3_f")

    def test_filter_by_label(self):
        response = self.client.get("/tasks/", {"label": self.label_2.id})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "T2_f")
        self.assertContains(response, "T3_f")
        self.assertNotContains(response, "T1_f")

    def test_filter_only_self_tasks(self):
        response = self.client.get("/tasks/", {"self_tasks": "on"})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "T1_f")
        self.assertContains(response, "T2_f")
        self.assertNotContains(response, "T3_f")