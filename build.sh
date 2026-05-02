#!/usr/bin/env bash
set -e


pip install -r requirements.txt
python manage.py collectstatic --no-input
python manage.py migrate --run-syncdb
python manage.py shell -c "
from django.contrib.auth import get_user_model
User = get_user_model()
if not User.objects.filter(username='admin').exists():
    User.objects.create_superuser('admin', 'back@foreningsnodroppen.se', 'deneme12345')
    print('Superuser created')
else:
    print('Superuser already exists')
"