start:
	uv run python manage.py runserver 0.0.0.0:8000

dev:
	make install && make migrate && make start

migrate:
	uv run python manage.py migrate