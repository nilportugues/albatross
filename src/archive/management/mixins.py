from django.conf import settings
from django.core.mail import send_mail


class NotificationMixin(object):

    @staticmethod
    def _alert(subject, message, additional=""):

        if isinstance(message, Exception):
            import traceback
            message = "\n".join(traceback.format_exception(
                type(message), message, message.__traceback__))

        message = "{}\n\nAdditional message:\n\n{}".format(message, additional)

        send_mail(
            subject,
            message,
            settings.DEFAULT_FROM_EMAIL,
            [settings.ADMINS[0][1]]
        )
