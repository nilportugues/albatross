import bz2
import functools

from datetime import datetime

from django.core.urlresolvers import reverse
from django.contrib import messages
from django.http import StreamingHttpResponse
from django.shortcuts import get_object_or_404
from django.views.generic import FormView
from rest_framework import generics, permissions
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.renderers import JSONRenderer, BrowsableAPIRenderer

from .forms import ArchiveForm
from .filters import ArchiveFilterSet
from .models import Archive
from .serializers import ArchiveSerializer
from .parsers.base import TweetParser

try:
    import ujson as json
except ImportError:
    import json


class IndexView(FormView):

    template_name = "archive/index.html"
    form_class = ArchiveForm

    def form_valid(self, form):
        form.save()
        return FormView.form_valid(self, form)

    def get_form_kwargs(self):
        kwargs = FormView.get_form_kwargs(self)
        kwargs["user"] = self.request.user
        return kwargs

    def get_success_url(self):
        messages.success(
            self.request,
            "Thanks, your stream will be captured.  Just return to this page "
            "when the time's up and you'll be able to download it."
        )
        return reverse("index")


class ArchiveListView(generics.ListAPIView):
    queryset = Archive.objects.filter(
        status=Archive.STATUS_ACTIVE).order_by("-started")
    serializer_class = ArchiveSerializer
    permission_classes = (permissions.AllowAny,)
    renderer_classes = (JSONRenderer, BrowsableAPIRenderer)
    filter_class = ArchiveFilterSet


class ArchiveDetailView(generics.RetrieveAPIView):
    queryset = Archive.objects.filter(
        status=Archive.STATUS_ACTIVE
    ).prefetch_related("events").order_by("-started")
    serializer_class = ArchiveSerializer
    permission_classes = (permissions.AllowAny,)
    renderer_classes = (JSONRenderer, BrowsableAPIRenderer)
    filter_class = ArchiveFilterSet


class ArchiveSubsetView(APIView):
    """
    Pulls down a subset of a compressed archive.  This can be slow and CPU-
    intensive, so maybe it should go away?  If we remove it though, something
    else will have to power the text view, or we'll have to drop it completely.
    """

    def get(self, request, *args, **kwargs):
        """
        Totally override the default behaviour and ignore the whole idea of a
        serializer.  DRF 3.2.x doesn't support dynamic field generation in
        serializers, so this was the next logical option.
        """

        keys = self._get_split_fields("keys")
        required_fields = self._get_split_fields("required")
        archive = get_object_or_404(Archive, pk=kwargs.get("pk"))

        r = []
        with bz2.open(archive.get_tweets_path()) as f:

            try:

                for line in f:

                    skip = False

                    try:
                        tweet = json.loads(str(line.strip(), "UTF-8"))
                    except ValueError:
                        continue  # If we can't decode the tweet, we move on

                    for required in required_fields:
                        if required not in tweet or not tweet[required]:
                            skip = True

                    if skip:
                        continue

                    r.append(
                        [self.get_parsed_attribute(tweet, f) for f in keys]
                    )

            # Exit the read in the event that the archive isn't finished writing
            except EOFError:
                pass

        return Response(r)

    def _get_split_fields(self, key):
        required_fields = self.request.GET.get(key, "")
        if required_fields:
            return required_fields.split(",")
        return []

    @classmethod
    def get_parsed_attribute(cls, tweet, field_name):

        try:
            r = functools.reduce(
                cls.smart_getattr, field_name.split("."), tweet)
        except (AttributeError, IndexError):
            # We can assume that either the value is missing, or that key
            # doesn't exist.  Either way, there's no harm.
            return None

        # JSON doesn't like datetime objects
        if isinstance(r, datetime):
            r = r.isoformat()

        return r

    @staticmethod
    def smart_getattr(obj, key):

        if key.startswith("_"):
            return None

        if key == "url":
            if "user" in obj:
                return TweetParser.get_url(obj)

        if isinstance(obj, list):
            try:
                return list.__getitem__(obj, int(key))
            except IndexError:
                return None

        if isinstance(obj, dict):
            try:
                return dict.__getitem__(obj, key)
            except KeyError:
                return None

        return None


class ArchiveDistillationView(APIView):

    permission_classes = (permissions.AllowAny,)

    def __init__(self, **kwargs):
        APIView.__init__(self, **kwargs)
        self.archive = None

    def get(self, request, *args, **kwargs):

        self.archive = get_object_or_404(Archive, pk=kwargs.get("pk"))

        kind = kwargs.get("kind")
        if kind == "map":
            with bz2.open(self.archive.get_map_path()) as f:
                return StreamingHttpResponse(f.readlines())

        return StreamingHttpResponse(getattr(self.archive, kind))
