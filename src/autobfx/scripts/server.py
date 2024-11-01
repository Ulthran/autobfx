import argparse
from prefect.server import Server


def main(argv):
    parser = argparse.ArgumentParser(description="Manage the Prefect server")
    subparsers = parser.add_subparsers(dest="command", help="Sub-command help")

    # Subparser for the start command
    parser_start = subparsers.add_parser("start", help="Start the server")

    # Subparser for the stop command
    parser_stop = subparsers.add_parser("stop", help="Stop the server")

    # Subparser for the check command
    parser_check = subparsers.add_parser("check", help="Check the server status")

    args = parser.parse_args(argv)

    server = Server()

    if args.command == "start":
        server.start()
    elif args.command == "stop":
        server.stop()
    elif args.command == "check":
        server.check_status()
