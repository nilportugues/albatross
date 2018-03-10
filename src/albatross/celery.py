import os

from celery import Celery
from django.conf import settings
from dotenv import find_dotenv, load_dotenv

load_dotenv(find_dotenv())

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "albatross.settings")

app = Celery("albatross")
app.config_from_object("django.conf:settings")
app.autodiscover_tasks(lambda: settings.INSTALLED_APPS)
