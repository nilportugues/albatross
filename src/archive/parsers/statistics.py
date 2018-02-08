import collections
import datetime
import json
import math
import os
import pycountry
import re

from django.conf import settings

from .base import TweetParser

try:
    import ujson
except ImportError:
    import json as ujson


class StatisticsParser(TweetParser):

    SENTIMENT_THRESHOLD = 0.6
    SENTIMENT_SPLIT_REGEX = re.compile(r"\W+")

    TIME_FORMATS = {
        "twitter": "%a %b %d %H:%M:%S %z %Y",
        "iso": "%Y-%m-%dT%H:00:00%z",
    }

    def __init__(self, archive):

        self.archive = archive

        self.aggregate = {
            "makeup": {"Retweets": 0, "Original Content": 0, "Replies": 0},
            "languages": collections.defaultdict(int),
            "urls": 0,
            "countries": {"complete": collections.defaultdict(int), "pie": {}},
            "hashtags": collections.defaultdict(int),
            "hours": collections.defaultdict(int),
            "mentions": collections.defaultdict(int),
            "retweetees": collections.defaultdict(int),
            "total": 0,
            "sentiments": {"Positive": 0, "Negative": 0, "Neutral": 0}
        }

        self._set_afinn_db()

    def collect(self, tweet):

        self.aggregate["languages"][self.get_language(tweet)] += 1

        if "entities" in tweet:

            # URL Count
            if "urls" in tweet["entities"]:
                self.aggregate["urls"] += len(tweet["entities"]["urls"])

            # Hashtags
            if "hashtags" in tweet["entities"]:
                for hashtag in tweet["entities"]["hashtags"]:
                    hash_text = hashtag["text"].lower()
                    if not hash_text == self.archive.hashless_query:
                        self.aggregate["hashtags"][hash_text] += 1

            # Mentions
            if "user_mentions" in tweet["entities"]:
                for mention in tweet["entities"]["user_mentions"]:
                    self.aggregate["mentions"][mention["screen_name"]] += 1

        # Countries
        if "place" in tweet and tweet["place"]:
            if "country_code" in tweet["place"]:
                country = tweet["place"]["country_code"].lower()
                if country:
                    self.aggregate["countries"]["complete"][country] += 1

        # Times
        created = datetime.datetime.strptime(
            tweet["created_at"], self.TIME_FORMATS["twitter"]
        ).strftime(self.TIME_FORMATS["iso"])
        self.aggregate["hours"][created] += 1

        # Tweet types
        if tweet["in_reply_to_user_id"]:
            self.aggregate["makeup"]["Replies"] += 1
        elif "retweeted_status" in tweet:
            self.aggregate["makeup"]["Retweets"] += 1
            user = tweet["retweeted_status"]["user"]["screen_name"]
            self.aggregate["retweetees"][user] += 1

        sentiment = self._get_sentiment(tweet)
        if sentiment > self.SENTIMENT_THRESHOLD:
            self.aggregate["sentiments"]["Positive"] += 1
        elif sentiment < self.SENTIMENT_THRESHOLD * -1:
            self.aggregate["sentiments"]["Negative"] += 1
        else:
            self.aggregate["sentiments"]["Neutral"] += 1

        self.aggregate["total"] += 1

    def generate(self):

        return bytes(json.dumps({
            "makeup": [
                ["Retweets", self.aggregate["makeup"]["Retweets"]],
                ["Original Content", self.aggregate["total"] - self.aggregate["makeup"]["Retweets"] - self.aggregate["makeup"]["Replies"]],
                ["Replies", self.aggregate["makeup"]["Replies"]]
            ],
            "languages": self._simplify_statistic(
                self._translate_from_codes(
                    self.aggregate["languages"],
                    "languages",
                    "iso639_1_code"
                )
            ),
            "urls": self.aggregate["urls"],
            "countries": {
                "complete": self.aggregate["countries"]["complete"],
                "pie": self._simplify_statistic(self._translate_from_codes(
                    self.aggregate["countries"]["complete"].copy(),
                    "countries",
                    "alpha2",
                    modifier="upper"
                ))
            },
            "hashtags": self._simplify_statistic(self.aggregate["hashtags"]),
            "hours": self._hour_ranges(self.aggregate["hours"]),
            "mentions": self._simplify_statistic(self.aggregate["mentions"]),
            "retweetees": self._simplify_statistic(self.aggregate["retweetees"]),
            "total": self.aggregate["total"],
            "sentiments": list(self.aggregate["sentiments"].items())
        }, separators=(",", ":")), "UTF-8")

    @staticmethod
    def _translate_from_codes(stats, library, lookup, modifier="lower"):

        r = {}
        for code, total in stats.items():
            try:
                kwargs = {lookup: getattr(code, modifier)()}
                name = getattr(pycountry, library).get(**kwargs).name
                r[name] = total
            except KeyError:
                pass

        if library == "languages" and "und" in stats:
            r["Undefined"] = stats["und"]

        return r

    @staticmethod
    def _simplify_statistic(stats):
        """
        Sort and limit the size of the result to a threshold number of results,
        lumping everything else into an "other" category.
        """

        # Whittle down the stats to a maximum of a top 8
        top = []
        for k, v in stats.items():
            if not top or v > min(_[1] for _ in top):
                top.append((k, v))
            top = sorted(top, key=lambda _: _[1], reverse=True)[:8]

        stats["*"] = 0
        threshold = sum([v for k, v in stats.items()]) / 12.5  # 1/8 of 100
        top_names = [_[0] for _ in top]
        delete = []

        for name, subtotal in stats.items():
            if name == "*":
                continue
            if name not in top_names:
                if subtotal < threshold:
                    stats["*"] += subtotal
                    delete.append(name)

        for name in delete:
            del(stats[name])

        return sorted(  # Second sort to put "Other" at the bottom
            sorted(  # First sort to get the 8 winners
                list(stats.items()),
                key=lambda _: _[1],
                reverse=True
            )[:8],
            key=lambda _: 0 if _[0] == "*" else _[1],
            reverse=True
        )

    @staticmethod
    def _hour_ranges(hours):
        r = {"times": [], "data": []}
        for k, v in list(sorted(hours.items(), key=lambda _: _[0])):
            r["times"].append(k)
            r["data"].append(v)
        return r

    def _set_afinn_db(self):
        db = os.path.join(
            settings.BASE_DIR, "archive", "db", "sentiment.json")
        with open(db) as f:
            self._afinn = ujson.load(f)

    def _get_sentiment(self, tweet):
        text = self.get_complete_text(tweet)
        text = self._split_camel_case(text.replace("#", ""))
        words = self.SENTIMENT_SPLIT_REGEX.split(text.lower())
        sentiments = [self._afinn.get(s, 0) for s in words]
        if not sentiments:
            return 0
        return round(sum(sentiments) / math.sqrt(len(sentiments)), 2)

    @staticmethod
    def _split_camel_case(s):
        matches = re.finditer(
            '.+?(?:(?<=[a-z])(?=[A-Z])|(?<=[A-Z])(?=[A-Z][a-z])|$)', s)
        return " ".join([m.group(0) for m in matches])
