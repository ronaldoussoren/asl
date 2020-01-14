import logging
import os
import sys

import asl

_LOGGING2ASL = {
    logging.DEBUG: asl.ASL_STRING_DEBUG,
    logging.INFO: asl.ASL_STRING_INFO,
    logging.WARNING: asl.ASL_STRING_WARNING,
    logging.ERROR: asl.ASL_STRING_ERR,
    logging.CRITICAL: asl.ASL_STRING_CRIT,
    logging.FATAL: asl.ASL_STRING_ALERT,
}


def _logging2asl(lvl: int):
    try:
        return _LOGGING2ASL[lvl]
    except KeyError:
        r = asl.ASL_STRING_DEBUG
        for k in sorted(_LOGGING2ASL):
            if k < lvl:
                r = _LOGGING2ASL[k]
        return r


class ASLConsoleHandler(logging.Handler):
    def __init__(self, ident=None, level=asl.ASL_STRING_INFO):
        logging.Handler.__init__(self)
        self._asl = asl.aslclient(ident, level, 0)

    def emit(self, record):
        msg = asl.aslmsg(asl.ASL_TYPE_MSG)

        # Add all attributes of the logging record
        # to the ASL log message:
        for k in dir(record):
            if k in (
                "args",
                "levelno",
                "levelname",
                "msecs",
                "relativeCreated",
                "asctime",
                "created",
            ):
                continue
            if k.startswith("_"):
                continue

            # What about exc_info?

            msg["py." + k] = str(getattr(record, k))

        # Then set up the default attributes:
        msg[asl.ASL_KEY_FACILITY] = "com.apple.console"
        msg[asl.ASL_KEY_LEVEL] = _logging2asl(record.levelno)
        msg[asl.ASL_KEY_READ_UID] = str(os.getuid())
        msg[asl.ASL_KEY_MSG] = self.format(record)

        self._asl.send(msg)


logging.basicConfig(stream=sys.stderr, level=logging.DEBUG)
root = logging.getLogger()
print(root)
root.addHandler(ASLConsoleHandler())

root.warning("test me")
