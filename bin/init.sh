#!/bin/bash

docker-compose run webapp /usr/local/bin/python /srv/webapp/manage.py makemigrations
docker-compose run webapp /usr/local/bin/python /srv/webapp/manage.py migrate
docker-compose run webapp /usr/local/bin/python /srv/webapp/manage.py collectstatic --no-input
docker-compose run webapp /usr/local/bin/python /srv/webapp/manage.py shell -c "from django.contrib.auth.models import User; User.objects.create_superuser('admin', 'admin@localhost', 'admin')"
docker-compose run webapp /usr/local/bin/python /srv/webapp/manage.py fetch_sources
docker-compose run webapp /usr/local/bin/python /srv/webapp/manage.py init_sources
docker-compose run webapp /usr/local/bin/python /srv/webapp/manage.py loaddata ./fixtures/keywords.json
docker-compose run webapp /usr/local/bin/python /srv/webapp/manage.py loaddata ./fixtures/tasks.json
docker-compose run webapp /usr/local/bin/python /srv/webapp/manage.py loaddata ./fixtures/tld.json