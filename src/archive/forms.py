import pytz
import re

from datetime import datetime, timedelta

from django import forms

from users.models import User

from .models import Archive

from django.forms.utils import ErrorList


class BootstrapErrorList(ErrorList):
    def __init__(self, *args, **kwargs):
        ErrorList.__init__(self, *args, **kwargs)
        self.error_class = "errorlist alert alert-danger"


class ArchiveForm(forms.Form):

    CONCURRENCY_LIMIT = 1

    start = forms.DateTimeField(required=False)
    duration = forms.TypedChoiceField(choices=[], coerce=int, initial=60)
    query = forms.CharField(min_length=4, max_length=32)

    ANTI_PUNCTUATION_REGEX = re.compile(
        '"|\[|\]|\{|\}|:|;|,|\.|/|<|>|\?|!|@|\$|%|\^|&|\*|\(|\)|-|=|\+|…|\'')

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

        durations = []
        if user.is_authenticated():
            for t, name in User.DURATIONS:
                if t in user.durations_available:
                    durations.append((t, name))
        self.fields["duration"].choices = durations

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

    def clean(self):

        currently_running = self._user.archives.filter(is_running=True).count()
        if not self._user.is_staff:
            if currently_running > self.CONCURRENCY_LIMIT:
                raise forms.ValidationError(
                    "Sorry, we currently only allow one collection at a time.  "
                    "You'll have to stop your other collection if you want to "
                    "start another."
                )

        return self.cleaned_data

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
