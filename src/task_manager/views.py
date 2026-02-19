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

from .models import Status, Task

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


class UserLogoutView(LogoutView):
    http_method_names = ["post"]  


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
        fields = ['name', 'description', 'status', 'executor']  # важно: author НЕ в форме (ставим автоматически)


class TaskListView(LoginRequiredMixin, ListView):  # GET /tasks/ — список задач
    model = Task  # модель
    template_name = 'tasks/list.html'  # шаблон списка
    context_object_name = 'tasks'  # имя переменной в шаблоне

    def get_queryset(self):  # определяем выборку
        return Task.objects.select_related('status', 'author', 'executor').order_by('id')  # оптимизация + порядок


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


class OnlyAuthorMixin(UserPassesTestMixin):  # миксин: удалять может только автор задачи
    def test_func(self):  # проверка допуска
        task = self.get_object()  # получаем задачу
        return task.author_id == self.request.user.id  # true если текущий юзер == автор


class TaskDeleteView(LoginRequiredMixin, OnlyAuthorMixin, DeleteView):  # GET/POST /tasks/<pk>/delete/ — удаление
    model = Task  # модель
    template_name = 'tasks/delete.html'  # шаблон подтверждения удаления
    success_url = reverse_lazy('tasks_list')  # после удаления — список

    def post(self, request, *args, **kwargs):  # переопределяем POST ради flash
        messages.success(request, 'Задача успешно удалена')  # flash успех (перед фактическим удалением)
        return super().post(request, *args, **kwargs)  # удаляем

    def handle_no_permission(self):  # если проверка миксина не прошла (не автор)
        messages.error(self.request, 'Задачу может удалить только её автор')  # flash ошибка
        return redirect(self.success_url)  # уводим в список