import lzma
import json

from django.utils.timezone import now


class RawParser:

    def __init__(self, archive):
        self.archive = archive
        self.log = ""

    def collect(self, tweet):
        self.log += json.dumps(
            tweet,
            ensure_ascii=False,
            separators=(",", ":")
        ) + "\n"

    def generate(self):
        suffix = now().strftime("%Y%m%d%H%M%S")
        with lzma.open(self.archive.get_raw_path(suffix), "wb") as f:
            f.write(bytes(self.log, "UTF-8"))
