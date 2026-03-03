"""task_manager URL Configuration.

The `urlpatterns` list routes URLs to views.
"""

from django.contrib import admin
from django.urls import path

from .views import (
    LabelCreateView,
    LabelDeleteView,
    LabelUpdateView,
    LabelsListView,
    StatusCreateView,
    StatusDeleteView,
    StatusListView,
    StatusUpdateView,
    TaskCreateView,
    TaskDeleteView,
    TaskDetailView,
    TaskListView,
    TaskUpdateView,
    UserCreateView,
    UserDeleteView,
    UserLoginView,
    UserLogoutView,
    UsersListView,
    UserUpdateView,
    index,
)

urlpatterns = [
    path("", index, name="index"),
    path("admin/", admin.site.urls),
    path("users/", UsersListView.as_view(), name="users_list"),
    path("users/create/", UserCreateView.as_view(), name="user_create"),
    path(
        "users/<int:pk>/update/",
        UserUpdateView.as_view(),
        name="user_update",
    ),
    path(
        "users/<int:pk>/delete/",
        UserDeleteView.as_view(),
        name="user_delete",
    ),
    path("login/", UserLoginView.as_view(), name="login"),
    path("logout/", UserLogoutView.as_view(), name="logout"),
    path("statuses/", StatusListView.as_view(), name="statuses_list"),
    path("statuses/create/", StatusCreateView.as_view(), name="status_create"),
    path(
        "statuses/<int:pk>/update/",
        StatusUpdateView.as_view(),
        name="status_update",
    ),
    path(
        "statuses/<int:pk>/delete/",
        StatusDeleteView.as_view(),
        name="status_delete",
    ),
    path("tasks/", TaskListView.as_view(), name="tasks_list"),
    path("tasks/create/", TaskCreateView.as_view(), name="task_create"),
    path("tasks/<int:pk>/", TaskDetailView.as_view(), name="task_show"),
    path(
        "tasks/<int:pk>/update/",
        TaskUpdateView.as_view(),
        name="task_update",
    ),
    path(
        "tasks/<int:pk>/delete/",
        TaskDeleteView.as_view(),
        name="task_delete",
    ),
    path("labels/", LabelsListView.as_view(), name="labels_list"),
    path("labels/create/", LabelCreateView.as_view(), name="label_create"),
    path(
        "labels/<int:pk>/update/",
        LabelUpdateView.as_view(),
        name="label_update",
    ),
    path(
        "labels/<int:pk>/delete/",
        LabelDeleteView.as_view(),
        name="label_delete",
    ),
]