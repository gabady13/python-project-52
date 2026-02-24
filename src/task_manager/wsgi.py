"""
WSGI config for task_manager project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/5.2/howto/deployment/wsgi/
"""

import os

from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'task_manager.settings')

application = get_wsgi_application()

try:
    from django.conf import settings

    if (
        getattr(settings, "ROLLBAR_ENABLED", False)
        and not getattr(settings, "DEBUG", True)
        and getattr(settings, "ROLLBAR_TEST_EVENT", False)
        and getattr(settings, "ROLLBAR_ACCESS_TOKEN", "")
    ):
        import rollbar

        rollbar.init(
            access_token=settings.ROLLBAR["access_token"],
            environment=settings.ROLLBAR["environment"],
            code_version=settings.ROLLBAR.get("code_version"),
            root=settings.ROLLBAR["root"],
            handler="blocking",
        )
        rollbar.report_message("Rollbar test message (wsgi startup)", level="info")
except Exception:
    # Любая ошибка в тестовой отправке не должна ломать запуск приложения
    pass