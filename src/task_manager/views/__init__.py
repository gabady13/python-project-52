from django.shortcuts import render

from .labels import LabelsListView, LabelCreateView, LabelUpdateView, LabelDeleteView
from .statuses import StatusListView, StatusCreateView, StatusUpdateView, StatusDeleteView, StatusForm
from .tasks import (
    TaskListView,
    TaskCreateView,
    TaskDetailView,
    TaskUpdateView,
    TaskDeleteView,
    TaskForm,
    OnlyAuthorMixin,
)
from .users import (
    UsersListView,
    UserCreateView,
    UserUpdateView,
    UserDeleteView,
    UserLoginView,
    UserLogoutView,
    UserRegisterForm,
    UserUpdateForm,
    OnlySelfMixin,
)


def index(request):
    return render(request, "index.html")