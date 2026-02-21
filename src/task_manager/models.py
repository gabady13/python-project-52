from django.db import models
from django.conf import settings


class Status(models.Model):
    name = models.CharField(max_length=255, unique=True, verbose_name='Имя')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата создания')

    def __str__(self) -> str:
        return self.name


class Label(models.Model):
    name = models.CharField(max_length=255, unique=True, verbose_name='Имя')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата создания')

    def __str__(self) -> str:
        return self.name


class Task(models.Model):  # модель "Задача" (новая сущность по ТЗ)
    name = models.CharField(max_length=255, verbose_name='Имя')  # имя задачи (обязательное)
    description = models.TextField(blank=True, verbose_name='Описание')  # описание (может быть пустым в форме)

    status = models.ForeignKey(  # связь "многие к одному": много задач → один статус
        Status,  # модель, на которую ссылаемся
        on_delete=models.PROTECT,  # запретить удаление статуса, если он используется задачами
        verbose_name='Статус',  # русское имя поля
    )

    author = models.ForeignKey(  # автор задачи (пользователь)
        settings.AUTH_USER_MODEL,  # ссылка на модель пользователя (стандартно auth.User)
        on_delete=models.PROTECT,  # запретить удаление пользователя, если он связан с задачами
        related_name='created_tasks',  # удобное имя обратной связи: user.created_tasks
        verbose_name='Автор',  # русское имя поля
    )

    executor = models.ForeignKey(  # исполнитель задачи (пользователь)
        settings.AUTH_USER_MODEL,  # ссылка на модель пользователя
        on_delete=models.PROTECT,  # запретить удаление пользователя, если он назначен исполнителем в задачах
        related_name='executed_tasks',  # удобное имя обратной связи: user.executed_tasks
        null=True,  # в базе допускаем NULL (исполнитель необязателен)
        blank=True,  # в форме допускаем пустое значение
        verbose_name='Исполнитель',  # русское имя поля
    )

    labels = models.ManyToManyField(
        Label, 
        blank=True, 
        related_name='tasks', 
        verbose_name='Метки')

    created_at = models.DateTimeField(  # техническое поле даты создания задачи
        auto_now_add=True,  # выставляется автоматически при создании записи
        verbose_name='Дата создания',  # русское имя поля
    )

    def __str__(self) -> str:  # строковое представление задачи
        return self.name  # возвращаем имя задачи
