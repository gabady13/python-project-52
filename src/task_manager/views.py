from django.shortcuts import render
from django.contrib.auth.models import User
from django.views.generic import ListView


def index(request):
    return render(request, "index.html")


class UsersListView(ListView):
    model = User
    template_name = "users/user_list.html"
    context_object_name = "users"

    def get_queryset(self):
        return User.objects.order_by("id")