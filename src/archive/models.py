import datetime
import glob
import lzma
import os

import pytz
from django.conf import settings
from django.contrib.postgres.fields import ArrayField
from django.db import models

from albatross.logging import LogMixin


class Archive(LogMixin, models.Model):

    STATUS_ACTIVE = 1
    STATUS_DISABLED = 2
    STATUSES = (
        (STATUS_ACTIVE, "Active"),
        (STATUS_DISABLED, "Disabled")
    )

    ARCHIVES_DIR = os.path.join(settings.MEDIA_ROOT, "archives")
    ARCHIVES_URL = os.path.join(settings.MEDIA_URL, "archives")

    query = models.CharField(max_length=32)
    user = models.ForeignKey(
        "users.User",
        related_name="archives",
        null=True,
        on_delete=models.PROTECT
    )
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

    def calculate_size(self):
        path = os.path.join(self.ARCHIVES_DIR, "raw", f"{self.pk:05}*fjson.xz")
        return sum([os.stat(f).st_size for f in glob.glob(path)])

    def get_raw_path(self, prefix="", suffix=None):
        suffix = f"-{suffix}" if suffix else ""
        return os.path.join(
            self.ARCHIVES_DIR, "raw", f"{prefix}{self.pk:09}{suffix}.fjson.xz")

    def get_tweets(self):
        """
        Collect all tweets from all compressed files and give us a generator
        yielding one tweet per iteration.
        """
        for p in self._get_tweet_archive_paths():
            try:
                with lzma.open(p) as f:
                    for line in f:
                        yield str(line.strip(), "UTF-8")
            except EOFError:
                continue

    def get_tweets_url(self):
        if not os.path.exists(self.get_raw_path()):
            return None
        return os.path.join(self.ARCHIVES_URL, "raw", f"{self.pk:09}.fjson.xz")

    def get_map_path(self):
        return os.path.join(
            self.ARCHIVES_DIR, "map", f"{self.pk:09}.json.bz2")

    def get_map_url(self):
        return os.path.join(
            self.ARCHIVES_URL, "map", f"{self.pk:09}.json.bz2")

    def get_absolute_url(self):
        return "/archives/{}/statistics/".format(self.pk)

    @property
    def hashless_query(self):
        return self.query.replace("#", "").lower()

    def stop(self):
        self.stopped = datetime.datetime.now(tz=pytz.UTC)
        self.save(update_fields=("stopped",))

    def consolidate(self):

        consolidated_path = self.get_raw_path(prefix=".")
        if os.path.exists(consolidated_path):
            return

        self.logger.debug(f"Compiling tweets for {self}")

        # Rewrite all tweets to one compressed file
        with lzma.open(consolidated_path, "wb") as f:
            for tweet in self.get_tweets():
                f.write(bytes(tweet, "UTF-8") + b"\n")

        # Delete the rest
        for path in self._get_tweet_archive_paths():
            self.logger.debug(f"Deleting {path}")
            os.unlink(path)

        os.rename(consolidated_path, self.get_raw_path())

    def _get_tweet_archive_paths(self):
        return sorted(glob.glob(os.path.join(
            self.ARCHIVES_DIR,
            "raw",
            f"{self.pk:09}*fjson.xz"
        )))


class Event(models.Model):
    """
    Arbitrary event values for an archive that help explain behaviour.  These
    are plotted on the hours chart.
    """

    archive = models.ForeignKey(
        Archive, related_name="events", on_delete=models.CASCADE)
    time = models.DateTimeField()
    label = models.CharField(max_length=64)

    def __str__(self):
        return self.label


class Tweet(models.Model):
    """
    Created for the purpose of allowing searches of specific collections.  This
    is probably not a good idea and it's yet to be used, since large
    collections tend to produce Very Large Databases.  If we're going to have
    search, something like ElasticSearch makes more sense, but until that's
    figured out, this will stick around.
    """
    id = models.BigIntegerField(primary_key=True)
    archive = models.ForeignKey(
        "archive.Archive", related_name="tweets", on_delete=models.CASCADE)
    created = models.DateTimeField(db_index=True)
    mentions = ArrayField(
        models.CharField(max_length=64), blank=True, null=True)
    hashtags = ArrayField(
        models.CharField(max_length=280), blank=True, null=True)
    text = models.CharField(max_length=256, db_index=True)
