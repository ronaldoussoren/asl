:mod:`asl` --- ASL library
==========================

.. module:: asl
   :synopsis: ASL library bindings

The Apple System Log facility is a logging API with a simular
goal to the classic unix syslog API, but with a richer interface
and with an API for querying the logging system.

See Apple's manual page for the C API for more information on how
to use this module.

.. note::

   All APIs accept unicode strings, and require them for Python 3.

   The strings will be converted to the C strings expected by the
   C API using the UTF-8 encoding.

.. note::

   Functions and methods raise :exc:`OSError` when the C API
   fails.


ASL connection
--------------

.. class:: aslclient(ident, facility, options)

   :param ident:    Name of the sender
   :param facility: A facility name
   :param optons:   Option flags, see `Open options`_

   Connection to the ASL backend. These objects implement
   the context protocol and can be used with the "with"
   statement.

   .. method:: add_log_file(fd)

      :param fd: A file descriptor

      Log messages will be written to the file descriptor as well
      as to the logging subsystem.

   .. method:: remove_log_file(fd)

      :param fd: A file descriptor

      No longer write log messages to the file descriptor. The
      file descriptor should be one that's added earlier with
      :meth:`add_log_file`.

   .. method:: set_filter(filter)

      :param filter: an integer with the levels that should be sent to the server

      *filter* is an bitwise or of values from `Message priority levels`_,
      and only messages whose log level is set in *filter* will be
      sent to the logging subsystem.

      Returns the previous value of the filter.

   .. method:: log(msg, level, text)

      :param msg: an :class:`aslmsg` object or :data:`None`

      :param level: a lot level from `Message priority levels`_

      :param text: a message string for the log message

      .. note::

         The C API uses a printf-style format string instead of
         a message. In Python you can use string formatting to
         format the string.

   .. method:: send(msg)

      :param msg: an :class:`aslmsg` object

      Send a log message to the logging subsystem.

   .. method:: search(msg)

      :param msg: an :class:`aslmsg` object
      :returns: an iterator that yields the result messages.

      Send a query message to the logging subsystem.

   .. method:: log_descriptor(msg, level, fd, fd_type)

      :param msg: an :class:`aslmsg` object or :data:`None`
      :param level: a log level from `Message priority levels`_
      :param fd: a file descriptor
      :param fd_type: type of file descriptor, from `File descriptor types`_

      If *fd_type* is :data:`ASL_LOG_DESCRIPTOR_READ` ASL will read lines
      from the file descriptor and forward those lines to the logging
      subsystem as log messages.

      If *fd_type* is :data:`ASL_LOG_DESCRIPTOR_WRITE` the file descriptor
      is closed and reopened as a pipe where the application can write
      lines that will be converted to log messages.

      The *msg* is a template for the log messages created by this API.

      This method is available on OSX 10.8 or later.


   .. method:: close()

      Explicitly close the client.

      .. note::

         The connection will also de closed when the
         object is garbage collected.


.. function::  asl_open(ident, facility, options)

   :param ident: A program identifier string, or :data:`None`.
   :param facility: A facility name
   :param options: Option flags, see `Open options`_

   This is an alias for :class:`asclient`.

.. function:: open_from_file(fd, ident, facility)

   :param fd: A file descriptor, open for writing and reading
   :param ident: A program identifier string, or :data:`None`.
   :param facility: A facility name

   Opens an ASL log file for writing using an existing
   file descriptor, for example one returned by
   :func:`create_auxiliary_file`. The file descriptor
   must be open for reading and writing.

   Avaliable on Mac OS X 10.7 or later.



ASL messages
------------

.. class:: aslmsg(type)

   .. method:: __getitem__(key)

      :param key: An attribute name

      Return the attribute value for *key*. The key is a unicode string.

      See `Standard message attributes`_ for a list of standard attributes.


   .. method:: __setitem__(key, value)

      :param key: An attribute name
      :param value: Value for the attribute, must be a string

      Set the value for attribute *key* to *value*. Both arguments
      are unicode strings.

      See `Standard message attributes`_ for a list of standard attributes.

   .. method:: __delitem__(key)

      :param key: An attribute name

      Remove an attribute from the message.

   .. method:: set_query(key, value, operation)

      :param key: An attribute name
      :param value: Value to compare the attribute name with
      :param operation: The comparison method

      Add a query element to the message. The operation is ... .

      A second call to :meth:`set_query` for the same *key* will
      replace that query. Calls to :meth:`set_query` for different
      values of *key* are combined into an AND query (that is, all
      query elements must match).

      .. note::

         It is not possible to perform OR queries, to do those you'll
         have to fetch and merge the various subsets yourself.

      .. note::

         For basic equality tests (:data:`ASL_QUERY_OP_EQUAL`) you can
         also set the *key* and *value* using the mapping interface. That
         is,

         ::

             m[key] = value

         is equivalent to::

             m.set_query(key, value, ASL_QUERY_OP_EQUAL)


   .. method:: keys()

      Returns the set of attribute names for this message.

   .. method:: asdict()

      Return a dict with all attributes of this message. Equivalent to::

         { k: msg[k] for k in msg.keys() }

      .. note::

         It is not possible to retrieve the "operation" for query
         messages, the C API doesn't provide this information.


Utility functions
-----------------


.. function:: ASL_FILTER_MASK(level)

   :param level: A message priority level

   Converts one of the values from `Message priority levels` into
   a bit mask that can be used with :meth:`aslclient.set_filter`.


.. function:: ASL_FILTER_MASK_UPTO(level)

   :param level: A message priority level

   Returns a mask where all bits from :data:`ASL_LEVEL_DEBUG`
   upto *level* are set.


.. function:: create_auxiliary_file(msg, title, uti)

   :param msg: An :class:`aslmsg` object
   :param title: Title for the auxiliary file (for display in Console.app)
   :param uti: UTI for the file format, or :data:`None`

   Creates an auxiliary file that may be used to store arbitrary
   data associated with the mssage. Returns a file descriptor
   for the file. This file descriptor must be closed with
   :func:`close_auxiliary_file`.

   When *uti* is :data:`None` the system will use "public.data"
   instead.

   The Console.app application will show auxiliary file as an file
   icon that can be opened.

   This function is available on Mac OS X 10.7 or later.


.. function:: log_auxiliary_location(msg, title, uti, url)

   :param msg: An :class:`aslmsg` object
   :param title: Title for the auxiliary file (for display in Console.app)
   :param uti: UTI for the file format of the URL contents, or :data:`None`
   :param url: String representation of an URL

   Write a log message to the logging system with a URL in the message.

   When *uti* is :data:`None` the system will use "public.data"
   instead.

   The Console.app application will show the URL as a clickable link.

   This method is available on Mac OS X 10.7 or later.


.. function:: close_auxiliary_file(fd)

   :param fd: File descriptor returned by :func:`create_auxiliary_file`.

   Close the file descriptor for an auxiliary file that was created
   earlier with :meth:`aslmsg.create_auxiliary_file`. A side effect
   of this is that the message is logged with the logging system.

.. function:: asl_new(type)

   This is an alias for :class:`aslmsg`



Constants
---------


Message priority levels
.......................

.. data:: ASL_LEVEL_EMERG

.. data::  ASL_LEVEL_ALERT

.. data::  ASL_LEVEL_CRIT

.. data::  ASL_LEVEL_ERR

.. data::  ASL_LEVEL_WARNING

.. data::  ASL_LEVEL_NOTICE

.. data::  ASL_LEVEL_INFO

.. data::  ASL_LEVEL_DEBUG


Message priority level strings
..............................

These are the string representation of the constants in
the `previous section <Message priority levels>`_, and are
used as the value for the :data:`ASL_KEY_LEVEL` key in
:class:`aslmsg` objects.

.. data::  ASL_STRING_EMERG

.. data::  ASL_STRING_ALERT

.. data::  ASL_STRING_CRIT

.. data::  ASL_STRING_ERR

.. data::  ASL_STRING_WARNING

.. data::  ASL_STRING_NOTICE

.. data::  ASL_STRING_INFO

.. data::  ASL_STRING_DEBUG


Priority translations
.....................

.. data:: LEVEL2STRING

   A directionary mapping numeric levels to the equivalent string value

.. data:: STRING2LEVEL

   A directionary mapping string levels to the equivalent integer value


Attribute matching operations
.............................


Modifiers
~~~~~~~~~

.. data::  ASL_QUERY_OP_CASEFOLD

.. data::  ASL_QUERY_OP_PREFIX

.. data::  ASL_QUERY_OP_SUFFIX

.. data::  ASL_QUERY_OP_SUBSTRING

.. data::  ASL_QUERY_OP_NUMERIC

.. data::  ASL_QUERY_OP_REGEX


Operators
~~~~~~~~~

.. data::  ASL_QUERY_OP_EQUAL

.. data::  ASL_QUERY_OP_GREATER

.. data::  ASL_QUERY_OP_GREATER_EQUAL

.. data::  ASL_QUERY_OP_LESS

.. data::  ASL_QUERY_OP_LESS_EQUAL

.. data::  ASL_QUERY_OP_NOT_EQUAL

.. data::  ASL_QUERY_OP_TRUE


Standard message attributes
...........................

These are the names of well-known attributes of ASL messages,
you can add other attributes as well but those won't be used
by the ASL backend.

.. data:: ASL_KEY_TIME

   Timestamp.  Set automatically

.. data:: ASL_KEY_TIME_NSEC

   Nanosecond time.

.. data:: ASL_KEY_HOST

   Sender's address (set by the server).

.. data:: ASL_KEY_SENDER

   Sender's identification string.  Default is process name.

.. data:: ASL_KEY_FACILITY

   Sender's facility.  Default is "user".

.. data:: ASL_KEY_PID

   Sending process ID encoded as a string.  Set automatically.

.. data:: ASL_KEY_UID

   UID that sent the log message (set by the server).

.. data:: ASL_KEY_GID

   GID that sent the log message (set by the server).

.. data:: ASL_KEY_LEVEL

   Log level number encoded as a string.  See levels above.

.. data:: ASL_KEY_MSG

   Message text.

.. data:: ASL_KEY_READ_UID

   User read access (-1 is any user).

.. data:: ASL_KEY_READ_GID

   Group read access (-1 is any group).

.. data:: ASL_KEY_EXPIRE_TIME

   Expiration time for messages with long TTL.

.. data:: ASL_KEY_MSG_ID

   64-bit message ID number (set by the server).

.. data:: ASL_KEY_SESSION

   Session (set by the launchd).

.. data:: ASL_KEY_REF_PID

   Reference PID for messages proxied by launchd

.. data:: ASL_KEY_REF_PROC

   Reference process for messages proxied by launchd

.. data:: ASL_KEY_AUX_TITLE

   Auxiliary title string

.. data:: ASL_KEY_AUX_UTI

   Auxiliary Uniform Type ID

.. data:: ASL_KEY_AUX_URL

   Auxiliary Uniform Resource Locator

.. data:: ASL_KEY_AUX_DATA

   Auxiliary in-line data

.. data:: ASL_KEY_OPTION

   Internal

.. data:: ASL_KEY_SENDER_INSTANCE

   Sender instance UUID.


Message types
.............

.. data:: ASL_TYPE_MSG

   A regular log message.

.. data:: ASL_TYPE_QUERY

   A query message.


Filter masks
............

These are used for client-side filtering.

.. data::  ASL_FILTER_MASK_EMERG

.. data::  ASL_FILTER_MASK_ALERT

.. data::  ASL_FILTER_MASK_CRIT

.. data::  ASL_FILTER_MASK_ERR

.. data::  ASL_FILTER_MASK_WARNING

.. data::  ASL_FILTER_MASK_NOTICE

.. data::  ASL_FILTER_MASK_INFO

.. data::  ASL_FILTER_MASK_DEBUG


Open options
............

.. data::  ASL_OPT_STDERR

   Write a copy of log lines to the stderr stream.

.. data::  ASL_OPT_NO_DELAY

   Immediately create a connection to the logging subsystem,
   instead of waiting for the first log message.

.. data::  ASL_OPT_NO_REMOTE

   Ignore the server side log filter for messages send
   using this connection. Using this option requires
   root privileges.


File descriptor types
.....................

.. data:: ASL_LOG_DESCRIPTOR_READ

   File descriptor is readable, ASL will read log lines from it.

.. data:: ASL_LOG_DESCRIPTOR_WRITE

   File descriptor is writable. ASL will convert the file descriptor
   to another writable descriptor where the application can write
   lines that will be converted to log messages.
