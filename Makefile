start:
	uv run python manage.py runserver 127.0.0.1:8000

dev:
	make install && make migrate && make start

migrate:
	uv run python manage.py migrate