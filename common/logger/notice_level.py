import logging  # noqa: LOG001

NOTICE = 25


def add_notice_logging_level():
    level_name = "NOTICE"
    level_number = NOTICE
    if hasattr(logging, level_name):
        return

    def method_on_logger_class(self, message, *args, **kwargs):
        if self.isEnabledFor(NOTICE):
            kwargs.setdefault("exc_info", False)
            kwargs.setdefault("stack_info", False)
            self._log(level_number, message, args, **kwargs)
        return

    logging._acquireLock()
    try:
        logger_class = logging.getLoggerClass()

        # Create new logging level between an INFO and a WARNING.
        logging.addLevelName(NOTICE, level_name)
        # Set method so that we can call 'logger.notice(...)'
        setattr(logger_class, level_name.lower(), method_on_logger_class)

    finally:
        logging._releaseLock()

    return
