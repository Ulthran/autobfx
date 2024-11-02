import argparse
import sys
from . import __version__
from .init import main as Init
from .run import main as Run


def main():
    usage_str = "%(prog)s [-h/--help,-v/--version] <subcommand>"
    description_str = (
        "subcommands:\n"
        "  init         \tInitialize a new project.\n"
        "  run          \tExecute the pipeline.\n"
    )

    parser = argparse.ArgumentParser(
        prog="autobfx",
        usage=usage_str,
        description=description_str,
        epilog="For more help, see the docs at TODO.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        add_help=False,
    )

    parser.add_argument("command", help=argparse.SUPPRESS, nargs="?")
    parser.add_argument(
        "-v",
        "--version",
        action="version",
        version=__version__,
    )

    args, remaining = parser.parse_known_args()

    if args.command == "run":
        Run(remaining)
    elif args.command == "init":
        Init(remaining)
    else:
        parser.print_help()
        sys.stderr.write("Unrecognized command.\n")
