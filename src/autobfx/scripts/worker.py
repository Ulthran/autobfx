import argparse
import requests
import subprocess
import sys
from autobfx.scripts.server import LOCAL_HOST


def start_worker(name: str, work_pool: str, worker_type: str):
    """Start a Prefect worker."""
    subprocess.Popen(
        [
            "nohup",
            "prefect",
            "worker",
            "start",
            "--name",
            f'"{name}"',
            "--pool",
            f'"{work_pool}"',
            "--type",
            f'"{worker_type}"',
            "2>",
            f"autobfx_worker_{name}_output.err",
            ">",
            f"autobfx_worker_{name}_output.log",
            "&",
        ],
    )
    print(f"Prefect worker {name} in pool {work_pool} started.\n")


def stop_worker(name: str, work_pool: str):
    """Find the PID for a Prefect worker and stop it."""
    result = subprocess.run(
        ["pgrep", "-f", f"prefect worker --name {name} --pool {work_pool}"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )
    if result.returncode == 0:
        pid = result.stdout.strip()
        subprocess.run(["kill", pid])
        print(f"Prefect worker {name} in pool {work_pool} stopped.\n")
    else:
        print(f"Prefect worker {name} in pool {work_pool} not found.\n")


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
        f"\nFor an interactive view, see the dashboard at: http://{host}:{port}/work-pools/work-pool/{work_pools[0]['name']}?tab=Workers"
    )


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
    start_parser.add_argument("--type", type=str, help="Type of worker.")

    # Stop command
    stop_parser = subparsers.add_parser("stop", help="Stop a Prefect worker.")

    # List command
    subparsers.add_parser(
        "list", help="List all running Prefect workers and their PIDs."
    )

    args = parser.parse_args(argv)

    if args.command == "start":
        start_worker(args.name, args.work_pool, args.type)
    elif args.command == "stop":
        stop_worker(args.name, args.work_pool)
    elif args.command == "list":
        list_workers()
    else:
        parser.print_help()
        sys.stderr.write("Unrecognized command.\n")
