import bz2
import datetime
import os
import pytz

from django.core.management.base import BaseCommand

from ...models import Archive
from ...parsers import (
    CloudParser, ImagesParser, MapParser, SearchParser, StatisticsParser)

try:
    import ujson as json
except ImportError:
    import json


class Command(BaseCommand):

    def add_arguments(self, parser):
        parser.add_argument(
            '--archive',
            action='store',
            dest='archive',
            default=None,
            help='Only distill this archive'
        )

    def handle(self, *args, **options):

        archive = options.get("archive")
        if archive:
            self._distill(Archive.objects.get(pk=archive))
            return

        for archive in Archive.objects.filter(is_running=False):
            self._distill(archive)

    @staticmethod
    def _distill(archive):

        print('Distilling "{}" (#{})'.format(archive, archive.pk))

        cloud = CloudParser(archive)
        images = ImagesParser()
        geography = MapParser(archive)
        search = SearchParser()
        statistics = StatisticsParser(archive)

        with bz2.open(archive.get_tweets_path()) as f:

            try:

                for line in f:

                    try:
                        tweet = json.loads(str(line.strip(), "UTF-8"))
                    except ValueError:
                        pass  # If the line is corrupted, we have to ignore it.
                    else:
                        cloud.collect(tweet)
                        images.collect(tweet)
                        geography.collect(tweet)
                        statistics.collect(tweet)
                        if archive.allow_search:
                            search.collect(tweet)

            except (EOFError, OSError):
                pass  # This happens when the file is partially written.

        stopped = datetime.datetime.now(tz=pytz.UTC)
        if archive.stopped and archive.stopped < stopped:
            stopped = archive.stopped

        geography.generate()

        archive.cloud = cloud.generate()
        archive.statistics = statistics.generate()
        archive.images = images.generate()

        archive.cloud_generated = stopped
        archive.statistics_generated = stopped
        archive.images_generated = stopped

        archive.total = statistics.aggregate["total"]
        archive.size = os.stat(archive.get_tweets_path()).st_size

        archive.save(update_fields=(
            "cloud", "cloud_generated",
            "images", "images_generated",
            "statistics", "statistics_generated",
            "map_generated", "size", "total"
        ))
