"""Entry point for python -m prw_wild.web"""

import argparse
from prw_wild.web.server import run_server

def main():
    parser = argparse.ArgumentParser(description="PRW-Wild Digital Twin Web Dashboard")
    parser.add_argument("--port", type=int, default=8000, help="Port to listen on (default 8000)")
    parser.add_argument("--host", type=str, default="127.0.0.1", help="Host interface (default 127.0.0.1)")
    parser.add_argument("--open", action="store_true", help="Automatically open browser")
    args = parser.parse_args()
    run_server(host=args.host, port=args.port, open_browser=args.open)

if __name__ == "__main__":
    main()
