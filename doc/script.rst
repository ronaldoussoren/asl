Module as a script
==================

The module can be used as a script::

  $ python3 -m asl --help

This is primarily intended as an example
on how to use the module, but can be usefull
on its own.

Usage
-----

Writing messages to the Console.app default view
................................................

::

  $ python3 -m asl consolelog [-i IDENT] [-l LEVEL] message ...

This logs the message arguments as a single line (separated
by spaces) with the attributes needed to end up in the default
view of Console.app.

The *IDENT* is the source identifier and is usually an application
name. It defaults to the name of the user.

The *LEVEL* is the log level, and is one of "Emergency", "Alert",
"Critical", "Error", "Warning", "Notice", "Info" and "Debug" (from
high to low priority). The default is "Notice", which is the lowest
priority that will end up in the default view of Console.app.


