#!/bin/bash

set -e

python manage.py migrate --noinput
python manage.py collectstatic --noinput

gunicorn e_shop.wsgi --workers 2 --timeout 120
