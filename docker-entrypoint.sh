#!/bin/bash
set -e

POSTGRES_PORT=5432
FILE_PATH=./fixtures/dummy_data.json

echo "Waiting for PostgreSQL..."
sleep 10

echo "Applying migrations..."
python manage.py migrate

if [ -f $FILE_PATH ]; then
    echo "Filling database with dummy data..."
    python manage.py loaddata $FILE_PATH
fi

echo "Starting server..."
exec "$@"