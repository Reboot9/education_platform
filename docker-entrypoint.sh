#!/bin/sh
set -e

# wait for Postgres
./wait-for-it.sh $POSTGRES_HOST:$POSTGRES_PORT -t 60

# run migrations, collect media, start the server
until python3 manage.py migrate
do
  echo "Waiting for the database to be ready..."
  sleep 2
done

echo "Database is ready."

python manage.py collectstatic --noinput


exec $@