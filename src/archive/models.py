import datetime
import os
import pytz

from django.conf import settings
from django.contrib.postgres.fields import ArrayField
from django.db import models


class Archive(models.Model):

    STATUS_ACTIVE = 1
    STATUS_DISABLED = 2
    STATUSES = (
        (STATUS_ACTIVE, "Active"),
        (STATUS_DISABLED, "Disabled")
    )

    ARCHIVES_DIR = os.path.join(settings.MEDIA_ROOT, "archives")
    ARCHIVES_URL = os.path.join(settings.MEDIA_URL, "archives")

    query = models.CharField(max_length=32)
    user = models.ForeignKey("users.User", related_name="archives", null=True)
    started = models.DateTimeField(auto_created=True)
    stopped = models.DateTimeField(
        blank=True, null=True, help_text="Defaults to start + 24hours")

    is_running = models.BooleanField(default=False)
    allow_consumption = models.BooleanField(
        default=True,
        help_text="Should incoming tweets actually be consumed or just left "
                  "in the queue?"
    )
    allow_search = models.BooleanField(default=False)
    last_distilled = models.DateTimeField(blank=True, null=True)
    status = models.PositiveIntegerField(
        choices=STATUSES, default=STATUS_ACTIVE)

    cloud = models.TextField(blank=True)
    statistics = models.TextField(blank=True)
    images = models.TextField(blank=True)

    # These are used to gauge availability of the distillations
    cloud_generated = models.DateTimeField(blank=True, null=True)
    map_generated = models.DateTimeField(blank=True, null=True)
    search_generated = models.DateTimeField(blank=True, null=True)
    statistics_generated = models.DateTimeField(blank=True, null=True)
    images_generated = models.DateTimeField(blank=True, null=True)

    colour_overrides = models.TextField(
        blank=True,
        help_text="A JSON field used to override the colours used by c3 in "
                  "generating pie charts."
    )

    total = models.BigIntegerField(default=0)
    size = models.BigIntegerField(
        default=0, help_text="The size, in bytes, of the tweets field")

    class Meta:
        ordering = ("-started",)

    def __str__(self):
        return self.query

    def get_tweets_path(self):
        return os.path.join(
            self.ARCHIVES_DIR, "raw", "{:05}.fjson.bz2".format(self.pk))

    def get_tweets_url(self):
        return os.path.join(
            self.ARCHIVES_URL, "raw", "{:05}.fjson.bz2".format(self.pk))

    def get_map_path(self):
        return os.path.join(
            self.ARCHIVES_DIR, "map", "{:05}.json.bz2".format(self.pk))

    def get_map_url(self):
        return os.path.join(
            self.ARCHIVES_URL, "map", "{:05}.json.bz2".format(self.pk))

    def get_absolute_url(self):
        return "/archives/{}/statistics/".format(self.pk)

    @property
    def hashless_query(self):
        return self.query.replace("#", "").lower()

    def stop(self):
        self.stopped = datetime.datetime.now(tz=pytz.UTC)
        self.save(update_fields=("stopped",))


class Event(models.Model):
    """
    Arbitrary event values for an archive that help explain behaviour.  These
    are plotted on the hours chart.
    """

    archive = models.ForeignKey(Archive, related_name="events")
    time = models.DateTimeField()
    label = models.CharField(max_length=64)

    def __str__(self):
        return self.label


class Tweet(models.Model):
    """
    Created for the purpose of allowing searches of specific collections.  This
    is probably not a good idea and it's yet to be used, since large collections
    tend to produce Very Large Databases.  If we're going to have search,
    something like ElasticSearch makes more sense, but until that's figured out,
    this will stick around.
    """
    id = models.BigIntegerField(primary_key=True)
    archive = models.ForeignKey("archive.Archive", related_name="tweets")
    created = models.DateTimeField(db_index=True)
    mentions = ArrayField(
        models.CharField(max_length=64), blank=True, null=True)
    hashtags = ArrayField(
        models.CharField(max_length=140), blank=True, null=True)
    text = models.CharField(max_length=256, db_index=True)
