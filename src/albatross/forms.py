from django import forms
from django.conf import settings
from django.core.mail import EmailMessage


class BootstrapMixin(object):
    def __init__(self):
        for field_name in self.fields.keys():
            self.fields[field_name].widget.attrs.update(
                {"class": "form-control"})


class ContactForm(BootstrapMixin, forms.Form):

    DEPARTMENT_GENERAL = "info"
    DEPARTMENT_SALES = "sales"
    DEPARTMENT_TECHNICAL = "webmaster"
    DEPARTMENTS = (
        (DEPARTMENT_GENERAL,   "General Inquiry"),
        # (DEPARTMENT_SALES,     "Sales Questions"),
        # (DEPARTMENT_TECHNICAL, "Technical Support")
    )

    department = forms.ChoiceField(
        DEPARTMENTS,
        initial=DEPARTMENT_GENERAL,
        widget=forms.widgets.HiddenInput
    )
    reply_to = forms.EmailField(label="Your Email Address")
    subject = forms.CharField(max_length=128)
    body = forms.CharField(label="Message", widget=forms.widgets.Textarea)

    def __init__(self, *args, **kwargs):
        forms.Form.__init__(self, *args, **kwargs)
        BootstrapMixin.__init__(self)

    def send(self):
        EmailMessage(
            subject=self.cleaned_data["subject"],
            body=self.cleaned_data["body"],
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=["{}@tweetpile.com".format(self.cleaned_data["department"])],
            bcc=["daniel@tweetpile.com"],
            headers={
                "Reply-To": self.cleaned_data["reply_to"]
            }
        ).send()
