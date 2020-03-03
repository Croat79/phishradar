# ctihq

    ░▒▓ ctihq ▓▒░ Your very own phishing detector

    ∙∙┌─────────────┬────────────────▄
      │▓███▓▒▀▓███▓ ▒▓█ ░▒▓█  ▓████▓ ▐
      ▓█┐   ▒▌ ▓█  ▀│▓█  ▒▓█ ▓█  ░▒▓█▐
      ▓█│   ▀  ▓█ ▓█│▓██████ ▓█   ▒▓█▐
      ▓█│    ▐ ▓█ ▒█│▓█  ▒▓█ ▓█  ■ ▓█▐
      ▓██  ▒██ ▒█ ▒█│▒█  ▒▓█ ▒█   ▌▓█▐
      │░▒▓███  ░█ ░█│░█  ░▒█  ░▒████∙▐
    ∙∙└─────────────┴────────────────▀

## Description

* Easily customizable phishing domains scoring application based on cert streams.
* Scales up thanks to parallel processing done with Redis and Celery.
* You are welcome to use the built-in algorithms (located in webapp/certstreams/scoring.py) or to develop your own (sharing is greatly appreciated).
* Works pretty well with defaults so in some cases your organization can stay even 24 hours ahead of phishing threats reported by popular feeds.

## Installation

### The simple version (for testing out)

Assuming you have the latest Docker (and docker-compose):

    % docker-compose --env-file ./docker-environ up
    % ./bin/init.sh

Now open http://localhost/admin and enable at least one source.

    % ./bin/do_all.sh

View results at http://localhost/admin/certstreams/domain/

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
    user@host:~/ctihq$ sudo chmod ug+x /usr/local/bin/docker-compose
    user@host:~/ctihq$ sudo chown :docker /usr/local/bin/docker-compose

Final touch:

    user@host:~/ctihq$ sudo usermod -aG docker user

Now "reload" with new groups:

    user@host:~/ctihq$ su - $USER

#### Deploy:

    user@host:~/ctihq$ docker-compose --env-file ./docker-environ up --build --scale worker_fetching=8 --scale worker_scoring=8 -d

No worries about scheduler exiting, execute the command below (creates default user admin:admin):

    user@host:~/ctihq$ ./bin/init.sh

#### Select sources to pull from:

- Login at http://admin:admin@yourserver/admin
- Go to Sources and check "Enable" option for selected objects

Or enable all:

    user@host:~/ctihq$ docker-compose --env-file ./docker-environ run webapp /usr/local/bin/python /srv/webapp/manage.py enable_all


#### Initiate (or wait):

    user@host:~/ctihq$ ./bin/do_all.sh

#### Review results

- Login at http://admin:admin@yourserver/admin
- Go to Domains section

## Documentation

### Adding keywords

* Homoglyphs are created for each new keyword (configurable in `webapp/app/config.py:CERTSTREAMS_GENERATORS_HOMOGLYPHS`).
* Partial keywords add a bit to the domain scoring.

## Notes

* Make sure NOT to expose your admin panel in the public network, there's no need for that. The application may live comfortably behind NAT.
* Application needs to be restarted after new keywords or TLDs are added.

### Checking up on the webapp container

    user@host:~/ctihq$ docker-compose exec webapp bash

### Starting from scratch

    user@host:~/ctihq$ docker-compose down -v --rmi all

### Reset scores for all domains

    user@host:~/ctihq$ docker-compose --env-file ./docker-environ run webapp /usr/local/bin/python /srv/webapp/manage.py score_reset

### Run cleaning manually

    user@host:~/ctihq$ docker-compose --env-file ./docker-environ run webapp /usr/local/bin/python /srv/webapp/manage.py cleaning

### Deleting data

    user@host:~/ctihq$ docker-compose exec webapp bash
    # ./manage.py shell
    >>> from certstreams import models
    >>> models.Source.objects.all().delete()
    >>> models.Domain.objects.all().delete()
