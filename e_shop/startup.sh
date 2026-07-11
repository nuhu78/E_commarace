#!/bin/bash

set -e

mkdir -p media/products
python manage.py migrate sites --noinput
python manage.py migrate --noinput
python manage.py collectstatic --noinput

echo "from django.contrib.auth import get_user_model; User = get_user_model(); User.objects.filter(is_superuser=True).exists() or User.objects.create_superuser('admin', 'admin@gmail.com', 'admin')" | python manage.py shell

gunicorn e_shop.wsgi --workers 2 --timeout 120
