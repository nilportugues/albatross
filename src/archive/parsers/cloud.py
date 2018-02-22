import json
import re

from .base import TweetParser


class CloudParser(TweetParser):

    def __init__(self, archive):
        self.index = {}
        self.query_regex = re.compile(re.escape(archive.query), re.IGNORECASE)

    BUCKETS = 300
    BUCKET_SIZES = range(10, 310)

    ANTI_PUNCTUATION_REGEX = re.compile('["\[\]{}:;,./<>?!@#$%^&*()\-=+…\'\d]')

    STOP_WORDS = {
        "*": [
            "rt", "de", "the",
        ],
        "en": [
            "and", "or", "you", "a", "to", "be", "by", "on", "from", "is",
            "at", "it", "its", "it's", "it’s", "of", "–", "|", "but", "do",
            "so", "for", "not", "the", "in", "are", "will", "this", "as",
            "that", "with", "an", "than", "amp", "that's",
        ],
        "el": [
            "και", "αν", "τον", "τα", "την", "τη", "το", "είναι", "ο", "ότι",
            "του", "σε", "θα", "δεν", "για", "που", "οι", "να", "ή", "η",
            "στο", "με", "ωστε", "μου", "τι", "αυτο", "αυτό", "στις", "τις",
            "κι", "απο", "τους", "αλλά", "αλλα", "από", "της", "στην", "ειναι",
            "σας", "μετά", "ακόμα", "ακόμη", "πως", "των", "ήδη", "οτι", "μην",
        ],
        "nl": [
            "de", "het", "voor", "en", "naar", "met", "dit", "is", "die",
            "ook", "te", "bij", "zo", "om", "wat", "op", "van", "in", "ik",
            "dat", "er", "aan", "tot", "een",
        ]
    }

    def collect(self, tweet):
        text = self.query_regex.sub("", self.get_complete_text(tweet))
        for word in text.split():
            word = self.ANTI_PUNCTUATION_REGEX.sub("", word.lower()).strip()
            stop_words = self._get_stop_words(self.get_language(tweet))
            if word and word not in stop_words:
                if "http" not in word:
                    if word not in self.index:
                        self.index[word] = 0
                    self.index[word] += 1

    def generate(self):

        # Since we need a min & max, we kick any index less than 2.
        if len(list(self.index.keys())) < 2:
            return "[]"

        # Sort and reduce the index
        index = sorted(
            self.index.items(), key=lambda _: _[1], reverse=True)[1:500]

        frequency_max = index[0][1]
        frequency_min = index[-1][1]
        bucket_size = (frequency_max + 1 - frequency_min) / self.BUCKETS

        r = []
        for word, total in index:
            bucket = int((total - frequency_min) / bucket_size)
            r.append({
                "text": word,
                "size": self.BUCKET_SIZES[bucket]
            })

        return bytes(json.dumps(r, separators=(",", ":")), "UTF-8")

    def _get_stop_words(self, language):
        return self.STOP_WORDS["*"] + self.STOP_WORDS.get(language, [])
