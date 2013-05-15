import argparse

import asl
import os


parser = argparse.ArgumentParser(description="ASL command-line interface", prog=__package__)
parser.add_argument('--version', action='version', version='%(prog)s ' + asl.__version__)

sub = parser.add_subparsers(help="Sub-commands")

parser_consolelog = sub.add_parser('consolelog', help='Log to Console.app')
parser_consolelog.set_defaults(action='consolelog')
parser_consolelog.add_argument(
    '-i', '--ident',
    action='store', metavar='IDENT',
    default=os.getlogin(), help='Source identifier (default: %(default)s)'
)
parser_consolelog.add_argument(
    '-l', '--level',
    action='store', metavar='LEVEL',
    default=asl.ASL_STRING_NOTICE, choices=list(asl.STRING2LEVEL.keys()),
    help='Logging level (default: %(default)s)'
)
parser_consolelog.add_argument('message', help='The message', metavar='MESSAGE', nargs='+')


def do_consolelog(options):
    ident = options.ident
    message = ' '.join(options.message)
    level = options.level

    cli = asl.aslclient(ident=ident, facility='com.apple.console', options=0)
    msg = asl.aslmsg(asl.ASL_TYPE_MSG)
    msg[asl.ASL_KEY_FACILITY] = "com.apple.console"
    msg[asl.ASL_KEY_LEVEL] = level
    msg[asl.ASL_KEY_READ_UID] = str(os.getuid())

    cli.log(msg, asl.STRING2LEVEL[level], message)

def main():
    opts = parser.parse_args()
    if opts.action == 'consolelog':
        do_consolelog(opts)

if __name__ == "__main__":
    main()
