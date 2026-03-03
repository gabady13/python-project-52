from django.urls import path

from task_manager.tasks.views import (
    TaskListView,
    TaskCreateView,
    TaskUpdateView,
    TaskDeleteView,
    TaskDetailView,
)

urlpatterns = [
    path("", TaskListView.as_view(), name="tasks_list"),
    path("create/", TaskCreateView.as_view(), name="task_create"),
    path("<int:pk>/", TaskDetailView.as_view(), name="task_show"),
    path(
        "<int:pk>/update/",
        TaskUpdateView.as_view(),
        name="task_update",
    ),
    path(
        "<int:pk>/delete/",
        TaskDeleteView.as_view(),
        name="task_delete",
    ),
]