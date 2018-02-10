class NotificationMixin(object):

    @staticmethod
    def _alert(subject, message, additional=""):

        if isinstance(message, Exception):
            import traceback
            message = "\n".join(traceback.format_exception(
                type(message), message, message.__traceback__))

        message = "{}\n\nAdditional message:\n\n{}".format(message, additional)

