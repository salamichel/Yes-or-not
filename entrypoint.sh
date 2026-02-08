#!/bin/sh
set -e

echo "Waiting for PostgreSQL at db:5432..."
while ! python -c "import socket; s = socket.create_connection(('db', 5432), timeout=2); s.close()" 2>/dev/null; do
    echo "  ...PostgreSQL not ready, retrying in 1s"
    sleep 1
done
echo "PostgreSQL is ready."

echo "Applying migrations..."
python manage.py migrate --noinput

echo "Collecting static files..."
python manage.py collectstatic --noinput

echo "Starting server..."
exec "$@"
