import json
import numpy

from .base import TweetParser


class ImagesParser(TweetParser):

    def __init__(self):
        self.aggregate = {}

    def collect(self, tweet):
        if "entities" in tweet:
            if "media" in tweet["entities"]:
                for media in tweet["entities"]["media"]:
                    if media["type"] in ("photo", "animated_gif"):
                        image = media["media_url_https"]
                        if "video_thumb" not in image:
                            if image not in self.aggregate:
                                self.aggregate[image] = {
                                    "total": 0,
                                    "url": self.get_url(tweet),
                                    "users": []
                                }
                            self.aggregate[image]["total"] += 1
                            self.aggregate[image]["users"].append(
                                tweet["user"]["screen_name"]
                            )

    def generate(self):
        return bytes(
            json.dumps(
                self._calculate_image_weight(self.aggregate),
                separators=(",", ":")
            ),
            "UTF-8"
        )

    def _reduce_images(self, images, threshold=1):

        if len(images.keys()) <= 300:
            return images

        r = {}
        for url, data in images.items():
            if data["total"] > threshold:
                r[url] = data

        return self._reduce_images(r, threshold + 1)

    def _calculate_image_weight(self, images):

        if not images:
            return []

        images = self._reduce_images(images)

        array = numpy.array([_["total"] for _ in images.values()])
        buckets = [
            numpy.percentile(array, 10),
            numpy.percentile(array, 30),
            numpy.percentile(array, 50),
            numpy.percentile(array, 70),
            numpy.percentile(array, 90)
        ]

        r = []
        for url, data in images.items():
            total = data["total"]
            if total > buckets[4]:
                rank = 5
            elif total > buckets[3]:
                rank = 4
            elif total > buckets[2]:
                rank = 3
            elif total > buckets[1]:
                rank = 2
            else:
                rank = 1
            r.append([url, rank, images[url]["url"], images[url]["users"]])

        return r
