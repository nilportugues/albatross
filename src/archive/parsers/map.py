import bz2
import json


class MapParser(object):

    class NoCoordinatesFound(Exception):
        pass

    def __init__(self, archive):
        self.aggregate = []
        self.archive = archive

    def collect(self, tweet):
        try:
            self.aggregate.append(MapParser._get_refined_data(tweet))
        except MapParser.NoCoordinatesFound:
            pass

    def generate(self):
        with bz2.open(self.archive.get_map_path(), "w") as f:
            f.write(bytes(json.dumps(
                self.aggregate,
                separators=(",", ":"),
                sort_keys=True
            ), "UTF-8"))

    @classmethod
    def _get_refined_data(cls, tweet):

        if "coordinates" not in tweet:
            if "place" not in tweet:
                raise cls.NoCoordinatesFound()

        if cls._tweet_contains_coordinates(tweet):
            coordinates = (
                round(tweet["coordinates"]["coordinates"][0], 8),
                round(tweet["coordinates"]["coordinates"][1], 8)
            )
        elif cls._place_contains_bounding_box(tweet):
            coordinates = cls._get_centre(
                tweet["place"]["bounding_box"]["coordinates"][0])
        else:
            raise cls.NoCoordinatesFound()

        return [
            tweet["id_str"],
            tweet["user"]["screen_name"],
            tweet["text"],
            tweet["user"]["profile_image_url_https"],
            coordinates
        ]

    @staticmethod
    def _tweet_contains_coordinates(tweet):
        if "coordinates" in tweet:
            if tweet["coordinates"]:
                if "type" in tweet["coordinates"]:
                    if tweet["coordinates"]["type"] == "Point":
                        if tweet["coordinates"]["coordinates"]:
                            return True
        return False

    @staticmethod
    def _place_contains_bounding_box(tweet):
        if "place" not in tweet:
            return False
        if not tweet["place"]:
            return False
        if "bounding_box" not in tweet["place"]:
            return False
        if not tweet["place"]["bounding_box"]:
            return False
        if "coordinates" not in tweet["place"]["bounding_box"]:
            return False
        if not tweet["place"]["bounding_box"]["coordinates"]:
            return False
        if len(tweet["place"]["bounding_box"]["coordinates"]) > 1:
            return False
        return True

    @staticmethod
    def _get_centre(points):
        """
        Ripped shamelessly from http://stackoverflow.com/questions/18440823/

        Obviously, this doesn't work in cases where the bounding box overlaps
        the international date line, but since the box is typically very small,
        it's unlikely that'll ever happen given the locations of human
        habitation on Earth.
        """
        centroid = [0.0, 0.0]

        for point in points:
            centroid[0] += point[0]
            centroid[1] += point[1]

        total_points = len(points)
        centroid[0] /= total_points
        centroid[1] /= total_points

        return round(centroid[0], 8), round(centroid[1], 8)
