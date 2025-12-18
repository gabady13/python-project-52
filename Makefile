start:
	uv run python manage.py runserver 127.0.0.1:8000

dev:
	make install && make migrate && make start

migrate:
	uv run python manage.py migrate

build:
	./build.sh

install:
	uv sync --frozen

render-start:
	gunicorn task_manager.wsgi

collectstatic:
	uv run python manage.py collectstatic --noinput