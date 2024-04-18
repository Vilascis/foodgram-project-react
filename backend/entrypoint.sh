#!/bin/bash
set -e
python manage.py migrate
python manage.py collectstatic
cp -r /app/static/. /backend_static/static/
python manage.py csv
exec "$@"