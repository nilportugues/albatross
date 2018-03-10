import logging


class LogMixin:
    """
    Use this mixin to do logging:

      self.logger.debug("My debugging message")
    """
    _logger = None

    @property
    def logger(self):

        if self._logger:
            return self._logger

        self._logger = logging.getLogger(
            "albatross." + self.__class__.__module__)

        return self.logger
