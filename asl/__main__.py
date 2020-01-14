from __future__ import absolute_import, print_function

import argparse
import collections
import os
import sys

import asl

LEVELS = sorted(asl.STRING2LEVEL, key=lambda l: asl.STRING2LEVEL[l])

parser = argparse.ArgumentParser(
    description="ASL command-line interface", prog=__package__
)
parser.add_argument(
    "--version", action="version", version="%(prog)s " + asl.__version__
)

sub = parser.add_subparsers(help="Sub-commands")

parser_consolelog = sub.add_parser("consolelog", help="Log to Console.app")
parser_consolelog.set_defaults(action="consolelog")
parser_consolelog.add_argument(
    "-i",
    "--ident",
    action="store",
    metavar="IDENT",
    default=os.getlogin(),
    help="Source identifier (default: %(default)s)",
)
parser_consolelog.add_argument(
    "-l",
    "--level",
    action="store",
    metavar="LEVEL",
    default=asl.ASL_STRING_NOTICE,
    choices=LEVELS,
    help="Logging level (default: %(default)s, valid values: %(choices)s)",
)
parser_consolelog.add_argument(
    "message", help="The message", metavar="MESSAGE", nargs="+"
)

parser_sendlog = sub.add_parser("sendlog", help="Write log message")
parser_sendlog.set_defaults(action="sendlog")
parser_sendlog.add_argument(
    "-k",
    nargs=2,
    action="append",
    dest="keys",
    metavar=("KEY", "VALUE"),
    help="Add a key and value to the message",
)

parser_query = sub.add_parser("query", help="Perform ASL query")
parser_query.set_defaults(action="query")
parser_query.add_argument(
    "-f",
    "--format",
    action="store",
    dest="format",
    default=None,
    metavar="FMT",
    help="Format string for showing the record",
)
parser_query.add_argument(
    "-C",
    action="store_true",
    dest="show_console",
    help="include Console.app log entries",
)
parser_query.add_argument(
    "-k",
    action="append",
    dest="query",
    nargs=3,
    metavar=("KEY", "OP", "VALUE"),
    help="add query element",
)
parser_query.add_argument(
    "-e", action="append", dest="exists", metavar="KEY", help="query that key exists"
)


def do_consolelog(options):
    ident = options.ident
    message = " ".join(options.message)
    level = options.level

    cli = asl.aslclient(ident=ident, facility="com.apple.console", options=0)
    msg = asl.aslmsg(asl.ASL_TYPE_MSG)
    msg[asl.ASL_KEY_FACILITY] = "com.apple.console"
    msg[asl.ASL_KEY_LEVEL] = level
    msg[asl.ASL_KEY_READ_UID] = str(os.getuid())

    cli.log(msg, asl.STRING2LEVEL[level], message)


def do_sendlog(opts):
    if not opts.keys:
        print("No message arguments specified", file=sys.stderr)
        sys.exit(1)

    cli = asl.aslclient(ident=None, facility="user", options=0)
    msg = asl.aslmsg(asl.ASL_TYPE_MSG)
    for k, v in opts.keys:
        msg[k] = v

    cli.send(msg)


OP_MAP = {
    "eq": asl.ASL_QUERY_OP_EQUAL,
    "ne": asl.ASL_QUERY_OP_NOT_EQUAL,
    "gt": asl.ASL_QUERY_OP_GREATER,
    "ge": asl.ASL_QUERY_OP_GREATER_EQUAL,
    "le": asl.ASL_QUERY_OP_LESS_EQUAL,
    "lt": asl.ASL_QUERY_OP_LESS,
    "match": asl.ASL_QUERY_OP_REGEX,
    "Ceq": asl.ASL_QUERY_OP_EQUAL | asl.ASL_QUERY_OP_CASEFOLD,
    "Cne": asl.ASL_QUERY_OP_NOT_EQUAL | asl.ASL_QUERY_OP_CASEFOLD,
    "Cgt": asl.ASL_QUERY_OP_GREATER | asl.ASL_QUERY_OP_CASEFOLD,
    "Cge": asl.ASL_QUERY_OP_GREATER_EQUAL | asl.ASL_QUERY_OP_CASEFOLD,
    "Cle": asl.ASL_QUERY_OP_LESS_EQUAL | asl.ASL_QUERY_OP_CASEFOLD,
    "Clt": asl.ASL_QUERY_OP_LESS | asl.ASL_QUERY_OP_CASEFOLD,
    "Cmatch": asl.ASL_QUERY_OP_REGEX | asl.ASL_QUERY_OP_CASEFOLD,
    "==": asl.ASL_QUERY_OP_EQUAL | asl.ASL_QUERY_OP_NUMERIC,
    "!=": asl.ASL_QUERY_OP_NOT_EQUAL | asl.ASL_QUERY_OP_NUMERIC,
    ">": asl.ASL_QUERY_OP_GREATER | asl.ASL_QUERY_OP_NUMERIC,
    ">=": asl.ASL_QUERY_OP_GREATER_EQUAL | asl.ASL_QUERY_OP_NUMERIC,
    "<=": asl.ASL_QUERY_OP_LESS_EQUAL | asl.ASL_QUERY_OP_NUMERIC,
    "<": asl.ASL_QUERY_OP_LESS | asl.ASL_QUERY_OP_NUMERIC,
    "startswith": asl.ASL_QUERY_OP_EQUAL | asl.ASL_QUERY_OP_PREFIX,
    "endswith": asl.ASL_QUERY_OP_EQUAL | asl.ASL_QUERY_OP_SUFFIX,
    "contains": asl.ASL_QUERY_OP_EQUAL | asl.ASL_QUERY_OP_SUBSTRING,
    "Cstartswith": asl.ASL_QUERY_OP_EQUAL
    | asl.ASL_QUERY_OP_PREFIX
    | asl.ASL_QUERY_OP_CASEFOLD,
    "Cendswith": asl.ASL_QUERY_OP_EQUAL
    | asl.ASL_QUERY_OP_SUFFIX
    | asl.ASL_QUERY_OP_CASEFOLD,
    "Ccontains": asl.ASL_QUERY_OP_EQUAL
    | asl.ASL_QUERY_OP_SUBSTRING
    | asl.ASL_QUERY_OP_CASEFOLD,
}


def do_query(opts):
    cli = asl.aslclient(ident=None, facility="user", options=0)
    msg = asl.aslmsg(asl.ASL_TYPE_QUERY)
    if opts.show_console:
        msg.set_query(asl.ASL_KEY_FACILITY, "com.apple.console", asl.ASL_QUERY_OP_EQUAL)

    # Other search parameters
    if opts.query:
        valid = True
        for key, op, value in opts.query:
            try:
                msg.set_query(key, value, OP_MAP[op])

            except KeyError:
                valid = False
                print("Invalid query operation:", op, file=sys.stderr)

        if not valid:
            sys.exit(1)

    if opts.exists:
        for key in opts.exists:
            msg.set_query(key, "", asl.ASL_QUERY_OP_TRUE)

    for record in cli.search(msg):
        if opts.format is None:
            for key in sorted(record.keys()):
                print("{} {}".format(key, record[key]))
            print()

        else:
            fmt_arg: collections.defaultdict = collections.defaultdict(str)
            fmt_arg.update({k: record[k] for k in record.keys()})

            print(opts.format.format_map(fmt_arg))


def main():
    opts = parser.parse_args()
    if opts.action == "consolelog":
        do_consolelog(opts)

    elif opts.action == "sendlog":
        do_sendlog(opts)

    elif opts.action == "query":
        do_query(opts)

    else:
        raise NotImplementedError("Action: %s" % (opts.action,))


if __name__ == "__main__":
    main()
