from rest_framework import serializers

from .models import Archive, Event


class DistillationField(serializers.HyperlinkedIdentityField):
    """
    DRF's HyperlinkedIdentityField is strangely limiting in that it doesn't
    appear to allow for the possibility that a URL lookup would require more
    than one argument.
    """

    def __init__(self, kind=None, **kwargs):
        self.view_name = "archives-distillation"
        self.distillation = kind
        serializers.HyperlinkedIdentityField.__init__(
            self, view_name=self.view_name, **kwargs)

    def get_url(self, obj, view_name, request, format):
        return self.reverse(
            self.view_name,
            kwargs={"pk": obj.pk, "kind": self.distillation},
            request=request,
            format=format
        )


class EventSerializer(serializers.ModelSerializer):

    class Meta:
        model = Event
        fields = ("label", "time")


class ArchiveSerializer(serializers.ModelSerializer):

    user_id = serializers.IntegerField()
    raw = serializers.URLField(source="get_tweets_url")
    cloud = DistillationField(source="*", kind="cloud")
    statistics = DistillationField(source="*", kind="statistics")
    map = serializers.URLField(source="get_map_url")
    events = EventSerializer(many=True)

    class Meta:
        model = Archive
        fields = (
            "id",
            "user_id",
            "query",
            "started",
            "stopped",
            "is_running",
            "total",
            "size",
            "raw",
            "cloud",
            "map",
            "statistics",
            "cloud_generated",
            "statistics_generated",
            "search_generated",
            "events",
        )
