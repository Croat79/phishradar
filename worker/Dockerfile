FROM python:3.7-slim
WORKDIR /srv/webapp
COPY ./requirements.txt /srv/webapp/requirements.txt
RUN pip install --upgrade pip
RUN pip install -r /srv/webapp/requirements.txt
