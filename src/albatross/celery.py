import os

from celery import Celery
from dotenv import find_dotenv, load_dotenv

load_dotenv(find_dotenv())

# set the default Django settings module for the 'celery' program.
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'albatross.settings')

from django.conf import settings

app = Celery('albatross')

# Using a string here means the worker will not have to
# pickle the object when using Windows.
app.config_from_object('django.conf:settings')
app.autodiscover_tasks(lambda: settings.INSTALLED_APPS)
