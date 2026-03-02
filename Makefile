.PHONY: install migrate run test check

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
