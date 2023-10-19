#!/bin/sh

# wait for Postgres
./wait-for-it.sh $POSTGRES_HOST:$POSTGRES_PORT -t 60

# run migrations, collect media, start the server
python manage.py migrate

python manage.py collectstatic --noinput


exec $@