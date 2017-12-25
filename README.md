Hedge
=====

The Hedge app. A working demo is available at https://warm-oasis-54877.herokuapp.com.

Run on Development Machine
--------------------------

To run the app on your local machine, you need Python 3.5+ and PostgreSQL installed on your computer.

1.  Create and activate virtualenv:

        python3 -m venv venv
        . venv/bin/activate

2.  Install package dependencies:

        pip install -r requirements.txt

3.  Create new PostgreSQL database and user:

        $ psql postgres
        psql (9.6.5)
        Type "help" for help.

        postgres=# CREATE DATABASE dbname;
        postgres=# CREATE USER dbuser WITH PASSWORD 's3cr3t';
        postgres=# ALTER ROLE dbuser SET client_encoding TO 'utf8';
        postgres=# ALTER ROLE dbuser SET default_transaction_isolation TO 'read committed';
        postgres=# ALTER ROLE dbuser SET timezone TO 'UTC';
        postgres=# ALTER USER dbuser CREATEDB;
        postgres=# GRANT ALL PRIVILEGES ON DATABASE dbname TO dbuser;

4.  Create new `.env` file:

        cp .env.example .env

5.  Fill in the required values below and you can leave the others empty:

        POSTGRES_DBNAME=dbname
        POSTGRES_USER=dbuser
        POSTGRES_PASSWORD=s3cr3t
        DJANGO_SECRET_KEY=<random string>

6.  Run the development server:

        ./manage.py migrate
        ./manage.py runserver 3000

Deploy on Dedicated Server
--------------------------

Make sure that you have [Docker](https://docs.docker.com/engine/installation/linux/docker-ce/ubuntu/) and [Docker Compose](https://docs.docker.com/compose/install/) installed.

1.  Create new `.env` file:

        cp .env.example .env

    Fill in all of the values.

2.  Build and run the containers:

        docker-compose build && docker-compose up -d


Deploy on Heroku
----------------

Make sure you have a Heroku account and [Heroku CLI](https://cli.heroku.com/) is installed on your computer.

1.  Login to Heroku:

        heroku login

2.  Create new Heroku app:

        heroku create

3.  Set the environment variables:

        heroku config:set DJANGO_SETTINGS_MODULE=config.settings.heroku
        heroku config:set DJANGO_SECRET_KEY=<value>
        heroku config:set MAILGUN_API_KEY=<value>
        heroku config:set MAILGUN_SENDER_DOMAIN=<value>
        heroku config:set DEFAULT_FROM_EMAIL=<value>

4.  Push code to server:

        git push heroku master

5.  Run database migrations and optionally create a user:

        heroku run ./manage.py migrate
        heroku run ./manage.py createsuperuser

6.  Open the app:

        heroku open
