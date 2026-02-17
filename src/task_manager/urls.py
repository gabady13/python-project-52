"""
URL configuration for task_manager project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from .views import (
    index,
    UsersListView,
    UserCreateView,
    UserUpdateView,
    UserDeleteView,
    UserLoginView,
    UserLogoutView,
    StatusListView,
    StatusCreateView,
    StatusUpdateView,
    StatusDeleteView,
)


urlpatterns = [
    path("", index, name="index"),
    path('admin/', admin.site.urls),

    path("users/", UsersListView.as_view(), name="users_list"),
    path("users/create/", UserCreateView.as_view(), name="user_create"),
    path("users/<int:pk>/update/", UserUpdateView.as_view(), name="user_update"),
    path("users/<int:pk>/delete/", UserDeleteView.as_view(), name="user_delete"),
    
    path("login/", UserLoginView.as_view(), name="login"),
    path("logout/", UserLogoutView.as_view(), name="logout"),

    path('statuses/', StatusListView.as_view(), name='statuses_list'),
    path('statuses/create/', StatusCreateView.as_view(), name='status_create'),
    path('statuses/<int:pk>/update/', StatusUpdateView.as_view(), name='status_update'),
    path('statuses/<int:pk>/delete/', StatusDeleteView.as_view(), name='status_delete'),

]
