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


Generic logging
...............

::

    $ python3 -m asl writelog {-k KEY VALUE}...

Write a log message to the ASL, with all message parameters under control
of the user.

The *IDENT* is the source identifier and is usually an application
name. It defaults to the name of the user.

The *FACILITY* is the log facility.

The *LEVEL* is the log level, and is one of "Emergency", "Alert",
"Critical", "Error", "Warning", "Notice", "Info" and "Debug" (from
high to low priority). The default is "Notice".

The "-k" option is used to set the attributes of the log message. You should
at least include a "Message" key with the text of the log message.

The standard keys are:

* *Time*: Time of logging (added by the ASL daemon)
* *TimeNanoSec* Nano-second resolution time (added by the ASL daemon)
* *Host*: Host where the message was written
* *Sender*: Sender of the log message
* *Facility*: Log facility

  This is either one of the regular
  syslog facilities (auth, authpriv, cron, ..., or an arbitrary string.
  Messages that should be shown in the default view of Console.app should use facility
  "com.apple.console".

* *PID*: Process ID of the sending proces (replaced by the ASL daemon)

* *UID*: UID of the sending process (replaced by the ASL daemon)

* *GID*: GUID of the sending proccess (replaced by the ASL daemon)

* *Level*: Log level (see the -l command of the *consolelog* command)

* *Message*: Text of the log message

* *ReadUID*: UID that may read the message, use "-1" for "all users"

* *ReadGID*: GID that may read the message, use "-1" for "all groups"

* *ASLExpireTime*: Expiry time for this message (default to 7 days after the log time)

* *ASLMessageID* Message ID for this message (replaced by the ASL daemon)

* *Session*: Session ID

* *RefPID* Reference PID for messages proxied by launchd

* *RefProc*: Reference process for messages proxied by launchd

* *ASLAuxTitle*: Auxiliary title string

* *ASLAuxUTI*: Auxiliary UTI

* *ASLAuxURL*: Auxiliary URL

* *ASLAuxData*: Auxiliary in-line data

* *SenderInstance*: Sender instance UUID

Query the ASL database
......................

::

   python3 -m asl query [-f FMT] [--format FMT] [-C] {-e KEY}... {-k KEY OP VALUE}...

Search the ASL database for matching records. All found records are printed on
stdout. By default all records are printed, and using the "-C", "-e" and "-k" options
a subset can be selected:

When mutiple "-C", "-e" and "-k" are present all of them must match (that is,
the subexpressions are combined with an "AND" operator).

* "-f FMT" or "--format FMT"

  Use FMT for formatting the records before printing them. The format string is
  a format string that can be using with :class:`str.format`, and it will be used
  in such a way that non-existing keys are ignored.

  When this option is not used all attributes of records are printed and records
  are separated by a single empty line.

* "-C"

  Add selection for messages destined for the Console.app. This is equivalent
  to "-k Facility eq com.apple.console"

* "-e KEY"

  Add a test that checks that attribute *KEY* exists.

* "-k KEY OP VALUE"

  Add a test for the value of attribute *KEY*.

  The following operators are recognized:

  * *eq*: The value must be equal to the specified value

  * *ne*: The value must not be equal to the specified value

  * *gt*: The value must be lexographically greater than the specified value

  * *ge*: The value must be lexographically greater than or equal to the specified value

  * *lt*: The value must be lexographically less than the specified value

  * *le*: The value must be lexographically less than or equal to the specified value

  * *match*: The value must match the specified regular expression (see regex(3))

  * *startswith*: The value must start with the specified value

  * *endswith*: The value must end with the specified value

  * *contains*: The value must contain the specified value

  * *==*: The value must be a number and must be equal to the specified value

  * *!=*: The value must be a number and must be different from the specified value

  * *>*: The value must be a number and must be greater than the specified value

  * *>=*: The value must be a number and must be greater than or equal to the specified value

  * *<*: The value must be a number and must be less than the specified value

  * *<=*: The value must be a number and must be less than or equal to the specified value

  The string operators can be prefix with "C" to perform case folding before the comparison.

  See the section on `Generic logging`_ for a description of the standard keys.
