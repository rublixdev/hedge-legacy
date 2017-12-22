#!/bin/bash

set -e

export DJANGO_SETTINGS_MODULE=config.settings.production

function postgres_ready(){
python << END
import sys
import psycopg2
try:
    conn = psycopg2.connect(dbname="$POSTGRES_USER", user="$POSTGRES_USER", password="$POSTGRES_PASSWORD", host="postgres")
except psycopg2.OperationalError:
    sys.exit(-1)
sys.exit(0)
END
}

until postgres_ready; do
  >&2 echo "Postgres is unavailable - sleeping"
  sleep 1
done

>&2 echo "Postgres is up - continuing..."
exec $cmd

python manage.py migrate
python manage.py collectstatic --noinput
gunicorn config.wsgi -w 4 -b 0.0.0.0:5000 --chdir=/app