from django.core.urlresolvers import reverse
from django.contrib import messages
from django.views.generic import FormView

from .forms import ContactForm


class ContactView(FormView):

    form_class = ContactForm
    template_name = "albatross/contact.html"

    def form_valid(self, form):
        form.send()
        messages.info(
            self.request,
            "Thank you.  Someone will reply to you shortly"
        )
        return FormView.form_valid(self, form)

    def get_success_url(self):
        return reverse("contact")
