#!/bin/bash

docker-compose --env-file docker-environ run webapp /usr/local/bin/python /srv/webapp/manage.py fetch_all
docker-compose --env-file docker-environ run webapp /usr/local/bin/python /srv/webapp/manage.py score_all
