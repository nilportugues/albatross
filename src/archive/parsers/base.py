class TweetParser:

    @classmethod
    def get_complete_text(cls, tweet):
        """
        Twitter likes to strictly define `text` as 280characters, which means
        that if a tweet is retweeted or quoted, the text of the tweet is
        mangled to contain things like a prefixed `RT ` and a suffixed `...`.
        This is how we can always be sure we get the actual text of the tweet
        in question.
        """

        if "retweeted_status" in tweet:
            return cls.get_complete_text(tweet["retweeted_status"])

        if "quoted_status" in tweet:
            return cls.get_complete_text(tweet["quoted_status"])

        return tweet["text"]

    @staticmethod
    def get_language(tweet):
        """
        Twitter has a very strange way of identifying languages
        """

        r = tweet.get("lang") or tweet["user"].get("lang")

        if not r or r in ("in", "enen", "enes", "fil"):
            r = "und"

        r = r.lower()
        if r in ("en-gb",):
            r = "en"
        if r in ("zh-cn",):
            r = "zh"

        return r

    @classmethod
    def get_original_user(cls, tweet):

        if "retweeted_status" in tweet:
            return cls.get_original_user(tweet["retweeted_status"])

        if "quoted_status" in tweet:
            return cls.get_original_user(tweet["quoted_status"])

        return tweet["user"]["screen_name"]

    @classmethod
    def get_url(cls, tweet):

        if "retweeted_status" in tweet:
            return cls.get_url(tweet["retweeted_status"])

        if "quoted_status" in tweet:
            return cls.get_url(tweet["quoted_status"])

        return "https://twitter.com/{}/status/{}".format(
            tweet["user"]["screen_name"],
            tweet["id"]
        )

    def collect(self, tweet):
        raise NotImplementedError("Must be defined by subclass")

    def generate(self):
        raise NotImplementedError("Must be defined by subclass")
