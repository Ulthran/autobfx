import argparse
import requests
import subprocess
import time


LOCAL_HOST = "127.0.0.1"


def ping_server(host: str = LOCAL_HOST, port: int = 4200) -> bool:
    """Ping the Prefect server."""
    try:
        response = requests.head(f"http://{host}:{port}/api", timeout=2)
        return response.status_code == 200
    except requests.exceptions.RequestException:
        return False


def check_server_status(host: str = LOCAL_HOST, port: int = 4200):
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
            if ping_server(host, port):
                print(
                    f"Prefect server is running at PID {server_pid} "
                    f"with status: 200 OK"
                )
            else:
                print(
                    f"Prefect server is running at PID {server_pid}, but HTTP status is unavailable."
                )
    except Exception as e:
        print(f"Error checking server status: {e}")


def start_server(
    host: str = LOCAL_HOST, port: int = 4200, ui: bool = True, wait: bool = True
):
    """Start the Prefect server."""
    # Check that the server isn't already running
    if ping_server(host, port):
        print("Prefect server is already running.")
        return

    with (
        open("autobfx_server_output.err", "w") as err_file,
        open("autobfx_server_output.log", "w") as log_file,
    ):
        subprocess.Popen(
            [
                "prefect",
                "server",
                "start",
                "--port",
                str(port),
                "--ui" if ui else "--no-ui",
                "--background",
            ],
            stdout=log_file,
            stderr=err_file,
            start_new_session=True,
        )

    if wait:
        max_wait_time = 10
        start_wait_time = time.time()
        started = ping_server(host, port)
        while started:
            started = ping_server(host, port)
            if time.time() - start_wait_time > max_wait_time:
                print(f"Server did not start within {max_wait_time} seconds\n")
                return

    print("Prefect server started.\n")


def stop_server(host: str = LOCAL_HOST, port: int = 4200, wait: bool = True):
    """Stop the Prefect server."""
    try:
        result = subprocess.run(
            ["pkill", "-f", f"prefect server start --port {port}"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )
        if result.returncode == 0:
            if wait:
                max_wait_time = 10
                start_wait_time = time.time()
                running = ping_server(host, port)
                while running:
                    running = ping_server(host, port)
                    if time.time() - start_wait_time > max_wait_time:
                        print(
                            f"Attempted to kill server but it appears to still be running\n"
                        )
                        return

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
