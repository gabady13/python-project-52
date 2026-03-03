from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.forms import ModelForm
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.views.generic import ListView, CreateView, UpdateView, DeleteView

from task_manager.tasks.models import Task
from task_manager.labels.models import Label


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

        if Task.objects.filter(labels=label).exists():
            messages.error(
                self.request,
                "Невозможно удалить метку, потому что она используется"
            )
            return redirect(self.success_url)

        response = super().post(request, *args, **kwargs)
        messages.success(self.request, "Метка успешно удалена")
        return response