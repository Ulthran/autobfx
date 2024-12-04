import argparse
import requests
import os
import signal
import socket
import subprocess
import time
from autobfx.lib.daemon import start_daemon, stop_daemon, check_daemon
from autobfx.scripts import DOT_FP


LOCAL_HOST = "127.0.0.1"
DEFAULT_PORT = 4200
SERVER_PID_FP = DOT_FP / "server.pid"
SERVER_LOG_FP = DOT_FP / "server.log"
SERVER_ERR_FP = DOT_FP / "server.err"


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
        if pid := check_daemon(SERVER_PID_FP):
            # Check HTTP status of the Prefect server
            if ping_server(host, port):
                print(f"Prefect server is running at PID {pid} " f"with status: 200 OK")
            else:
                print(
                    f"Prefect server is running at PID {pid}, but HTTP status is unavailable."
                )
        else:
            print("Prefect server is not running.")
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
            f"Port {port} is already in use. This usually happens if you quickly stop and start the server. If this is the case, wait a few seconds and try again. You can use `lsof -i :{port}` to see what process is using the port."
        )
        return

    def post_process():
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

    start_daemon(
        [
            "prefect",
            "server",
            "start",
            "--port",
            str(port),
            "--ui" if ui else "--no-ui",
            # "--background",
        ],
        SERVER_PID_FP,
        SERVER_LOG_FP,
        SERVER_ERR_FP,
        post_process=post_process,
    )


def stop_server(host: str = LOCAL_HOST, port: int = DEFAULT_PORT, wait: bool = True):
    """Stop the Prefect server."""
    # TODO: Verify that user has shut down workers (or at least warn)

    # Stops the `autobfx server start` command that is daemonized
    daemon_pid = stop_daemon(SERVER_PID_FP)

    # Stops the `prefect server start` command (should also stop the uvicorn process that is the actual server)
    if daemon_pid:
        os.kill(daemon_pid + 1, signal.SIGTERM)

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
