from django.shortcuts import render
from django import forms
from django.forms import ModelForm
from django.contrib import messages
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.views.generic import ListView, CreateView, UpdateView, DeleteView, DetailView
from django.contrib.auth.views import LoginView, LogoutView
from django.urls import reverse_lazy
from django.shortcuts import redirect
from django.contrib.auth.mixins import LoginRequiredMixin
from django_filters.views import FilterView

from .models import Status, Task, Label
from .filters import TaskFilter

def index(request):
    return render(request, "index.html")


class UsersListView(ListView):
    model = User
    template_name = "users/user_list.html"
    context_object_name = "users"

    def get_queryset(self):
        return User.objects.order_by("id")

class UserRegisterForm(UserCreationForm):
    """Регистрация. UserCreationForm даёт стандартные поля:
    username, password1, password2.
    """
    class Meta(UserCreationForm.Meta):
        model = User
        fields = ("username", "first_name", "last_name")


class UserUpdateForm(forms.ModelForm):
    """Редактирование профиля (без пароля)."""
    class Meta:
        model = User
        fields = ("username", "first_name", "last_name")


class OnlySelfMixin(UserPassesTestMixin):
    """Редактировать/удалять можно только самого себя."""
    def test_func(self):
        return self.get_object().id == self.request.user.id


class UserCreateView(CreateView):
    model = User
    form_class = UserRegisterForm
    template_name = "users/user_form.html"
    success_url = reverse_lazy("login")


class UserUpdateView(LoginRequiredMixin, OnlySelfMixin, UpdateView):
    model = User
    form_class = UserUpdateForm
    template_name = "users/user_form.html"
    success_url = reverse_lazy("users_list")


class UserDeleteView(LoginRequiredMixin, OnlySelfMixin, DeleteView):
    model = User
    template_name = "users/user_confirm_delete.html"
    success_url = "/users/"

class UserLoginView(LoginView):
    template_name = "users/login.html"
    redirect_authenticated_user = True  # если уже залогинен — не показывать форму

    def form_valid(self, form):
        messages.success(self.request, "Вы залогинены")
        return super().form_valid(form)


class UserLogoutView(LogoutView):
    http_method_names = ["post"]  

    def post(self, request, *args, **kwargs):
        messages.info(request, "Вы разлогинены")
        return super().post(request, *args, **kwargs)


class StatusForm(ModelForm):
    class Meta:
        model = Status
        fields = ['name']   # важно: имя поля формы должно совпадать с демо


class StatusListView(LoginRequiredMixin, ListView):
    model = Status
    template_name = 'statuses/list.html'
    context_object_name = 'statuses'


class StatusCreateView(LoginRequiredMixin, CreateView):
    model = Status
    form_class = StatusForm
    template_name = 'statuses/form.html'
    success_url = reverse_lazy('statuses_list')

    def form_valid(self, form):
        messages.success(self.request, 'Статус успешно создан')
        return super().form_valid(form)


class StatusUpdateView(LoginRequiredMixin, UpdateView):
    model = Status
    form_class = StatusForm
    template_name = 'statuses/form.html'
    success_url = reverse_lazy('statuses_list')

    def form_valid(self, form):
        messages.success(self.request, 'Статус успешно изменён')
        return super().form_valid(form)


class StatusDeleteView(LoginRequiredMixin, DeleteView):
    model = Status
    template_name = 'statuses/delete.html'
    success_url = reverse_lazy('statuses_list')

    def post(self, request, *args, **kwargs):
        status = self.get_object()

        # Бизнес-правило: нельзя удалить статус, если он используется задачами
        # поддерживаем оба варианта (related_name='tasks' или дефолт task_set)
        used = False
        if hasattr(status, 'tasks'):
            used = status.tasks.exists()
        elif hasattr(status, 'task_set'):
            used = status.task_set.exists()

        if used:
            messages.error(request, 'Невозможно удалить статус, потому что он используется')
            return redirect(self.success_url)

        messages.success(request, 'Статус успешно удалён')
        return super().post(request, *args, **kwargs)


class TaskForm(ModelForm):  # форма задачи
    class Meta:  # meta
        model = Task  # модель Task
        fields = ['name', 'description', 'status', 'executor', 'labels']  # важно: author НЕ в форме (ставим автоматически)


class TaskListView(LoginRequiredMixin, FilterView):  # GET /tasks/ — список задач
    model = Task  # модель
    template_name = 'tasks/list.html'  # шаблон списка
    context_object_name = 'tasks'  # имя переменной в шаблоне
    filterset_class = TaskFilter
    queryset = Task.objects.select_related('status', 'author', 'executor').prefetch_related('labels').order_by('id')


class TaskCreateView(LoginRequiredMixin, CreateView):  # GET/POST /tasks/create/ — создание
    model = Task  # модель
    form_class = TaskForm  # форма
    template_name = 'tasks/form.html'  # шаблон
    success_url = reverse_lazy('tasks_list')  # после успеха — список

    def form_valid(self, form):  # если форма валидна
        form.instance.author = self.request.user  # ставим автора автоматически (по ТЗ)
        messages.success(self.request, 'Задача успешно создана')  # flash успех
        return super().form_valid(form)  # сохраняем


class TaskDetailView(LoginRequiredMixin, DetailView):  # GET /tasks/<pk>/ — просмотр
    model = Task  # модель
    template_name = 'tasks/show.html'  # шаблон просмотра
    context_object_name = 'task'  # имя переменной в шаблоне


class TaskUpdateView(LoginRequiredMixin, UpdateView):  # GET/POST /tasks/<pk>/update/ — редактирование
    model = Task  # модель
    form_class = TaskForm  # форма
    template_name = 'tasks/form.html'  # шаблон
    success_url = reverse_lazy('tasks_list')  # после успеха — список

    def form_valid(self, form):  # если форма валидна
        messages.success(self.request, 'Задача успешно изменена')  # flash успех
        return super().form_valid(form)  # сохраняем


class OnlyAuthorMixin(UserPassesTestMixin):
    def test_func(self):
        obj = self.get_object()
        return obj.author_id == self.request.user.id

    def handle_no_permission(self):
        if not self.request.user.is_authenticated:
            return super().handle_no_permission()

        messages.error(self.request, "Задачу может удалить только её автор")
        return redirect("tasks_list")



class TaskDeleteView(LoginRequiredMixin, OnlyAuthorMixin, DeleteView):  # GET/POST /tasks/<pk>/delete/ — удаление
    model = Task
    template_name = "tasks/delete.html"
    success_url = reverse_lazy("tasks_list")

    def delete(self, request, *args, **kwargs):
        response = super().delete(request, *args, **kwargs)
        messages.success(request, "Задача успешно удалена")
        return response


class LabelForm(ModelForm):
    class Meta:
        model = Label
        fields = ["name"]


class LabelsListView(LoginRequiredMixin, ListView):
    model = Label
    template_name = "labels/list.html"
    context_object_name = "labels"


class LabelCreateView(LoginRequiredMixin, CreateView):
    model = Label
    form_class = LabelForm
    template_name = "labels/form.html"
    success_url = reverse_lazy("labels_list")

    def form_valid(self, form):
        messages.success(self.request, "Метка успешно создана")
        return super().form_valid(form)


class LabelUpdateView(LoginRequiredMixin, UpdateView):
    model = Label
    form_class = LabelForm
    template_name = "labels/form.html"
    success_url = reverse_lazy("labels_list")

    def form_valid(self, form):
        messages.success(self.request, "Метка успешно изменена")
        return super().form_valid(form)


class LabelDeleteView(LoginRequiredMixin, DeleteView):
    model = Label
    template_name = "labels/delete.html"
    success_url = reverse_lazy("labels_list")

    def post(self, request, *args, **kwargs):
        label = self.get_object()
        if label.tasks.exists():
            messages.error(self.request, "Невозможно удалить метку, потому что она используется")
            return redirect("labels_list")
        messages.success(self.request, "Метка успешно удалена")
        return super().post(request, *args, **kwargs)