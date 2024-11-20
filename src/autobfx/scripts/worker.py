import argparse
import subprocess
import sys


def start_worker(name: str, work_pool: str):
    """Start a Prefect worker."""
    subprocess.Popen(
        [
            "prefect",
            "worker",
            "start",
            "-n",
            f'"{name}"',
            "-p",
            f'"{work_pool}"',
            "2>",
            "autobfx_worker_output.err",
            ">",
            "autobfx_worker_output.log",
        ],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        start_new_session=True,
    )
    print("Prefect server started.\n")


def stop_worker(name: str, work_pool: str):
    pass


def main(argv):
    parser = argparse.ArgumentParser(description="Manage Prefect workers.")
    subparsers = parser.add_subparsers(title="Commands", dest="command")
    parser.add_argument(
        "--name",
        type=str,
        help="Name of the worker.",
    )
    parser.add_argument(
        "--work_pool",
        type=str,
        help="Name of the work pool.",
    )

    # Start command
    start_parser = subparsers.add_parser("start", help="Start a Prefect worker.")

    # Stop command
    stop_parser = subparsers.add_parser("stop", help="Stop a Prefect worker.")

    # Status command
    subparsers.add_parser(
        "status", help="Check on running Prefect workers in the dashboard."
    )

    args = parser.parse_args(argv)

    if args.command == "start":
        start_worker(args.name, args.work_pool)
    elif args.command == "stop":
        stop_worker(args.name, args.work_pool)
    elif args.command == "status":
        print(
            f"View dashboard at: http://127.0.0.1:4200/work-pools/work-pool/{args.work_pool}?tab=Workers"
        )
    else:
        parser.print_help()
        sys.stderr.write("Unrecognized command.\n")
