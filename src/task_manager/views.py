from django.shortcuts import render
from django import forms
from django.forms import ModelForm
from django.contrib import messages
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from django.contrib.auth.views import LoginView, LogoutView
from django.urls import reverse_lazy
from django.shortcuts import redirect

from .models import Status

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