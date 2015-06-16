from bz2 import open as bz2_open
from datetime import datetime
from json import dumps as json_dumps
from os import stat
from pytz import UTC
from sys import stdout
from threading import Thread

from django.utils import timezone

from kombu import Queue
from kombu.mixins import ConsumerMixin

from ..parsers import (
    CloudParser, ImagesParser, MapParser, SearchParser, StatisticsParser)

try:
    import ujson as json
except ImportError:
    import json


class ArchiveConsumer(ConsumerMixin, Thread):

    DISTILLATION_WINDOW = 60 * 5  # How long to wait between distillations

    def __init__(self, archive, connection, verbosity=1, *args, **kwargs):

        Thread.__init__(self, *args, **kwargs)

        self.verbosity = verbosity
        self.connection = connection
        self.archive = archive

        self.aggregates = {}

        self.raw_data = None

        self.cloud = None
        self.images = None
        self.map = None
        self.search = None
        self.statistics = None

        self.is_stopped = True
        self.last_distilled = None

    def set_verbosity(self, verbosity):
        print("Setting {} consumer verbosity to {}".format(
            self.archive, verbosity))
        self.verbosity = verbosity

    def start(self):

        self.is_stopped = False

        self.raw_data = bz2_open(self.archive.get_tweets_path(), "a")

        self.cloud = CloudParser(self.archive)
        self.images = ImagesParser()
        self.map = MapParser(self.archive)
        self.search = SearchParser()
        self.statistics = StatisticsParser(self.archive)

        self.last_distilled = datetime.now(tz=UTC)

        Thread.start(self)

        if self.verbosity > 0:
            print("Consumer started for archive #{}".format(self.archive.pk))

    def get_consumers(self, consumer_class, channel):

        if not self.archive.allow_consumption:
            return []

        return [consumer_class(
            Queue("archiver:{}".format(self.archive.pk)),
            callbacks=[self.on_message],
            accept=["json"]
        )]

    def on_message(self, tweet, message):

        timer = datetime.now()

        self.archive.total += 1

        # Remember: it won't write in real-time because of the buffer, so the
        # file size won't change for blocks at a time.
        self.raw_data.write(bytes(json_dumps(
            tweet, ensure_ascii=False, separators=(",", ":")) + "\n", "UTF-8"))

        self.cloud.collect(tweet)
        self.images.collect(tweet)
        self.statistics.collect(tweet)
        self.map.collect(tweet)
        if self.archive.allow_search:
            self.search.collect(tweet)

        stdout.flush()

        message.ack()

        now = timezone.now()
        if self.verbosity > 2:
            print("{}: {} Message processed: {}".format(
                self.archive, now, now - timer))

        window = self.DISTILLATION_WINDOW
        if (now - self.last_distilled).total_seconds() > window:
            self._write_distillations()
        elif self.verbosity > 2:
            print("Skipping distillation")

    def on_consume_ready(self, connection, channel, consumers, **kwargs):
        if self.verbosity > 1:
            print('Readying consumption for "{}" (#{})'.format(
                self.archive.query,
                self.archive.pk
            ))
        self._compile_aggregates()

    def on_consume_end(self, connection, channel):

        if self.verbosity > 1:
            print('Closing consumption for "{}" (#{})'.format(
                self.archive.query,
                self.archive.pk
            ))

        self.raw_data.close()
        self._write_distillations(rate_limit=False)
        self.is_stopped = True

    def _write_distillations(self, rate_limit=True):

        now = timezone.now()

        if self.verbosity > 1:
            print("Writing aggregates for {}".format(self.archive))

        self.last_distilled = now
        self.map.generate()
        self.archive.cloud = self.cloud.generate()
        self.archive.cloud_generated = now
        self.archive.statistics = self.statistics.generate()
        self.archive.statistics_generated = now
        self.archive.images = self.images.generate()
        self.archive.images_generated = now
        self.archive.total = self.statistics.aggregate["total"]
        self.archive.size = stat(self.archive.get_tweets_path()).st_size
        self.archive.save(update_fields=(
            "cloud", "cloud_generated",
            "images", "images_generated",
            "statistics", "statistics_generated",
            "map_generated", "size", "total"
        ))

    def _compile_aggregates(self):

        if self.verbosity > 1:
            print("Compiling aggregates for {}".format(self.archive))

        self.aggregates = {
            "cloud": [],
            "statistics": {},
            "map": []
        }

        last_tweet_time = ""
        self.archive.total = 0
        with bz2_open(self.archive.get_tweets_path()) as f:
            try:
                for line in f:
                    if self.should_stop:
                        if self.verbosity > 1:
                            print("Stopping aggregate compilation for {}".format(self.archive))
                        return
                    last_tweet_time = self._parse_line(line)
            except (EOFError, OSError):
                pass  # This happens when the file is partially written to.

        self.archive.total = self.statistics.aggregate["total"]

        if self.verbosity > 0:
            print(
                "Aggregate compilation for {} complete. "
                "{} tweets accounted for. "
                "The last tweet was created at {}".format(
                    self.archive,
                    self.archive.total,
                    last_tweet_time
                )
            )

    def _parse_line(self, line):

        last_tweet_time = ""

        try:
            tweet = json.loads(str(line.strip(), "UTF-8"))
            last_tweet_time = tweet.get("created_at")
        except ValueError:
            pass  # If the line is corrupted, we have to ignore it.
        else:
            self.map.collect(tweet)
            self.cloud.collect(tweet)
            self.images.collect(tweet)
            self.statistics.collect(tweet)
            if self.archive.allow_search:
                self.search.collect(tweet)

        return last_tweet_time
