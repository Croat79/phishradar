FROM python:3.7-slim
WORKDIR /srv/webapp
ADD ./webapp /srv/webapp/
RUN pip install --upgrade pip
RUN pip install -r /srv/webapp/requirements.txt
RUN pip install flower
