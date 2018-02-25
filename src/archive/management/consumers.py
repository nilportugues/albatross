from sys import stdout
from threading import Thread

from django.utils import timezone
from kombu import Queue
from kombu.mixins import ConsumerMixin

import ujson as json
from .mixins import NotificationMixin
from ..parsers import (
    CloudParser,
    ImagesParser,
    MapParser,
    RawParser,
    SearchParser,
    StatisticsParser
)


class ArchiveConsumer(NotificationMixin, ConsumerMixin, Thread):

    DISTILLATION_WINDOW = 60 * 5  # Seconds wait between distillations

    def __init__(self, archive, connection, verbosity=1, *args, **kwargs):

        super().__init__(*args, **kwargs)

        self.verbosity = verbosity
        self.connection = connection
        self.archive = archive

        self.aggregates = {}

        self.raw = None
        self.cloud = None
        self.images = None
        self.map = None
        self.search = None
        self.statistics = None

        self.is_stopped = True
        self.last_distilled = None

    def set_verbosity(self, verbosity):
        print("Setting {} consumer verbosity to {}".format(
            self.archive,
            verbosity
        ))
        self.verbosity = verbosity

    def start(self):

        self.is_stopped = False

        self.raw = RawParser(self.archive)
        self.cloud = CloudParser(self.archive)
        self.images = ImagesParser()
        self.map = MapParser(self.archive)
        self.search = SearchParser()
        self.statistics = StatisticsParser(self.archive)

        self.last_distilled = timezone.now()

        super().start()

        if self.verbosity > 0:
            print("Consumer started for archive #{}".format(self.archive.pk))

    def run(self, _tokens=1, **kwargs):
        try:
            super().run(_tokens=_tokens)
        except Exception as e:
            self._alert(
                "An error occurred whilst running the archive consumer",
                e
            )

    def get_consumers(self, consumer_class, channel):

        if not self.archive.allow_consumption:
            return []

        return [consumer_class(
            Queue(f"archiver:{self.archive.pk}"),
            callbacks=[self.callback],
            accept=["json"]
        )]

    def callback(self, tweet, message):
        try:
            self._process_message(tweet, message)
        except Exception as e:
            self._alert("An error occurred whilst processing a message", e)

    def _process_message(self, tweet, message):

        timer = timezone.now()

        self.archive.total += 1

        self.raw.collect(tweet)
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
            print("{} ({}): {} processed in {}s".format(
                self.archive.query,
                self.archive.total,
                now,
                (now - timer).total_seconds()
            ))

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

        self._write_distillations()
        self.is_stopped = True

    def _write_distillations(self):

        now = timezone.now()

        if self.verbosity > 1:
            print("Writing aggregates for {}".format(self.archive))

        self.last_distilled = now
        self.raw.generate()
        self.map.generate()
        self.archive.cloud = self.cloud.generate()
        self.archive.cloud_generated = now
        self.archive.statistics = self.statistics.generate()
        self.archive.statistics_generated = now
        self.archive.images = self.images.generate()
        self.archive.images_generated = now
        self.archive.total = self.statistics.aggregate["total"]
        self.archive.size = self.archive.calculate_size()
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
        for line in self.archive.get_tweets():
            if self.should_stop:
                if self.verbosity > 1:
                    print(f"Stopping aggregate compilation for {self.archive}")
                return
            last_tweet_time = self._parse_line(line)

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
            tweet = json.loads(line)
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
