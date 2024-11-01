import argparse
from prefect.worker import Worker


def main(argv):
    parser = argparse.ArgumentParser(description="Manage Prefect workers")
    parser.add_argument("work_pool", type=str, help="Name of the work pool")
    parser.add_argument(
        "--worker_name", type=str, help="Name of the worker", default="default"
    )
    subparsers = parser.add_subparsers(dest="command", help="Sub-command help")

    # Subparser for the start command
    parser_start = subparsers.add_parser("start", help="Start a worker")

    # Subparser for the stop command
    parser_stop = subparsers.add_parser("stop", help="Stop a worker")

    # Subparser for the check command
    parser_check = subparsers.add_parser("check", help="Check a worker's status")

    args = parser.parse_args(argv)

    # Create a worker for a specific work pool
    worker = Worker(
        work_pool_name=args.work_pool,
        work_queue_name="default",
        worker_name=args.worker_name,
    )

    if args.command == "start":
        worker.run()
    elif args.command == "stop":
        worker.stop()
    elif args.command == "check":
        worker.check_status()
