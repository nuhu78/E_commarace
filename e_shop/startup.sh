#!/bin/bash

set -e

mkdir -p media/products

# Fix migration state: sites was added after socialaccount already ran
python manage.py shell --no-imports -c "from django.db.migrations.recorder import MigrationRecorder; from django.db import connection; MigrationRecorder(connection).migration_qs.get_or_create(app='sites', name='0001_initial')"

python manage.py migrate --noinput
python manage.py collectstatic --noinput

echo "from django.contrib.auth import get_user_model; User = get_user_model(); User.objects.filter(is_superuser=True).exists() or User.objects.create_superuser('admin', 'admin@gmail.com', 'admin')" | python manage.py shell --no-imports

gunicorn e_shop.wsgi --workers 2 --timeout 120
