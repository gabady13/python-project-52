import django_filters
from django import forms
from django.contrib.auth.models import User

from .models import Label, Status, Task


class TaskFilter(django_filters.FilterSet):
    status = django_filters.ModelChoiceFilter(
        queryset=Status.objects.all(),
        label="Статус",
    )
    executor = django_filters.ModelChoiceFilter(
        queryset=User.objects.all(),
        label="Исполнитель",
    )
    label = django_filters.ModelChoiceFilter(
        queryset=Label.objects.all(),
        method="filter_label",
        label="Метка",
    )
    self_tasks = django_filters.BooleanFilter(
        method="filter_self_tasks",
        widget=forms.CheckboxInput(),
        label="Только свои задачи",
    )

    class Meta:
        model = Task
        fields = ["status", "executor", "label", "self_tasks"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.form.fields["status"].widget.attrs.update({"class": "form-select ml-2 mr-3"})
        self.form.fields["executor"].widget.attrs.update({"class": "form-select mr-3 ml-2"})
        self.form.fields["label"].widget.attrs.update({"class": "form-select mr-3 ml-2"})
        self.form.fields["self_tasks"].widget.attrs.update({"class": "form-check-input mr-3"})

    def filter_label(self, queryset, name, value):
        if not value:
            return queryset
        return queryset.filter(labels=value).distinct()

    def filter_self_tasks(self, queryset, name, value):
        if not value:
            return queryset
        if not getattr(self, "request", None) or not self.request.user.is_authenticated:
            return queryset
        return queryset.filter(author=self.request.user)
