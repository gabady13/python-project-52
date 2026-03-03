from django.shortcuts import render

from .labels import (
    LabelCreateView,
    LabelDeleteView,
    LabelsListView,
    LabelUpdateView,
)
from .statuses import (
    StatusCreateView,
    StatusDeleteView,
    StatusForm,
    StatusListView,
    StatusUpdateView,
)
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