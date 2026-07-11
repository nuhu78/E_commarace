#!/bin/bash

set -e

mkdir -p media/products

# Fix: socialaccount.0001_initial was applied BEFORE sites was installed.
# We need to (a) fake sites.0001 as applied, (b) create the django_site table,
# then run migrate normally.

python -c "
import os, django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'e_shop.settings')
django.setup()
from django.db import connection
from django.db.migrations.recorder import MigrationRecorder
from django.contrib.sites.models import Site

rec = MigrationRecorder(connection)

# Record sites migrations as applied
rec.migration_qs.get_or_create(app='sites', name='0001_initial')
rec.migration_qs.get_or_create(app='sites', name='0002_alter_domain_unique')

# Create django_site table if it doesn't exist
try:
    Site.objects.count()
except Exception:
    with connection.schema_editor() as schema_editor:
        schema_editor.create_model(Site)
    Site.objects.create(id=1, domain='eshop-django-app.onrender.com', name='E-Shop')
    print('Created django_site table and default site.')
else:
    print('django_site table already exists.')
"

python manage.py migrate --noinput
python manage.py collectstatic --noinput

# Create missing M2M junction table for socialaccount_socialapp_sites
python -c "
import os, django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'e_shop.settings')
django.setup()
from django.db import connection
from allauth.socialaccount.models import SocialApp
table = SocialApp.sites.through._meta.db_table
with connection.schema_editor() as schema_editor:
    if table not in connection.introspection.table_names():
        schema_editor.create_model(SocialApp.sites.through)
        print(f'Created missing table: {table}')
    else:
        print(f'Table already exists: {table}')
"

python -c "
import os, django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'e_shop.settings')
django.setup()
from django.contrib.auth import get_user_model
User = get_user_model()
if not User.objects.filter(is_superuser=True).exists():
    User.objects.create_superuser('admin', 'admin@gmail.com', 'admin')
    print('Superuser created.')
else:
    print('Superuser already exists.')
"

gunicorn e_shop.wsgi --workers 2 --timeout 120
