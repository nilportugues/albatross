import datetime
import json
import lzma
import os
import pytz

import tweepy
from allauth.socialaccount.models import SocialApp, SocialToken
from celery.utils.log import get_task_logger
from django.utils import timezone

from albatross.celery import app

from .models import Archive
from .settings import LOOKBACK

logger = get_task_logger(__name__)


@app.task
def backfill(archive_id):
    """
    Attempt to loop backward through the Twitter REST API to collect as much
    older stuff as possible.

    :param archive_id:
    """

    archive = Archive.objects.get(pk=archive_id)

    # No sense in proceeding if this has already been done
    path = archive.get_raw_path(suffix="00000000000000")
    if os.path.exists(path):
        return

    logger.info("Backfilling for %s", archive)

    socialtoken = SocialToken.objects.get(account__user=archive.user)
    socialapp = SocialApp.objects.first()

    auth = tweepy.OAuthHandler(socialapp.client_id, socialapp.secret)
    auth.set_access_token(socialtoken.token, socialtoken.token_secret)

    window_limit = timezone.now() - datetime.timedelta(minutes=LOOKBACK)
    cursor = tweepy.Cursor(tweepy.API(auth).search, archive.query)
    collected_ids = []

    with lzma.open(path, "wb") as f:

        try:

            for tweet in cursor.items():

                # As we're going backward through time, we need to account for
                # the possibility of the same tweet coming through more than
                # once.
                if tweet.id in collected_ids:
                    continue

                if pytz.UTC.localize(tweet.created_at) < window_limit:
                    break

                logger.debug(f"Backfilling: {tweet.created_at}: {tweet.text}")

                f.write(
                    bytes(
                        json.dumps(
                            tweet._json,
                            ensure_ascii=False,
                            separators=(",", ":")
                        ) + "\n",
                        "UTF-8"
                    )
                )

                collected_ids.append(tweet.id)

        except tweepy.error.TweepError:
            pass


@app.task
def consolidate(archive_id):
    """
    As a collection is running, we're periodically creating timestamped files
    with a bunch of tweets in them.  This task is run after the collection is
    finished and all it does is roll all of those separate files into one big
    one.

    :param archive_id:
    """

    Archive.objects.get(pk=archive_id).consolidate()
