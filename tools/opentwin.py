"""PRW-Wild Digital Twin — Shortest Terminal & Quick Launcher CLI.

Provides the shortest, ultra-compact terminal view of the PRW-Wild Digital Twin,
verifies background server health, and opens the web application in the default browser.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import sys
import time
import urllib.error
import urllib.request
import webbrowser
from pathlib import Path

DEFAULT_PORT = 8000
DEFAULT_URL = f"http://127.0.0.1:{DEFAULT_PORT}/"
PROJECT_ROOT = Path(__file__).resolve().parent.parent

# ANSI Colors for Windows Terminal & PowerShell
C_CYAN = "\033[96m"
C_GREEN = "\033[92m"
C_YELLOW = "\033[93m"
C_RED = "\033[91m"
C_MAGENTA = "\033[95m"
C_BLUE = "\033[94m"
C_DIM = "\033[90m"
C_BOLD = "\033[1m"
C_RESET = "\033[0m"


def enable_windows_ansi() -> None:
    """Enable VT100 / ANSI escape processing on Windows console."""
    if os.name == "nt":
        try:
            import ctypes
            kernel32 = ctypes.windll.kernel32
            handle = kernel32.GetStdHandle(-11)  # STD_OUTPUT_HANDLE = -11
            mode = ctypes.c_ulong()
            if kernel32.GetConsoleMode(handle, ctypes.byref(mode)):
                # ENABLE_VIRTUAL_TERMINAL_PROCESSING = 0x0004
                kernel32.SetConsoleMode(handle, mode.value | 0x0004)
        except Exception:
            pass


def strip_ansi(text: str) -> str:
    """Remove ANSI escape sequences for accurate visual length calculation."""
    return re.sub(r"\033\[[0-9;]*m", "", text)


def format_row(content: str, width: int = 70) -> str:
    """Format a single content row with precise padding and vertical borders."""
    vis_len = len(strip_ansi(content))
    pad = max(0, width - vis_len)
    return f"{C_BOLD}{C_CYAN}│{C_RESET} {content}{' ' * pad} {C_BOLD}{C_CYAN}│{C_RESET}"


def check_server(url: str, timeout: float = 1.0) -> bool:
    """Check if the Digital Twin server is responding."""
    try:
        api_url = f"{url.rstrip('/')}/api/status"
        req = urllib.request.Request(api_url, headers={"User-Agent": "OpenTwin-CLI"})
        with urllib.request.urlopen(req, timeout=timeout) as response:
            if response.status == 200:
                data = json.loads(response.read().decode("utf-8"))
                return data.get("status") == "online"
    except Exception:
        return False
    return False


def start_server_in_background(port: int = DEFAULT_PORT) -> bool:
    """Start the web server in the background if not already running."""
    pkg_src = PROJECT_ROOT / "src"
    env = os.environ.copy()
    env["PYTHONPATH"] = str(pkg_src)

    # Detached creation flags for Windows
    creation_flags = 0
    if os.name == "nt":
        DETACHED_PROCESS = 0x00000008
        CREATE_NEW_PROCESS_GROUP = 0x00000200
        creation_flags = DETACHED_PROCESS | CREATE_NEW_PROCESS_GROUP

    cmd = [sys.executable, "-m", "prw_wild.web", "--port", str(port)]
    try:
        subprocess.Popen(
            cmd,
            cwd=str(PROJECT_ROOT),
            env=env,
            creationflags=creation_flags,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            close_fds=True,
        )
    except Exception as e:
        print(f"{C_RED}[ERROR] Failed to start server: {e}{C_RESET}")
        return False

    # Wait for server to come online
    target_url = f"http://127.0.0.1:{port}/"
    for _ in range(30):
        time.sleep(0.15)
        if check_server(target_url, timeout=0.5):
            return True
    return False


def fetch_telemetry(url: str) -> dict:
    """Fetch real-time hardware telemetry and state from the web server."""
    api_url = f"{url.rstrip('/')}/api/hardware/telemetry"
    try:
        req = urllib.request.Request(api_url, headers={"User-Agent": "OpenTwin-CLI"})
        with urllib.request.urlopen(req, timeout=1.5) as response:
            return json.loads(response.read().decode("utf-8"))
    except Exception:
        return {}


def render_shortest_view(url: str, clear: bool = False, width: int = 70) -> None:
    """Render the ultra-compact, shortest version of the Digital Twin in the terminal."""
    data = fetch_telemetry(url)
    latest = data.get("latest") or {}
    status = data.get("status") or {}
    nodes = status.get("nodes") or {}

    is_conn = status.get("is_connected", False)
    port = status.get("connected_port") or status.get("configured_port") or "COM7"
    rssi = latest.get("rssi_dbm", -78)
    snr = latest.get("snr_db", 11.0)
    seq = latest.get("sequence", 0)
    freshness = latest.get("data_freshness", "FRESH")

    # Sensor readings
    pir_val = latest.get("pir_raw", 0)
    pir_active = latest.get("pir_active", False)

    piezo_val = latest.get("piezo_raw_adc", latest.get("piezo_p2p", 0))
    piezo_th = latest.get("piezo_threshold", 1775)
    piezo_active = latest.get("piezo_active", False)

    mic_val = latest.get("mic_raw_rms", latest.get("mic_rms", 0))
    mic_th = latest.get("mic_threshold", 255000)
    mic_active = latest.get("mic_active", False)

    # Node modes
    node_a = nodes.get("node_a", "ON")
    node_b = nodes.get("node_b", "ON")

    # Color formatters
    c_status = C_GREEN if is_conn else C_RED
    c_fresh = C_GREEN if freshness == "FRESH" else C_YELLOW
    c_a = C_GREEN if node_a == "ON" else C_DIM
    c_b = C_GREEN if node_b == "ON" else C_DIM
    c_pir = C_RED if pir_active else C_GREEN
    c_piezo = C_RED if piezo_active else C_GREEN
    c_mic = C_RED if mic_active else C_GREEN

    if clear:
        print("\033[H\033[J", end="")

    top_border = f"{C_BOLD}{C_CYAN}┌{'─' * (width + 2)}┐{C_RESET}"
    mid_border = f"{C_BOLD}{C_CYAN}├{'─' * (width + 2)}┤{C_RESET}"
    bot_border = f"{C_BOLD}{C_CYAN}└{'─' * (width + 2)}┘{C_RESET}"

    # Row 1: Header + URL + Status
    row1 = f"{C_BOLD}PRW-WILD DIGITAL TWIN{C_RESET}  {C_DIM}│{C_RESET}  {C_YELLOW}{url}{C_RESET}  {C_DIM}│{C_RESET}  STATUS: {C_GREEN}● ONLINE{C_RESET}"
    
    # Row 2: Hardware Gateway
    conn_str = f"{c_status}● CONNECTED{C_RESET}" if is_conn else f"{c_status}○ DISCONNECTED{C_RESET}"
    fresh_str = f"{c_fresh}[{freshness}]{C_RESET}"
    row2 = f"{C_BOLD}HARDWARE{C_RESET} : {port} ({conn_str})  LoRa: 433MHz ({rssi} dBm, SNR {snr:.1f} dB) {fresh_str}"
    
    # Row 3: ESP32 Modes
    row3 = f"{C_BOLD}MODES   {C_RESET}: [ESP32-A: {c_a}{node_a}{C_RESET}]  [ESP32-B: {c_b}{node_b}{C_RESET}]  Cascade: {C_CYAN}A->B Active{C_RESET}"
    
    # Row 4: Sensors
    pir_txt = f"PIR: {c_pir}{pir_val} ({'ALERT' if pir_active else 'LOW'}){C_RESET}"
    piezo_txt = f"Piezo: {c_piezo}{piezo_val} ADC{C_RESET} {C_DIM}(>{piezo_th}){C_RESET}"
    mic_txt = f"Mic: {c_mic}{mic_val:,} RMS{C_RESET} {C_DIM}(>{mic_th:,}){C_RESET}"
    row4 = f"{C_BOLD}SENSORS {C_RESET}: {pir_txt} │ {piezo_txt} │ {mic_txt}"
    
    # Row 5: 3D Twin state
    row5 = f"{C_BOLD}3D TWIN {C_RESET}: Target: ELEPHANT_01 (40.0m to fence) │ Layers L1-L3: {C_GREEN}ACTIVE{C_RESET}"

    print(top_border)
    print(format_row(row1, width))
    print(mid_border)
    print(format_row(row2, width))
    print(format_row(row3, width))
    print(format_row(row4, width))
    print(format_row(row5, width))
    print(bot_border)


def main() -> None:
    parser = argparse.ArgumentParser(
        description="PRW-Wild Digital Twin — Quick Launcher & Shortest Terminal View",
        prog="opentwin",
    )
    parser.add_argument(
        "-p", "--port", type=int, default=DEFAULT_PORT, help="Server port (default: 8000)"
    )
    parser.add_argument(
        "-n", "--no-open", action="store_true", help="Do not open the browser"
    )
    parser.add_argument(
        "-w", "--watch", "-l", "--live", action="store_true", help="Watch live sensor updates in terminal"
    )
    parser.add_argument(
        "-c", "--compact", action="store_true", default=True, help="Open website in compact/shortest UI view (default: True)"
    )
    parser.add_argument(
        "--full", action="store_true", help="Open website in full standard view without short mode"
    )

    args = parser.parse_args()
    enable_windows_ansi()

    url = f"http://127.0.0.1:{args.port}/"
    web_launch_url = url if args.full else f"{url}?view=short"

    # 1. Ensure server is running
    is_running = check_server(url)
    if not is_running:
        print(f"{C_YELLOW}[opentwin] Web server not running on port {args.port}. Starting in background...{C_RESET}")
        started = start_server_in_background(args.port)
        if not started:
            print(f"{C_RED}[opentwin] Could not connect to digital twin server on port {args.port}.{C_RESET}")
            sys.exit(1)
        print(f"{C_GREEN}[opentwin] Server started successfully.{C_RESET}")

    # 2. Open browser if not suppressed
    if not args.no_open and not args.watch:
        try:
            webbrowser.open(web_launch_url)
        except Exception:
            pass

    # 3. Render shortest view
    if args.watch:
        print(f"{C_CYAN}[opentwin] Live monitoring active. Press Ctrl+C to stop.{C_RESET}\n")
        try:
            while True:
                render_shortest_view(url, clear=True)
                time.sleep(1.0)
        except KeyboardInterrupt:
            print(f"\n{C_DIM}[opentwin] Stopped.{C_RESET}")
    else:
        render_shortest_view(url, clear=False)
        print(f"{C_DIM}Website opened -> {web_launch_url}  (Run 'opentwin -w' for live terminal watch){C_RESET}")


if __name__ == "__main__":
    main()
