import random
import socket
from src.autobfx.scripts.run import main as Run
from src.autobfx.scripts.server import check_server_status, start_server, stop_server
from src.autobfx.scripts.worker import start_worker


def get_random_free_port() -> int:
    while True:
        port = random.randint(
            10000, 65535
        )  # Choose a port from the ephemeral port range
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            try:
                s.bind(("localhost", port))  # Try to bind to the port
                return port  # If successful, return the port
            except OSError:
                pass  # If the port is in use, try another one


def test_clean_shotgun(dummy_project, test_runner):
    test_port = get_random_free_port()
    start_server(port=test_port, ui=False, wait=True)
    check_server_status(port=test_port)

    # Consider a way to modify config file to use test runner, dry runner is fine for now

    flow_run = Run([str(dummy_project.project_fp), "clean_shotgun:clean_shotgun_flow"])

    print(flow_run)
    print(flow_run.name)
    print(flow_run.flow_id)
    print(flow_run.state_id)
    print(flow_run.tags)

    stop_server(port=test_port, wait=True)

    assert False
