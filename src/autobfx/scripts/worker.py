import argparse
import requests
import subprocess
import sys
from autobfx.lib.daemon import check_daemon, start_daemon, stop_daemon
from autobfx.scripts import DOT_FP
from autobfx.scripts.server import LOCAL_HOST


WORKER_PID_FP = lambda name, work_pool: DOT_FP / f"worker_{work_pool}_{name}.pid"
SERVER_LOG_FP = lambda name, work_pool: DOT_FP / f"worker_{work_pool}_{name}_output.log"
SERVER_ERR_FP = lambda name, work_pool: DOT_FP / f"worker_{work_pool}_{name}_output.err"


def start_worker(name: str, work_pool: str, worker_type: str):
    """Start a Prefect worker."""
    start_daemon(
        [
            "prefect",
            "worker",
            "start",
            "--name",
            f"{name}",
            "--pool",
            f"{work_pool}",
            "--type",
            f"{worker_type}",
        ],
        WORKER_PID_FP(name, work_pool),
        SERVER_LOG_FP(name, work_pool),
        SERVER_ERR_FP(name, work_pool),
        lambda: print(f"Prefect worker {name} in pool {work_pool} started."),
    )


def stop_worker(name: str, work_pool: str):
    """Find the PID for a Prefect worker and stop it."""
    stop_daemon(WORKER_PID_FP(name, work_pool))
    print(f"Prefect worker {name} in pool {work_pool} stopped.")


def worker_status(work_pool: str, host: str = LOCAL_HOST, port: int = 4200) -> bool:
    """Check if there is a running worker for a pool."""
    url = f"http://{host}:{port}/api/work_pools/{work_pool}"
    headers = {"Content-Type": "application/json"}

    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        work_pool = response.json()
        if work_pool["status"] == "READY":
            print(f"At least one worker for pool {work_pool['name']} is running.")
            return True
        else:
            print(f"No workers for pool {work_pool['name']} are running.")
            return False
    else:
        print(f"Error: {response.status_code}, {response.text}")

    return False


def list_workers(host: str = LOCAL_HOST, port: int = 4200):
    """List all running Prefect workers and their PIDs."""
    url = f"http://{host}:{port}/api/work_pools/filter"
    headers = {"Content-Type": "application/json"}
    data = {
        "work_pools": {},  # Empty filter to get all work pools
        "limit": 100,  # Adjust this number based on how many work pools you want to retrieve
    }

    response = requests.post(url, json=data, headers=headers)

    if response.status_code == 200:
        work_pools = response.json()
        print("Work Pools:")
        for pool in work_pools:
            print(f"Name: {pool['name']}, Type: {pool['type']}, ID: {pool['id']}")

        print("\nWorkers:")
        for pool in work_pools:
            # Get workers for each work pool
            url = f"http://{host}:{port}/api/work_pools/{pool['name']}/workers/filter"
            data = {
                "workers": {},  # Empty filter to get all workers
                "limit": 100,  # Adjust this number based on how many workers you want to retrieve
            }
            response = requests.post(url, json=data, headers=headers)

            if response.status_code == 200:
                workers = response.json()
                for worker in workers:
                    print(
                        f"Name: {worker['name']}, Status: {worker['status']}, ID: {worker['id']}"
                    )
            else:
                print(f"Error: {response.status_code}, {response.text}")
    else:
        print(f"Error: {response.status_code}, {response.text}")

    print(
        f"\nFor an interactive view, see the dashboard at: http://{host}:{port}/work-pools/work-pool/default?tab=Workers"
    )


def main(argv):
    parser = argparse.ArgumentParser(description="Manage Prefect workers.")
    subparsers = parser.add_subparsers(title="Commands", dest="command")

    # Start command
    start_parser = subparsers.add_parser("start", help="Start a Prefect worker.")
    start_parser.add_argument(
        "--name",
        type=str,
        help="Name of the worker.",
    )
    start_parser.add_argument(
        "--work_pool",
        type=str,
        help="Name of the work pool.",
    )
    start_parser.add_argument(
        "--type", type=str, default="process", help="Type of worker (default: process)."
    )

    # Stop command
    stop_parser = subparsers.add_parser("stop", help="Stop a Prefect worker.")
    stop_parser.add_argument(
        "--name",
        type=str,
        help="Name of the worker.",
    )
    stop_parser.add_argument(
        "--work_pool",
        type=str,
        help="Name of the work pool.",
    )

    # Status command
    status_parser = subparsers.add_parser(
        "status", help="Check if there is a running worker for a pool."
    )
    status_parser.add_argument(
        "--work_pool",
        type=str,
        required=True,
        help="Name of the work pool.",
    )

    # List command
    subparsers.add_parser(
        "list", help="List all running Prefect workers and their PIDs."
    )

    args = parser.parse_args(argv)

    if args.command == "start":
        start_worker(args.name, args.work_pool, args.type)
    elif args.command == "stop":
        stop_worker(args.name, args.work_pool)
    elif args.command == "status":
        return worker_status(args.work_pool)
    elif args.command == "list":
        list_workers()
    else:
        parser.print_help()
        sys.stderr.write("Unrecognized command.")
