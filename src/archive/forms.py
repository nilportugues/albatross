import pytz
import re

from datetime import datetime, timedelta

from django import forms

from .models import Archive

from django.forms.utils import ErrorList


class BootstrapErrorList(ErrorList):
    def __init__(self, *args, **kwargs):
        ErrorList.__init__(self, *args, **kwargs)
        self.error_class = "errorlist alert alert-danger"


class ArchiveForm(forms.Form):

    CONCURRENCY_LIMIT = 1

    query = forms.CharField(min_length=4, max_length=32)
    start = forms.DateTimeField(required=False)
    duration = forms.TypedChoiceField(
        choices=(
            (30, "30m"),
            (60, "1h"),
            (180, "3h"),
            (360, "6h"),
            (720, "12h"),
            (1440, "24h"),
            (2880, "48h"),
            (4320, "72h"),
            (10080, "7d"),
            (20160, "14d"),
            (525600, "30d"),
            (0, "∞"),
        ),
        coerce=int,
        initial=60
    )

    ANTI_PUNCTUATION_REGEX = re.compile('["\[\]{\}:;,./<>?!@$%^&*()-=+…\']')

    def __init__(self, user, *args, **kwargs):

        forms.Form.__init__(
            self, error_class=BootstrapErrorList, *args, **kwargs)

        self._user = user

        self.add_css_class("start", "form-control clearable")
        self.add_css_class("query", "form-control clearable")
        self.add_css_class("duration", "form-control")

        self.fields["query"].widget.attrs.update({
            "placeholder": "The Twitter search term",
            "required": "required"
        })
        self.fields["start"].widget.attrs.update({
            "placeholder": "The default is right now"
        })

    def clean_query(self):

        query = self.cleaned_data.get("query")

        if self.ANTI_PUNCTUATION_REGEX.search(query):
            raise forms.ValidationError("Sorry, punctuation is not permitted")

        return query.strip()

    def clean_start(self):
        now = datetime.now(tz=pytz.UTC)
        start = self.cleaned_data.get("start")
        if start and start < now:
            raise forms.ValidationError("The start time must be in the future")
        return start or now

    def save(self, *args, **kwargs):

        query = self.cleaned_data.get("query")
        start = self.cleaned_data.get("start")
        duration = self.cleaned_data.get("duration")

        stop = None
        if duration:
            stop = start + timedelta(minutes=duration)

        Archive.objects.create(
            user=self._user,
            started=start,
            stopped=stop,
            query=query
        )

    def add_css_class(self, field_name, css):
        attributes = self.fields[field_name].widget.attrs
        classes = attributes.get("class", "").split(" ") + css.split(" ")
        self.fields[field_name].widget.attrs.update({
            "class": " ".join(classes).strip()
        })
