FROM python:3.6
MAINTAINER Nash <nashruddin.amin@gmail.com>

ENV DJANGO_SETTINGS_MODULE config.settings.production

ADD . /app
ADD ./docker/django/server.sh /server.sh

RUN chmod +x /server.sh && \
    cd /app && \
    apt-get update && \
    pip install -r requirements.txt

WORKDIR /app
CMD ["/server.sh"]