import os
import signal
import sys
import time
import traceback
from datetime import datetime

import pytz
import tweepy
from allauth.socialaccount.models import SocialApp, SocialToken
from django.core.management.base import BaseCommand
from django.db import connections
from django.db.models.query_utils import Q
from django.db.utils import OperationalError, ProgrammingError

from albatross.logging import LogMixin
from users.models import User

from ...models import Archive
from ..listeners import StreamArchiver
from ..mixins import NotificationMixin


class Command(LogMixin, NotificationMixin, BaseCommand):
    """
    Loop forever checking the db for when to start/stop an archive.  New
    streams are stored in self.streams, keyed by the user owning the stream.
    """

    LOOP_TIME = 1
    CHILL_TIME = 30  # 420: Enhance your calm
    LISTENER_WAIT_TIME = 5  # Time to wait between starting listeners

    VERBOSITY_FILE = "/tmp/tweetpile-collector.verbosity"

    def __init__(self):

        BaseCommand.__init__(self)
        self.tracking = []
        self.streams = {}
        self.first_pass_completed = False
        self.verbosity = 1

        self._wait_for_db()

        self.socialapp = SocialApp.objects.get(pk=1)

        os.makedirs(os.path.join(Archive.ARCHIVES_DIR, "raw"), exist_ok=True)
        os.makedirs(os.path.join(Archive.ARCHIVES_DIR, "map"), exist_ok=True)

    def handle(self, *args, **options):

        self.verbosity = options.get("verbosity", self.verbosity)

        self.logger.info("Starting Collector\n")

        signal.signal(signal.SIGINT, self.exit)
        signal.signal(signal.SIGTERM, self.exit)

        try:
            self.loop()
        except Exception as e:
            self.logger.error("Exception: {}".format(e))
            self.logger.error(traceback.format_exc())
            self.exit()

    def exit(self, *args):

        self.logger.info(f"Exit called with {args}\n")

        for user, stream in self.streams.items():
            self.logger.info(f"  Killing stream for {user}: ")
            stream.disconnect()
            stream.listener.close_log()
            self.logger.info("[ DONE ]\n")

        self.logger.info("Exiting gracefully\n")
        sys.exit(0)

    def loop(self):

        while True:

            now = datetime.now(tz=pytz.UTC)

            to_start = self._get_archives_to_start(now)
            to_stop = Archive.objects.filter(stopped__lte=now, is_running=True)

            if to_start or to_stop:
                self.adjust_connections(to_start, to_stop)

            sys.stdout.flush()

            time.sleep(self.LOOP_TIME)

    def start_tracking(self, archive):

        if archive not in self.tracking:
            self.tracking.append(archive)

        archive.is_running = True
        archive.save(update_fields=("is_running",))

    def stop_tracking(self, archive):
        if archive in self.tracking:
            self.tracking.remove(archive)
        archive.is_running = False
        archive.save(update_fields=("is_running",))

    def adjust_connections(self, to_start, to_stop):

        self.logger.info("Adjusting connections: {}\n".format(self.tracking))

        users_adjusting = [a.user for a in list(to_start) + list(to_stop)]

        # Kill streams belonging to users that are either stopping or starting
        # a new collection.
        for user in users_adjusting:
            if user in self.streams:
                self.streams[user].disconnect()
                self.streams[user].listener.close_log()
                del(self.streams[user])

        for archive in to_stop:
            self.stop_tracking(archive)

        for archive in to_start:
            self.start_tracking(archive)

        # Regroup the archives so we only have one stream per user.
        groups = {}
        for archive in self.tracking:
            if archive.user in users_adjusting:
                if archive.user not in groups:
                    groups[archive.user] = []
                groups[archive.user].append(archive)

        for user, archives in groups.items():
            self.logger.info("Connecting: {}::{}\n".format(user, archives))
            try:
                api = self._authenticate(user)
                self.streams[user] = tweepy.Stream(
                    auth=api.auth,
                    listener=StreamArchiver(
                        archives, api=api, verbosity=self.verbosity)
                )
                self.streams[user].filter(
                    track=set([a.query for a in archives]),
                    async=True
                )
            except Exception as e:
                self._alert("Albatross collector exception [collector]", e)

            time.sleep(self.LISTENER_WAIT_TIME)

    def _get_archives_to_start(self, now):
        """
        If the archiver is killed unexpectedly, we need to account for the
        special case of its "first pass", where we need to re-start should-be
        ongoing archivals.  We also call ._handle_restarts() here to capture
        the special case where the stream was killed for whatever reason.
        """

        r = Archive.objects\
            .filter(started__lte=now)\
            .exclude(pk__in=[a.pk for a in self.tracking])

        if self.first_pass_completed:
            r = r.exclude(is_running=False)
            self.first_pass_completed = True

        return self._handle_restarts(
            r.filter(Q(stopped__gt=now) | Q(stopped__isnull=True))
        ).exclude(
            user__status=User.STATUS_DISABLED
        )

    def _handle_restarts(self, to_start):
        """
        For when a stream spontaneously disconnects (errors, Twitter whim)
        """

        to_restart = []
        for user, stream in self.streams.items():
            if not stream.running:
                self.logger.warning("Reconnection required: {}\n".format(user))
                for channel in stream.listener.channels:
                    to_restart.append(channel["archive"].pk)

        if not to_restart:
            return to_start

        time.sleep(self.CHILL_TIME)

        return Archive.objects.filter(
            pk__in=[a.pk for a in to_start] + to_restart)

    def _authenticate(self, user):

        socialtoken = SocialToken.objects.get(account__user=user)

        access = {
            "key": socialtoken.token,
            "secret": socialtoken.token_secret
        }
        consumer = {
            "key": self.socialapp.client_id,
            "secret": self.socialapp.secret
        }

        auth = tweepy.OAuthHandler(consumer["key"], consumer["secret"])
        auth.set_access_token(access["key"], access["secret"])

        return tweepy.API(auth)

    def _wait_for_db(self):
        try:
            self.logger.info("Looking for the database...\n")
            cursor = connections["default"].cursor()
            cursor.execute(f"SELECT count(*) FROM {SocialApp._meta.db_table}")
            assert cursor.fetchone()
            time.sleep(2)  # Chill before startup
        except (OperationalError, ProgrammingError, AssertionError):
            time.sleep(1)
            self._wait_for_db()
