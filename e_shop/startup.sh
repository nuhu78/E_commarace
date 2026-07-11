#!/bin/bash

set -e

mkdir -p media/products

python manage.py shell -c "
import django; django.setup()
from django.db import connection
from django.db.migrations.recorder import MigrationRecorder
from django.contrib.sites.models import Site

rec = MigrationRecorder(connection)

# Record sites.0001 as applied (socialaccount ran without sites installed)
rec.migration_set.get_or_create(app='sites', name='0001_initial')

# Create django_site table if it doesn't exist yet
try:
    Site.objects.count()
except Exception:
    with connection.schema_editor() as schema_editor:
        schema_editor.create_model(Site)
    Site.objects.create(id=1, domain='eshop-django-app.onrender.com', name='E-Shop')
"

python manage.py migrate --noinput
python manage.py collectstatic --noinput

python manage.py shell -c "
from django.contrib.auth import get_user_model
User = get_user_model()
if not User.objects.filter(is_superuser=True).exists():
    User.objects.create_superuser('admin', 'admin@gmail.com', 'admin')
"

gunicorn e_shop.wsgi --workers 2 --timeout 120
