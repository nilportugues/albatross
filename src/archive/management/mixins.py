class NotificationMixin(object):

    BAR = "==================================================================="

    def _alert(self, subject, message, additional=""):

        if isinstance(message, Exception):
            import traceback
            message = "\n".join(traceback.format_exception(
                type(message), message, message.__traceback__))

        message = "{}\n\nAdditional message:\n\n{}".format(message, additional)

        print(f"{self.BAR}\n{subject}\n{message}\n{self.BAR}")
