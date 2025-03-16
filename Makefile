venv:
	python3 -m venv venv

activate:
	source venv/bin/activate

install:
	pip install -r requirements.txt

migrations:
	python3 manage.py makemigrations

migrate:
	python3 manage.py migrate

run:
	python3 manage.py runserver

test:
	python3 manage.py test

clean:
	rm -rf venv
	find . -type d -name "__pycache__" -exec rm -rf {} +

requirements:
	pip freeze > requirements.txt
