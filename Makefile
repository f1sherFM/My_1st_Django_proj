.PHONY: install migrate run test check lint format

install:
	pip install -r requirements.txt

migrate:
	python manage.py migrate

run:
	python manage.py runserver

test:
	python manage.py test

check:
	python manage.py check

lint:
	ruff check .
	black --check .
	isort --check-only .

format:
	black .
	isort .
	ruff check . --fix
