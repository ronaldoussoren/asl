Examples
========

Basic logging
-------------

::

    cli = asl.aslclient("example", "user", 0)
    cli.log(None, asl.ASL_LEVEL_NOTICE, "hello world")


Logging with more control
-------------------------

::

    cli = asl.aslclient("example", "user", 0)
    msg = asl.aslmsg(asl.ASL_TYPE_MSG)
    msg[asl.ASL_KEY_FACILITY, "com.secrets.r.us");
    msg[asl.ASL_KEY_LEVEL] = asl.ASL_STRING_EMERG
    msg[asl.ASL_KEY_MSG] = "Breaking attempt!"

    cli.send(msg)

Sending log messages to the default view of Console.app
-------------------------------------------------------

::

    cli = asl.aslclient("example", "com.apple.console", 0)
    msg = asl.aslmsg(asl.ASL_TYPE_MSG)
    msg[asl.ASL_KEY_FACILITY] = "com.apple.console"
    msg[asl.ASL_KEY_LEVEL] = asl.ASL_STRING_NOTICE
    msg[asl.ASL_KEY_READ_UID] = str(os.getuid())

    cli.log(msg, asl.ASL_LEVEL_NOTICE, "hello console.app!")

Logging an auxiliary URL
------------------------

::

    cli = asl.aslclient("example", "com.apple.console", 0)
    msg = asl.aslmsg(asl.ASL_TYPE_MSG)
    msg[asl.ASL_KEY_FACILITY] = "com.apple.console"
    msg[asl.ASL_KEY_LEVEL] = asl.ASL_STRING_NOTICE
    msg[asl.ASL_KEY_READ_UID] = "-1"
    msg[asl.ASL_KEY_MSG] = "Python was here"

    asl.log_auxiliary_location(msg, "More information", None, "http://www.python.org/")


Querying the ASL database
-------------------------

::

    cli = asl.aslclient("example", "user", 0)
    msg = asl.aslmsg(asl.ASL_TYPE_QUERY)
    msg.set_query(asl.ASL_KEY_FACILITY, "com.apple.console", asl.ASL_QUERY_OP_EQUAL)

    for info in cli.search(msg):
        print info.asdict()


Integration with the logging package
------------------------------------

This example implements a :class:`logging.Handler` subclass that
forwards all messages to ASL while marking them for display
in Console.app's default view.

This class is not part of the API of the ASL package because it
is at this time not clear if the implementation is fully usable
in its current form.

::

    import logging
    import asl
    import sys
    import os

    # Translation from logging levels to ASL levels:

    _LOGGING2ASL = {
        logging.DEBUG: asl.ASL_STRING_DEBUG,
        logging.INFO: asl.ASL_STRING_INFO,
        logging.WARNING: asl.ASL_STRING_WARNING,
        logging.ERROR: asl.ASL_STRING_ERR,
        logging.CRITICAL: asl.ASL_STRING_CRIT,
        logging.FATAL: asl.ASL_STRING_ALERT,
    }
    def _logging2asl(lvl):
        try:
            return _LOGGING2ASL[lvl]
        except KeyError:
            r = asl.ASL_STRING_DEBUG
            for k in sorted(_LOGGING2ASL):
               if k < lvl:
                   r = _LOGGING2ASL[k]
            return r

    #
    # Define a logging handler:
    #

    class ASLConsoleHandler (logging.Handler):
        def __init__(self, ident=None, level=asl.ASL_STRING_INFO):
            logging.Handler.__init__(self)
            self._asl = asl.aslclient(ident, level, 0)

        def emit(self, record):
            msg = asl.aslmsg(asl.ASL_TYPE_MSG)

            # Add all attributes of the logging record
            # to the ASL log message:
            for k in dir(record):
                if k in ('args', 'levelno', 'levelname', 'msecs', 'relativeCreated', 'asctime', 'created'):
                   continue
                if k.startswith('_'):
                   continue

                # What about exc_info?

                msg["py." + k] = str(getattr(record, k))

            # Then set up the default attributes:
            msg[asl.ASL_KEY_FACILITY] = "com.apple.console"
            msg[asl.ASL_KEY_LEVEL] = _logging2asl(record.levelno)
            msg[asl.ASL_KEY_READ_UID] = str(os.getuid())
            msg[asl.ASL_KEY_MSG] = self.format(record)

            self._asl.send(msg)


    # Use the logger class:

    logging.basicConfig(stream=sys.stderr, level=logging.DEBUG)
    root = logging.getLogger()
    print root
    root.addHandler(ASLConsoleHandler())

    root.warning("test me")
