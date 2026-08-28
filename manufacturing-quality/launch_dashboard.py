from __future__ import annotations

import socket
import subprocess
import sys
import time
import webbrowser
from pathlib import Path

PORT = 8501
HOST = "127.0.0.1"
URL = f"http://{HOST}:{PORT}"


def _print_header() -> None:
    print()
    print("PPAP Level 3 Streamlit Dashboard")
    print("================================")
    print(f"Python: {sys.executable}")
    print(f"Version: {sys.version.split()[0]}")
    print()


def _check_dependencies() -> bool:
    missing: list[str] = []
    try:
        import streamlit  # noqa: F401
    except ImportError:
        missing.append("streamlit")
    try:
        import pypdf  # noqa: F401
    except ImportError:
        missing.append("pypdf")

    if not missing:
        import streamlit

        print(f"OK  streamlit {streamlit.__version__}")
        print("OK  pypdf")
        return True

    print("ERROR: Missing packages:", ", ".join(missing))
    print()
    print("Run this command:")
    print(f'  "{sys.executable}" -m pip install --user streamlit pypdf')
    return False


def _check_app_import(root: Path) -> bool:
    if str(root) not in sys.path:
        sys.path.insert(0, str(root))
    try:
        from ppap_inbox_triage.triage import triage_inbox  # noqa: F401
    except Exception as error:
        print(f"ERROR: Cannot import PPAP modules: {error}")
        return False
    print("OK  ppap_inbox_triage")
    return True


def _port_is_open(port: int) -> bool:
    try:
        with socket.create_connection((HOST, port), timeout=1):
            return True
    except OSError:
        return False


def _wait_for_server(port: int, timeout_seconds: int = 90) -> bool:
    print(f"Waiting for server at {URL} ...")
    deadline = time.time() + timeout_seconds
    while time.time() < deadline:
        if _port_is_open(port):
            return True
        time.sleep(0.5)
    return False


def main() -> int:
    root = Path(__file__).resolve().parent
    app_path = root / "dashboard" / "app.py"

    _print_header()

    if not app_path.exists():
        print(f"ERROR: Dashboard app not found: {app_path}")
        return 1

    if not _check_dependencies():
        return 1
    if not _check_app_import(root):
        return 1

    print()
    print("Starting Streamlit server...")
    print("Keep this window open while using the dashboard.")
    print()

    command = [
        sys.executable,
        "-m",
        "streamlit",
        "run",
        str(app_path),
        "--server.port",
        str(PORT),
        "--server.address",
        HOST,
        "--server.headless",
        "true",
        "--browser.gatherUsageStats",
        "false",
    ]

    process = subprocess.Popen(command, cwd=str(root))

    if _wait_for_server(PORT):
        print()
        print(f"Server ready. Opening browser: {URL}")
        webbrowser.open(URL)
        print("If the browser did not open, copy this URL into Chrome:")
        print(f"  {URL}")
        print()
    else:
        print("ERROR: Streamlit did not start within 90 seconds.")
        process.terminate()
        return 1

    exit_code = process.wait()
    if exit_code != 0:
        print(f"ERROR: Streamlit exited with code {exit_code}")
        return exit_code

    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except KeyboardInterrupt:
        print("\nDashboard stopped.")
        raise SystemExit(0)
