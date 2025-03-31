# your_project/celery.py

import os
from celery import Celery

# Set the default Django settings module for the 'celery' program
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Nina_Bazar.settings')

app = Celery('Nina_Bazar')

# Load task modules from all registered Django app configs
app.config_from_object('django.conf:settings', namespace='CELERY')

# Auto-discover tasks in all installed apps
app.autodiscover_tasks()
# At the top of the file
try:
    from stock.tasks import reorder_stock
    CELERY_AVAILABLE = True
except ImportError:
    CELERY_AVAILABLE = False

# In the optimize_inventory function, replace the reordering section with:
