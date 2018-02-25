import django_filters

from .models import Archive


class ArchiveFilterSet(django_filters.FilterSet):

    started = django_filters.DateTimeFilter()
    started__lt = django_filters.DateTimeFilter(lookup_expr="lt")
    started__lte = django_filters.DateTimeFilter(lookup_expr="lte")
    started__gte = django_filters.DateTimeFilter(lookup_expr="gte")
    started__gt = django_filters.DateTimeFilter(lookup_expr="gt")

    stopped = django_filters.DateTimeFilter()
    stopped__lt = django_filters.DateTimeFilter(lookup_expr="lt")
    stopped__lte = django_filters.DateTimeFilter(lookup_expr="lte")
    stopped__gte = django_filters.DateTimeFilter(lookup_expr="gte")
    stopped__gt = django_filters.DateTimeFilter(lookup_expr="gt")

    is_running = django_filters.BooleanFilter()

    class Meta:
        model = Archive
        fields = (
            "started",
            "started__lt",
            "started__lte",
            "started__gte",
            "started__gt",
            "stopped",
            "stopped__lt",
            "stopped__lte",
            "stopped__gte",
            "stopped__gt",
            "is_running"
        )
