from django.conf.urls import include, url
from django.contrib import admin
from django.views.decorators.cache import cache_page
from django.views.generic import DetailView, TemplateView
from rest_framework.urlpatterns import format_suffix_patterns

from archive.models import Archive
from archive.views import (
    IndexView, ArchiveListView, ArchiveDetailView, ArchiveDistillationView,
    ArchiveSubsetView
)

from .views import ContactView

urlpatterns = [
    url(r'^admin/', include(admin.site.urls)),
    url(r'^$', IndexView.as_view(), name="index"),
    url(
        r'^about/$',
        TemplateView.as_view(template_name="albatross/about.html"),
        name="about"
    ),
    url(r'^contact/$', ContactView.as_view(), name="contact"),
    url(
        r'^archives/(?P<pk>\d+)/text/',
        DetailView.as_view(
            model=Archive, template_name="archive/detail/text.html"),
        name="detail-text"
    ),
    url(
        r'^archives/(?P<pk>\d+)/map/',
        DetailView.as_view(
            model=Archive, template_name="archive/detail/map.html"),
        name="detail-map"
    ),
    url(
        r'^archives/(?P<pk>\d+)/images/',
        DetailView.as_view(
            model=Archive, template_name="archive/detail/images.html"),
        name="detail-images"
    ),
    url(
        r'^archives/(?P<pk>\d+)/cloud/',
        DetailView.as_view(
            model=Archive, template_name="archive/detail/cloud.html"),
        name="detail-cloud"
    ),
    url(
        r'^archives/(?P<pk>\d+)/statistics/',
        DetailView.as_view(
            model=Archive, template_name="archive/detail/statistics.html"),
        name="detail-statistics"
    ),

    url(r'^accounts/', include('allauth.urls')),

]

urlpatterns += format_suffix_patterns([
    url(
        r'^api/archives$',
        cache_page(5)(ArchiveListView.as_view()),
        name="archives"
    ),
    url(
        r'^api/archives/(?P<pk>\d+)$',
        cache_page(5)(ArchiveDetailView.as_view()),
        name="archives-detail"
    ),
    url(
        r'^api/archives/(?P<pk>\d+)/distillation/(?P<kind>(cloud|map|statistics|images))$',  # NOQA: E501
        cache_page(60 * 15)(ArchiveDistillationView.as_view()),
        name="archives-distillation"
    ),
    url(
        r'^api/archives/(?P<pk>\d+)/subset$',
        cache_page(60 * 60 * 24 * 365)(ArchiveSubsetView.as_view()),
        name="archives-subset"
    ),
])
