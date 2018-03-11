from sys import stderr, stdout
from time import sleep

from django.conf import settings
from kombu import Connection
from tweepy import StreamListener

from albatross.logging import LogMixin
from users.models import User

from ..models import Archive
from .consumers import ArchiveConsumer
from .mixins import NotificationMixin


class StreamArchiver(LogMixin, NotificationMixin, StreamListener):

    def __init__(self, archives, verbosity=1, *args, **kwargs):

        super().__init__(*args, **kwargs)

        # A temporary storage for use in exception forensics
        self.raw_data = None

        # All archives in a stream belong to the same user
        self.user = archives[0].user

        self.verbosity = verbosity
        self.connection = Connection(settings.BROKER_URL)

        self.channels = []
        for archive in archives:
            with Connection(settings.BROKER_URL) as connection:
                consumer = ArchiveConsumer(
                    archive, connection, verbosity=self.verbosity)
                consumer.start()
                self.channels.append({
                    "archive": archive,
                    "consumer": consumer,
                    "queue": self.connection.SimpleQueue(
                        "archiver:{}".format(archive.pk)
                    ),
                })

    def set_verbosity(self, verbosity):
        self.logger.info(
            "Setting {} stream verbosity to {}".format(self.user, verbosity))
        self.verbosity = verbosity
        for channel in self.channels:
            channel["consumer"].set_verbosity(self.verbosity)

    def on_data(self, raw_data):
        self.raw_data = raw_data
        return StreamListener.on_data(self, raw_data)

    def on_status(self, status):

        for channel in self.channels:

            archive = channel["archive"]
            queue = channel["queue"]
            query = archive.query.lower()

            if query in status.text.lower():
                queue.put(status._json)
            elif hasattr(status, "retweeted_status"):
                if query in status.retweeted_status.text.lower():
                    queue.put(status._json)
                elif hasattr(status.retweeted_status, "quoted_status"):
                    if query in status.retweeted_status.quoted_status["text"].lower():  # NOQA: E501
                        queue.put(status._json)
            elif hasattr(status, "quoted_status"):
                if query in status.quoted_status["text"].lower():
                    queue.put(status._json)

    def on_exception(self, exception):

        additional = "Source: {}".format(self.raw_data)

        self._alert(
            "Collector exception [listener]", exception, additional)

        stderr.write("\n\nEXCEPTION:\n{}\n\nSource: {}\n".format(
            exception, additional))

        self.close_log()

        return False

    def on_error(self, status_code):

        message = str(status_code)
        if status_code == 401:
            message = (
                f"Twitter issued a 401 for {self.user}, so they've been "
                f"kicked."
            )
            self.user.status = User.STATUS_DISABLED
            self.user.save(update_fields=("status",))

        self._alert("Collector Twitter error", message)

        stderr.write("ERROR: Twitter responded with {}".format(status_code))

        self.close_log()

        return False

    def on_disconnect(self, notice):
        """
        This is what happens if *Twitter* sends a disconnect, not if we
        disconnect from the stream ourselves.
        """
        self._alert("Collector disconnect", str(notice))
        stderr.write("\n\nTwitter disconnect: {}\n\n\n".format(notice))
        self.close_log()
        return False

    def close_log(self):

        self.connection.close()
        self.connection.release()

        # Set `should_stop` which queues the consumer to close everything up
        for channel in self.channels:
            channel["consumer"].should_stop = True

        # Now wait until the consumer has confirmed that it's finished
        for channel in self.channels:
            while not channel["consumer"].is_stopped:
                if self.verbosity > 1:
                    self.logger.info("Waiting for {} to stop".format(
                        channel["consumer"].archive)
                    )
                sleep(0.1)

        stdout.flush()

        Archive.objects.filter(
            pk__in=[__["archive"].pk for __ in self.channels]
        ).update(
            is_running=False
        )
