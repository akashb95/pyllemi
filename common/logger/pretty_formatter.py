import copy
import logging

import colorama


class PrettyFormatter(logging.Formatter):
    def __init__(self, fmt, *args, **kwargs):

        super(PrettyFormatter, self).__init__(*args, **kwargs)
        self._fmt = fmt

        return

    def format(self, record: logging.LogRecord):

        record_copy = copy.copy(record)

        if record.levelno <= logging.DEBUG:
            color = "{}{}".format(colorama.Style.DIM, colorama.Fore.CYAN)
        elif record.levelno <= logging.INFO:
            color = colorama.Fore.GREEN
        elif record.levelno <= logging.WARNING:
            color = colorama.Fore.LIGHTYELLOW_EX
        elif record.levelno <= logging.ERROR:
            color = colorama.Fore.LIGHTRED_EX
        else:
            color = "{}{}".format(colorama.Style.BRIGHT, colorama.Fore.RED)

        record_copy.levelname = "{}{}{}".format(color, record.levelname, colorama.Style.RESET_ALL)
        record_copy.threadName = "{}{}{}".format(color, record.threadName, colorama.Style.RESET_ALL)
        record_copy.msg = "{}{}{}".format(color, record.msg, colorama.Style.RESET_ALL)

        self._style._fmt = self._fmt  # noqa: SLF001

        return super(PrettyFormatter, self).format(record_copy)
