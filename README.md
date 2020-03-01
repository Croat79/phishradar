# ctihq

    ░▒▓ ctihq ▓▒░ Your very own phishing detector

## Description

* Easily customizable phishing domains scoring application based on cert streams.
* Scales up thanks to parallel processing done with Redis and Celery.
* You are welcome to use the built-in algorithms (located in webapp/certstreams/scoring.py) or to develop your own (sharing is greatly appreciated).
* Works pretty well with defaults so in some cases your organization can stay even 24 hours ahead of phishing threats reported by popular feeds.

## Installation

### Debian 10.x

#### Download:

    user@host:~$ git clone https://github.com/tasooshi/ctihq.git
    user@host:~$ cd ctihq

#### Adjust configuration files:

    user@host:~/ctihq$ cp docker-environ.example docker-environ
    user@host:~/ctihq$ cp webapp/app/config.py.example webapp/app/config.py
    user@host:~/ctihq$ nano docker-environ
    user@host:~/ctihq$ nano webapp/app/config.py

#### Install dependencies:

**Source: https://docs.docker.com/install/linux/docker-ce/debian/**

    user@host:~/ctihq$ sudo apt install apt-transport-https ca-certificates curl gnupg2 software-properties-common
    user@host:~/ctihq$ curl -fsSL https://download.docker.com/linux/debian/gpg | sudo apt-key add -
    user@host:~/ctihq$ sudo apt-key fingerprint 0EBFCD88
    user@host:~/ctihq$ sudo add-apt-repository "deb [arch=amd64] https://download.docker.com/linux/debian $(lsb_release -cs) stable"
    user@host:~/ctihq$ sudo apt update
    user@host:~/ctihq$ sudo apt install docker-ce docker-ce-cli

**Source: https://docs.docker.com/compose/install/**

    user@host:~/ctihq$ sudo curl -L "https://github.com/docker/compose/releases/download/1.25.4/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
    user@host:~/ctihq$ sudo curl -L "https://raw.githubusercontent.com/docker/compose/1.25.4/contrib/completion/bash/docker-compose" -o /etc/bash_completion.d/docker-compose
    user@host:~/ctihq$ sudo chmod +x /usr/local/bin/docker-compose

Final touch:

    user@host:~/ctihq$ sudo usermod -aG docker user

#### Deploy:

    user@host:~/ctihq$ docker-compose up --build --scale worker_fetching=10 --scale worker_scoring=6 -d

No worries about scheduler exiting, execute the command below (creates default user admin:admin):

    user@host:~/ctihq$ ./bin/init.sh

#### Select sources to pull from:

- Login at http://admin:admin@yourserver/admin
- Go to Sources and check "Enable" option for selected objects
- Or see "Enabling all sources (via Django ORM)" below

#### Initiate (or wait):

    user@host:~/ctihq$ docker-compose run webapp /usr/local/bin/python /srv/webapp/manage.py fetch_all
    user@host:~/ctihq$ docker-compose run webapp /usr/local/bin/python /srv/webapp/manage.py score_all

#### Review results

- Login at http://admin:admin@yourserver/admin
- Go to Domains section

## Notes

* Make sure NOT to expose your admin panel in the public network, there's no need for that. The application may live comfortably behind NAT.

### Checking up on the webapp container

    user@host:~/ctihq$ docker-compose exec webapp bash

### Starting from scratch

    user@host:~/ctihq$ docker-compose down -v --rmi all

### Enabling all sources (via Django ORM)

    user@host:~/ctihq$ docker-compose exec webapp bash
    # ./manage.py shell
    >>> from certstreams import models
    >>> models.Source.objects.update(enabled=True)

### Deleting data (via Django ORM)

    user@host:~/ctihq$ docker-compose exec webapp bash
    # ./manage.py shell
    >>> from certstreams import models
    >>> models.Source.objects.all().delete()
    >>> models.Domain.objects.all().delete()
