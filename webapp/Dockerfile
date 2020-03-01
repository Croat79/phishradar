FROM python:3.7-slim
WORKDIR /srv/webapp
ADD ./ /srv/webapp/
RUN chmod +x ./manage.py
RUN pip install --upgrade pip
RUN pip install -r requirements.txt
