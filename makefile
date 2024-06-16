# Ir rellenando con los comandos que se vayan necesitando
export DJANGOPORT := 8001

CMD = python3 manage.py
APP = app

database:
	$(CMD) flush

runserver:
	$(CMD) runserver $(DJANGOPORT)

populate:
	@echo populate database
	$(CMD) populate

update_models:
	$(CMD) makemigrations $(APP)
	$(CMD) migrate

create_super_user:
	$(CMD) shell -c "from django.contrib.auth import get_user_model; User = get_user_model(); User.objects.create_superuser('alumnodb', 'admin@myproject.com', 'alumnodb')"

fully_update_db:
	@echo del migrations and make migrations and migrate
	rm -rf */migrations
	python3 ./manage.py makemigrations $(APP) 
	python3 ./manage.py migrate

all:
	make update_models
	make populate