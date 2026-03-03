from django.contrib import messages
from django.contrib.auth import get_user_model
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.forms import ModelForm
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.views.generic import CreateView, DeleteView, DetailView, UpdateView
from django_filters.views import FilterView

from task_manager.tasks.filters import TaskFilter
from ..models import Task
from task_manager.views.mixins import SafeDeleteWithProtectedErrorMixin


class TaskForm(ModelForm):
    class Meta:
        model = Task
        fields = ["name", "description", "status", "executor", "labels"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        user_model = get_user_model()
        self.fields["executor"].queryset = user_model.objects.all()

        def _label(user):
            full_name = f"{user.first_name} {user.last_name}".strip()
            return full_name or user.get_username()

        self.fields["executor"].label_from_instance = _label


class TaskListView(LoginRequiredMixin, FilterView):
    model = Task
    template_name = "tasks/list.html"
    context_object_name = "tasks"
    filterset_class = TaskFilter
    queryset = (
        Task.objects.select_related("status", "author", "executor")
        .prefetch_related("labels")
        .order_by("id")
    )


class TaskCreateView(LoginRequiredMixin, CreateView):
    model = Task
    form_class = TaskForm
    template_name = "tasks/form.html"
    success_url = reverse_lazy("tasks_list")

    def form_valid(self, form):
        form.instance.author = self.request.user
        messages.success(self.request, "Задача успешно создана")
        return super().form_valid(form)


class TaskDetailView(LoginRequiredMixin, DetailView):
    model = Task
    template_name = "tasks/show.html"
    context_object_name = "task"


class TaskUpdateView(LoginRequiredMixin, UpdateView):
    model = Task
    form_class = TaskForm
    template_name = "tasks/form.html"
    success_url = reverse_lazy("tasks_list")

    def form_valid(self, form):
        messages.success(self.request, "Задача успешно изменена")
        return super().form_valid(form)


class OnlyAuthorMixin(UserPassesTestMixin):
    def test_func(self):
        obj = self.get_object()
        return obj.author_id == self.request.user.id

    def handle_no_permission(self):
        if not self.request.user.is_authenticated:
            return super().handle_no_permission()
        messages.error(self.request, "Задачу может удалить только ее автор")
        return redirect("tasks_list")


class TaskDeleteView(
    LoginRequiredMixin,
    OnlyAuthorMixin,
    SafeDeleteWithProtectedErrorMixin,
    DeleteView,
):
    model = Task
    template_name = "tasks/delete.html"
    success_url = reverse_lazy("tasks_list")
    protected_error_message = (
        "Невозможно удалить задачу, потому что она используется"
    )
    success_message = "Задача успешно удалена"