import os
import sys
import signal
import subprocess
import time
from daemon import DaemonContext, pidfile
from pathlib import Path


def start_daemon(
    command: list[str], pid_fp: Path, log_fp: Path, err_fp: Path, post_process: callable
):
    """
    Run a command as a daemon.
    """
    if pid_fp.exists():
        print(f"Daemon already running (PID file {pid_fp} exists).")
        sys.exit(1)

    def run():
        with open(log_fp, "w") as log, open(err_fp, "w") as err:
            process = subprocess.Popen(command, stdout=log, stderr=err)
            print(process.pid)
            post_process()

            while True:
                # Ensure the subprocess is alive
                if process.poll() is not None:
                    break
                time.sleep(1)

    with DaemonContext(pidfile=pidfile.PIDLockFile(pid_fp)):
        run()


def stop_daemon(pid_fp: Path) -> int:
    """
    Stop a running daemon.
    """
    if not pid_fp.exists():
        print(f"No daemon is running (PID file {pid_fp} does not exist).")
        return

    with open(pid_fp, "r") as f:
        pid = int(f.read().strip())

    try:
        os.kill(pid, signal.SIGTERM)
        print(f"Stopped daemon with PID {pid}.")
    except ProcessLookupError:
        print(f"No process found with PID {pid}.")

    pid_fp.unlink()
    return pid


def check_daemon(pid_fp: Path) -> int:
    """
    Check the status of a daemon.
    """
    if not pid_fp.exists():
        print(f"No daemon is running (PID file {pid_fp} does not exist).")
        return None

    with open(pid_fp, "r") as f:
        pid = int(f.read().strip())

    if Path(f"/proc/{pid}").exists():
        print(f"Daemon is running with PID {pid}.")
        return pid
    else:
        print(f"Daemon is not running. Removing stale PID file {pid_fp}.")
        pid_fp.unlink()
        return None
