from django.contrib import messages
from django.db.models.deletion import ProtectedError
from django.shortcuts import redirect


class SafeDeleteWithProtectedErrorMixin:
    protected_error_message = ""
    success_message = ""

    def post(self, request, *args, **kwargs):
        try:
            response = super().post(request, *args, **kwargs)
        except ProtectedError:
            if self.protected_error_message:
                messages.error(request, self.protected_error_message)
            return redirect(self.success_url)

        if self.success_message:
            messages.success(request, self.success_message)
        return response