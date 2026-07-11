#!/bin/bash

set -e

mkdir -p media/products

# Clean up fake sites migration records from previous bad deploys
# Uses python -c directly to avoid Django shell auto-import bugs
python -c "
import os, django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'e_shop.settings')
django.setup()
from django.db.migrations.recorder import MigrationRecorder
from django.db import connection
try:
    recorder = MigrationRecorder(connection)
    deleted, _ = recorder.migration_qs.filter(app='sites').delete()
    if deleted:
        print(f'Cleaned up {deleted} fake sites migration record(s)')
    else:
        print('No fake sites records to clean up')
except Exception as e:
    print(f'Cleanup skipped: {e}')
"

python manage.py migrate --noinput
python manage.py collectstatic --noinput

# Create superuser if none exists (uses python -c to avoid shell auto-import bugs)
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
