import django_filters

from .models import Archive


class ArchiveFilterSet(django_filters.FilterSet):

    started = django_filters.DateTimeFilter()
    started__lt = django_filters.DateTimeFilter(lookup_type="lt")
    started__lte = django_filters.DateTimeFilter(lookup_type="lte")
    started__gte = django_filters.DateTimeFilter(lookup_type="gte")
    started__gt = django_filters.DateTimeFilter(lookup_type="gt")

    stopped = django_filters.DateTimeFilter()
    stopped__lt = django_filters.DateTimeFilter(lookup_type="lt")
    stopped__lte = django_filters.DateTimeFilter(lookup_type="lte")
    stopped__gte = django_filters.DateTimeFilter(lookup_type="gte")
    stopped__gt = django_filters.DateTimeFilter(lookup_type="gt")

    is_running = django_filters.BooleanFilter()

    class Meta:
        model = Archive
