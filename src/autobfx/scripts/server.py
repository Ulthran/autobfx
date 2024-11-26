import argparse
import requests
import socket
import subprocess
import time


LOCAL_HOST = "127.0.0.1"
DEFAULT_PORT = 4200


def ping_server(host: str = LOCAL_HOST, port: int = DEFAULT_PORT) -> bool:
    """Ping the Prefect server."""
    try:
        response = requests.get(f"http://{host}:{port}/api/ready", timeout=2)
        return response.status_code == 200
    except requests.exceptions.RequestException:
        return False


def check_port(host: str = LOCAL_HOST, port: int = DEFAULT_PORT) -> bool:
    """Check if the port is available. The Prefect server will often be slower to release the port than to shutdown the server process itself."""
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.bind((host, port))
    except OSError:
        return False
    return True


def check_server_status(host: str = LOCAL_HOST, port: int = DEFAULT_PORT):
    """Check if the Prefect server is running and its HTTP status."""
    try:
        # Use pgrep to find the PID of the Prefect server
        result = subprocess.run(
            ["pgrep", "-f", "prefect.server.api.server:create_app"],
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
    host: str = LOCAL_HOST, port: int = DEFAULT_PORT, ui: bool = True, wait: bool = True
):
    """Start the Prefect server."""
    # Check that the server isn't already running
    if ping_server(host, port):
        print("Prefect server is already running.")
        return
    if not check_port(host, port):
        print(
            f"Port {port} is already in use. This usually happens if quickly stop and start the server. If this is the case, wait a few seconds and try again. You can use `lsof -i :{port}` to see what process is using the port."
        )
        return

    with (
        open("autobfx_server_output.err", "w") as err_file,
        open("autobfx_server_output.log", "w") as log_file,
    ):
        subprocess.Popen(
            [
                "nohup",
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
        )

    if wait:
        max_wait_time = 10
        start_wait_time = time.time()
        started = ping_server(host, port)
        while not started:
            started = ping_server(host, port)
            if time.time() - start_wait_time > max_wait_time:
                print(f"Server did not start within {max_wait_time} seconds.")
                return

    print("Prefect server started.")


def stop_server(host: str = LOCAL_HOST, port: int = DEFAULT_PORT, wait: bool = True):
    """Stop the Prefect server."""
    # Verify that user has shut down workers

    try:
        result = subprocess.run(
            ["prefect", "server", "stop"],
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
                            f"Attempted to kill server but it appears to still be running."
                        )
                        return

            print(f"Stopped prefect server.")
        else:
            print(f"Prefect server failed to stop.")
    except Exception as e:
        print(f"Error stopping server: {e}")


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
