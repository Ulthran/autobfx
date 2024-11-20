import argparse
import subprocess
import requests


def check_server_status():
    """Check if the Prefect server is running and its HTTP status."""
    try:
        # Use pgrep to find the PID of the Prefect server
        result = subprocess.run(
            ["pgrep", "-f", "prefect server"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )
        server_pid = result.stdout.strip()

        if not server_pid:
            print("Prefect server is not running.")
        else:
            # Check HTTP status of the Prefect server
            try:
                response = requests.head("http://127.0.0.1:4200/api", timeout=2)
                print(
                    f"Prefect server is running at PID {server_pid} "
                    f"with status: {response.status_code} {response.reason}"
                )
            except requests.RequestException:
                print(
                    f"Prefect server is running at PID {server_pid}, but HTTP status is unavailable."
                )
    except Exception as e:
        print(f"Error checking server status: {e}")


def start_server():
    """Start the Prefect server."""
    subprocess.Popen(
        [
            "prefect",
            "server",
            "start",
            "2>",
            "autobfx_server_output.err",
            ">",
            "autobfx_server_output.log",
        ],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        start_new_session=True,
    )
    print("Prefect server started.\n")


def stop_server():
    """Stop the Prefect server."""
    try:
        result = subprocess.run(
            ["pkill", "-f", "prefect server"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )
        if result.returncode == 0:
            print(f"Stopped all processes matching 'prefect server'.\n")
        else:
            print(f"No processes found matching 'prefect server'.\n")
    except Exception as e:
        print(f"Error stopping processes: {e}")


def main(argv):
    parser = argparse.ArgumentParser(description="Manage Prefect server.")
    subparsers = parser.add_subparsers(title="Commands", dest="command")

    # Start command
    start_parser = subparsers.add_parser("start", help="Start the Prefect server.")

    # Stop command
    stop_parser = subparsers.add_parser("stop", help="Stop the Prefect server.")

    # Status command
    subparsers.add_parser("status", help="Check the status of the Prefect server.")

    args = parser.parse_args(argv)

    if args.command == "start":
        start_server()
    elif args.command == "stop":
        stop_server()
    elif args.command == "status":
        check_server_status()
    else:
        parser.print_help()
