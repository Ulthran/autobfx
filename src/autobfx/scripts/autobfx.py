import argparse
import sys
from autobfx import __version__
from autobfx.scripts.ai import main as AI
from autobfx.scripts.init import main as Init
from autobfx.scripts.run import main as Run
from autobfx.scripts.server import main as Server
from autobfx.scripts.worker import main as Worker


def main():
    usage_str = "%(prog)s [-h/--help,-v/--version] <subcommand>"
    description_str = (
        "subcommands:\n"
        "  init         \tInitialize a new project.\n"
        "  run          \tExecute the pipeline.\n"
        "  server       \tManage Prefect server.\n"
        "  worker       \tManage Prefect workers.\n"
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
    parser.add_argument(
        "--list_flows", action="store_true", help="List available flows."
    )

    args, remaining = parser.parse_known_args()

    if args.list_flows:
        from autobfx.flows import flows

        print("Available flows:")
        for flow in flows:
            print(f"  {flow}")
        return

    if args.command == "run":
        Run(remaining)
    elif args.command == "init":
        Init(remaining)
    elif args.command == "server":
        Server(remaining)
    elif args.command == "worker":
        Worker(remaining)
    else:
        parser.print_help()
        sys.stderr.write("Unrecognized command.\n")
