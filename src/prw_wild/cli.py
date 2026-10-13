"""Command-line interface for PRW-Wild.

Usage:
    python -m prw_wild.cli --help
    python -m prw_wild.cli validate-config <config_path>
    python -m prw_wild.cli run --scenario <config_path> [--seed N]
    python -m prw_wild.cli batch --suite <suite_path> [--runs N]
    python -m prw_wild.cli report --run-dir <path>
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from prw_wild.config import load_config, validate_config, ConfigError, _deep_merge, DEFAULT_CONFIG


def cmd_validate(args: argparse.Namespace) -> int:
    """Validate a configuration file."""
    try:
        cfg = load_config(args.config)
        print(f"[OK] Configuration '{args.config}' is valid.")
        print(f"     Scenario: {cfg['scenario_id']}")
        print(f"     Duration: {cfg['simulation']['duration_s']}s")
        print(f"     Animals:  {len(cfg['animals'])}")
        print(f"     Sensors:  {len(cfg['sensors']['nodes'])}")
        return 0
    except (ConfigError, FileNotFoundError, json.JSONDecodeError) as e:
        print(f"[ERROR] {e}", file=sys.stderr)
        return 1


def cmd_run(args: argparse.Namespace) -> int:
    """Run a single scenario."""
    from prw_wild.experiment_runner import run_experiment

    try:
        cfg = load_config(args.scenario)
    except Exception as e:
        print(f"[ERROR] {e}", file=sys.stderr)
        return 1

    seed = args.seed if args.seed is not None else cfg["random_seed"]
    output_dir = Path(args.output) if args.output else None

    print(f"Running scenario '{cfg['scenario_id']}' with seed={seed}...")
    metrics, run_dir = run_experiment(cfg, output_dir=output_dir, seed_override=seed)

    print(f"\n=== Results ===")
    print(f"Run directory: {run_dir}")
    print(f"Actual crossings:  {metrics.actual_crossings}")
    print(f"Alerts:            {metrics.total_alerts}")
    print(f"Camera activations: {metrics.camera_activations}")
    print(f"Crossing recall:   {_fmt(metrics.crossing_recall)}")
    print(f"Mean lead time:    {_fmt(metrics.mean_warning_lead_time_s)}s")
    print(f"Estimated energy:  {metrics.estimated_energy_j}J")
    return 0


def cmd_batch(args: argparse.Namespace) -> int:
    """Run a suite of scenarios with multiple seeds."""
    from prw_wild.experiment_runner import run_experiment
    from prw_wild.metrics import save_experiment_summary, RunMetrics

    suite_path = Path(args.suite)
    if not suite_path.exists():
        print(f"[ERROR] Suite file not found: {suite_path}", file=sys.stderr)
        return 1

    with open(suite_path, "r", encoding="utf-8") as f:
        suite = json.load(f)

    n_runs = args.runs or suite.get("runs_per_scenario", 5)
    scenarios = suite.get("scenarios", [])
    base_seed = suite.get("base_seed", 42)

    all_metrics: list[RunMetrics] = []
    batch_dir = Path("outputs") / f"batch_{suite_path.stem}"
    batch_dir.mkdir(parents=True, exist_ok=True)

    for sc_path in scenarios:
        sc_path = Path(sc_path)
        if not sc_path.exists():
            print(f"[WARN] Scenario not found: {sc_path}, skipping.")
            continue

        try:
            cfg = load_config(sc_path)
        except Exception as e:
            print(f"[ERROR] {e}", file=sys.stderr)
            continue

        for i in range(n_runs):
            seed = base_seed + i
            run_dir = batch_dir / cfg["scenario_id"] / f"seed_{seed}"
            print(f"  Running {cfg['scenario_id']} seed={seed}...")
            metrics, _ = run_experiment(cfg, output_dir=run_dir, seed_override=seed)
            all_metrics.append(metrics)

    # Save aggregate
    save_experiment_summary(all_metrics, batch_dir / "experiment_summary.csv")
    print(f"\nBatch complete. {len(all_metrics)} runs saved to {batch_dir}")
    print(f"Summary: {batch_dir / 'experiment_summary.csv'}")
    return 0


def cmd_report(args: argparse.Namespace) -> int:
    """Generate/display report for a completed run."""
    run_dir = Path(args.run_dir)
    summary_path = run_dir / "summary.md"
    metrics_path = run_dir / "metrics.json"

    if summary_path.exists():
        print(summary_path.read_text(encoding="utf-8"))
    elif metrics_path.exists():
        data = json.loads(metrics_path.read_text(encoding="utf-8"))
        print(json.dumps(data, indent=2))
    else:
        print(f"[ERROR] No results found in {run_dir}", file=sys.stderr)
        return 1
    return 0


def cmd_web(args: argparse.Namespace) -> int:
    """Launch interactive Digital Twin Web Dashboard."""
    from prw_wild.web.server import run_server
    run_server(host=args.host, port=args.port, open_browser=args.open)
    return 0


def _fmt(v) -> str:
    import math
    if v is None or (isinstance(v, float) and math.isnan(v)):
        return "N/A"
    return f"{v:.4f}"


def main() -> int:
    parser = argparse.ArgumentParser(
        prog="prw_wild",
        description="PRW-Wild — Predictive RF-Wildlife Digital Twin CLI",
    )
    sub = parser.add_subparsers(dest="command")

    # validate-config
    p_val = sub.add_parser("validate-config", help="Validate a scenario config file")
    p_val.add_argument("config", type=str, help="Path to JSON config file")

    # run
    p_run = sub.add_parser("run", help="Run a single scenario simulation")
    p_run.add_argument("--scenario", required=True, help="Path to scenario config")
    p_run.add_argument("--seed", type=int, default=None, help="Random seed override")
    p_run.add_argument("--output", type=str, default=None, help="Output directory")

    # batch
    p_batch = sub.add_parser("batch", help="Run a suite of scenarios")
    p_batch.add_argument("--suite", required=True, help="Path to suite JSON")
    p_batch.add_argument("--runs", type=int, default=None, help="Runs per scenario")

    # report
    p_report = sub.add_parser("report", help="Display run report")
    p_report.add_argument("--run-dir", required=True, help="Path to run directory")

    # web
    p_web = sub.add_parser("web", help="Launch interactive Digital Twin Web Dashboard")
    p_web.add_argument("--port", type=int, default=8000, help="Port to listen on (default: 8000)")
    p_web.add_argument("--host", type=str, default="127.0.0.1", help="Host interface (default: 127.0.0.1)")
    p_web.add_argument("--open", action="store_true", help="Automatically open browser")

    args = parser.parse_args()
    if args.command is None:
        parser.print_help()
        return 0

    handlers = {
        "validate-config": cmd_validate,
        "run": cmd_run,
        "batch": cmd_batch,
        "report": cmd_report,
        "web": cmd_web,
    }
    return handlers[args.command](args)


if __name__ == "__main__":
    sys.exit(main())
