# phishradar

> Your very own phishing detector

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

Now open http://localhost/admin-phishradar and enable at least one source.

    % ./bin/do_all.sh

View results at http://localhost/admin-phishradar/certstreams/domain/

### Debian 11.x

#### Install dependencies:

**Source: https://docs.docker.com/install/linux/docker-ce/debian/**

    user@host:~/phishradar$ sudo apt install apt-transport-https ca-certificates curl gnupg2 software-properties-common
    user@host:~/phishradar$ curl -fsSL https://download.docker.com/linux/debian/gpg | sudo apt-key add -
    user@host:~/phishradar$ sudo apt-key fingerprint 0EBFCD88
    user@host:~/phishradar$ sudo add-apt-repository "deb [arch=amd64] https://download.docker.com/linux/debian $(lsb_release -cs) stable"
    user@host:~/phishradar$ sudo apt update
    user@host:~/phishradar$ sudo apt install docker-ce docker-ce-cli

**Source: https://docs.docker.com/compose/install/**

    user@host:~/phishradar$ sudo curl -L "https://github.com/docker/compose/releases/download/1.29.2/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
    user@host:~/phishradar$ sudo curl -L "https://raw.githubusercontent.com/docker/compose/1.29.2/contrib/completion/bash/docker-compose" -o /etc/bash_completion.d/docker-compose
    user@host:~/phishradar$ sudo chmod ug+x /usr/local/bin/docker-compose
    user@host:~/phishradar$ sudo chown :docker /usr/local/bin/docker-compose

Final touch:

    user@host:~/phishradar$ sudo usermod -aG docker user

Now "reload" with new groups:

    user@host:~/phishradar$ su - $USER

#### Download:

    user@host:~$ git clone https://github.com/tasooshi/phishradar.git
    user@host:~$ cd phishradar

#### Adjust configuration files:

    user@host:~/phishradar$ cp docker-environ.example docker-environ
    user@host:~/phishradar$ cp webapp/app/config.py.example webapp/app/config.py
    user@host:~/phishradar$ vim docker-environ
    user@host:~/phishradar$ vim webapp/app/config.py

#### Deploy:

    user@host:~/phishradar$ docker-compose --env-file ./docker-environ up --build --scale worker_fetching=4 --scale worker_scoring=4 -d

#### Initialize:

No worries about scheduler exiting, execute the command below (creates default admin user):

    user@host:~/phishradar$ ./bin/init.sh

#### Select sources to pull from:

- Login at http://admin:admin@yourserver/admin-phishradar
- Go to Sources and check "Enable" option for selected objects

Or enable all:

    user@host:~/phishradar$ docker-compose --env-file ./docker-environ run webapp /usr/local/bin/python /srv/webapp/manage.py enable_all

#### Initiate (or wait for the scheduled task to kick in):

    user@host:~/phishradar$ ./bin/do_all.sh

#### Review results

- Login at http://admin:admin@yourserver/admin-phishradar
- Go to Domains section

## Documentation

### Adding keywords

* Homoglyphs are created for each new keyword (configurable in `webapp/app/config.py:CERTSTREAMS_GENERATORS_HOMOGLYPHS`).
* Partial keywords add a bit to the domain scoring.

## Notes

* Make sure NOT to expose your admin panel in the public network, there's no need for that. The application may live comfortably behind NAT.
* Application needs to be restarted after new keywords or TLDs are added.

### Checking up on the webapp container

    user@host:~/phishradar$ docker-compose exec webapp bash

### Starting from scratch

Removing volumes (database included):

    user@host:~/phishradar$ docker-compose down -v --rmi all

Preserving volumes:

    user@host:~/phishradar$ docker-compose down --rmi all

Rebuilding containers:

    user@host:~/phishradar$ docker-compose --env-file ./docker-environ build --no-cache --force-rm
    user@host:~/phishradar$ docker-compose --env-file ./docker-environ up --force-recreate --scale worker_fetching=4 --scale worker_scoring=4 -d

Now go back to the "Initialize" section.

### Reset scores for all domains

    user@host:~/phishradar$ docker-compose --env-file ./docker-environ run webapp /usr/local/bin/python /srv/webapp/manage.py score_reset

### Run cleaning manually

    user@host:~/phishradar$ docker-compose --env-file ./docker-environ run webapp /usr/local/bin/python /srv/webapp/manage.py cleaning

### Deleting data

    user@host:~/phishradar$ docker-compose exec webapp bash
    # ./manage.py shell
    >>> from certstreams import models
    >>> models.Source.objects.all().delete()
    >>> models.Domain.objects.all().delete()

## Troubleshooting

### Docker interferes with firewall

    /etc/docker/daemon.json:

    {
        "iptables": false
    }

