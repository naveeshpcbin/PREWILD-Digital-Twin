"""PRW-Wild Digital Twin Web Server.

Provides a robust HTTP server serving the interactive Digital Twin visualizer,
scenario runner, real-time telemetry streaming, and REST API.
"""

from __future__ import annotations

import http.server
import json
import mimetypes
import os
import shutil
import socketserver
import sys
import threading
import time
import urllib.parse
from pathlib import Path
from typing import Any

from prw_wild.config import load_config, _deep_merge, DEFAULT_CONFIG
from prw_wild.experiment_runner import run_experiment
from prw_wild.dispatch import DEFAULT_RECIPIENTS, DEFAULT_AUTHORITIES, AlertRouter

# Root paths
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent.parent
STATIC_DIR = Path(__file__).resolve().parent / "static"
CONFIGS_DIR = PROJECT_ROOT / "configs"
SCENARIOS_DIR = CONFIGS_DIR / "scenarios"
OUTPUTS_DIR = PROJECT_ROOT / "outputs"


def get_all_scenarios() -> list[dict[str, Any]]:
    """Scan and return all scenario configurations."""
    scenarios = []
    if not SCENARIOS_DIR.exists():
        return scenarios

    for p in sorted(SCENARIOS_DIR.glob("*.json")):
        try:
            with open(p, "r", encoding="utf-8") as f:
                data = json.load(f)
            scenarios.append({
                "id": data.get("scenario_id", p.stem),
                "filename": p.name,
                "path": str(p),
                "duration_s": data.get("simulation", {}).get("duration_s", 120.0),
                "time_step_s": data.get("simulation", {}).get("time_step_s", 0.5),
                "animals": data.get("animals", []),
                "description": data.get("description", f"Scenario: {p.stem}"),
            })
        except Exception as e:
            scenarios.append({
                "id": p.stem,
                "filename": p.name,
                "path": str(p),
                "error": str(e),
            })
    return scenarios


def execute_simulation(scenario_id_or_path: str, seed: int | None = None, overrides: dict | None = None) -> dict[str, Any]:
    """Execute a single scenario and return packaged results."""
    # Find scenario file
    config_path = None
    if Path(scenario_id_or_path).exists():
        config_path = Path(scenario_id_or_path)
    else:
        # Search by ID, stem, or scenario_id inside JSON
        candidates = list(SCENARIOS_DIR.glob(f"{scenario_id_or_path}.json"))
        if candidates:
            config_path = candidates[0]
        else:
            for c in SCENARIOS_DIR.glob("*.json"):
                if c.stem == scenario_id_or_path:
                    config_path = c
                    break
                try:
                    with open(c, "r", encoding="utf-8") as f:
                        d = json.load(f)
                    if d.get("scenario_id") == scenario_id_or_path:
                        config_path = c
                        break
                except Exception:
                    pass

    if config_path is not None and config_path.exists():
        cfg = load_config(config_path)
    else:
        cfg = load_config(DEFAULT_CONFIG)
        cfg["scenario_id"] = scenario_id_or_path

    if overrides:
        cfg = _deep_merge(cfg, overrides)

    metrics, run_dir = run_experiment(cfg, seed_override=seed)

    # Load results
    ground_truth = []
    gt_file = run_dir / "ground_truth.jsonl"
    if gt_file.exists():
        with open(gt_file, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line:
                    ground_truth.append(json.loads(line))

    events = []
    ev_file = run_dir / "events.jsonl"
    if ev_file.exists():
        with open(ev_file, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line:
                    events.append(json.loads(line))

    metrics_dict = {}
    m_file = run_dir / "metrics.json"
    if m_file.exists():
        with open(m_file, "r", encoding="utf-8") as f:
            metrics_dict = json.load(f)

    summary_md = ""
    s_file = run_dir / "summary.md"
    if s_file.exists():
        summary_md = s_file.read_text(encoding="utf-8")

    config_used = {}
    c_file = run_dir / "config_used.json"
    if c_file.exists():
        with open(c_file, "r", encoding="utf-8") as f:
            config_used = json.load(f)

    dispatches = []
    disp_file = run_dir / "dispatches.json"
    if disp_file.exists():
        try:
            with open(disp_file, "r", encoding="utf-8") as f:
                dispatches = json.load(f)
        except Exception:
            pass

    return {
        "success": True,
        "run_id": run_dir.name,
        "run_dir": str(run_dir),
        "scenario_id": cfg.get("scenario_id", "default"),
        "seed": seed if seed is not None else cfg.get("random_seed", 42),
        "config": config_used,
        "metrics": metrics_dict,
        "ground_truth": ground_truth,
        "events": events,
        "dispatches": dispatches,
        "summary_markdown": summary_md,
    }


class DigitalTwinHTTPHandler(http.server.SimpleHTTPRequestHandler):
    """Custom request handler with REST API and static file serving."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(STATIC_DIR), **kwargs)

    def do_OPTIONS(self):
        """Handle CORS pre-flight."""
        self.send_response(200)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()

    def _send_json(self, data: Any, status: int = 200):
        body = json.dumps(data, indent=2).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Cache-Control", "no-cache, no-store, must-revalidate")
        self.end_headers()
        self.wfile.write(body)

    def _send_error_json(self, message: str, status: int = 400):
        self._send_json({"error": message, "success": False}, status=status)

    def do_GET(self):
        parsed = urllib.parse.urlparse(self.path)
        path = parsed.path

        # REST API endpoints
        if path == "/api/status" or path == "/api/health":
            self._send_json({
                "status": "online",
                "version": "0.1.0",
                "service": "PRW-Wild Digital Twin",
                "time": time.time(),
            })
            return

        if path == "/api/scenarios":
            scenarios = get_all_scenarios()
            self._send_json({"scenarios": scenarios, "count": len(scenarios)})
            return

        if path.startswith("/api/scenarios/"):
            sc_id = path.split("/api/scenarios/")[1]
            candidates = list(SCENARIOS_DIR.glob(f"{sc_id}.json"))
            if not candidates:
                candidates = [c for c in SCENARIOS_DIR.glob("*.json") if c.stem == sc_id]
            if candidates:
                try:
                    with open(candidates[0], "r", encoding="utf-8") as f:
                        data = json.load(f)
                    self._send_json(data)
                    return
                except Exception as e:
                    self._send_error_json(f"Error loading scenario: {e}", 500)
                    return
            self._send_error_json("Scenario not found", 404)
            return

        if path == "/api/runs":
            runs_dir = OUTPUTS_DIR / "runs"
            runs_list = []
            if runs_dir.exists():
                for rd in sorted(runs_dir.iterdir(), reverse=True):
                    if rd.is_dir():
                        m_file = rd / "metrics.json"
                        meta = {"run_id": rd.name}
                        if m_file.exists():
                            try:
                                with open(m_file, "r", encoding="utf-8") as f:
                                    meta["metrics"] = json.load(f)
                            except Exception:
                                pass
                        runs_list.append(meta)
            self._send_json({"runs": runs_list[:30]})
            return

        if path == "/api/contacts":
            self._send_json({
                "recipients": [r.to_dict() for r in DEFAULT_RECIPIENTS],
                "authorities": [a.to_dict() for a in DEFAULT_AUTHORITIES],
            })
            return

        if path == "/api/hardware":
            hw_dir = PROJECT_ROOT / "hardware" / "devices"
            devices = []
            if hw_dir.exists():
                for f in sorted(hw_dir.glob("*.json")):
                    try:
                        with open(f, "r", encoding="utf-8") as jf:
                            d = json.load(jf)
                        devices.append({
                            "device_id": d.get("device_id", f.stem),
                            "name": d.get("name", f.stem),
                            "verification_status": d.get("verification_status", "UNKNOWN"),
                            "role_in_prw_wild": d.get("role_in_prw_wild", ""),
                            "filename": f.name,
                        })
                    except Exception as e:
                        devices.append({"device_id": f.stem, "error": str(e)})
            self._send_json({"devices": devices, "count": len(devices)})
            return

        if path == "/api/hardware/wiring":
            manifest_file = PROJECT_ROOT / "hardware" / "wiring_manifest.json"
            if manifest_file.exists():
                try:
                    with open(manifest_file, "r", encoding="utf-8") as mf:
                        d = json.load(mf)
                    self._send_json(d)
                    return
                except Exception as e:
                    self._send_error_json(f"Error reading wiring manifest: {e}", 500)
                    return
            self._send_error_json("Wiring manifest not found", 404)
            return

        if path.startswith("/api/hardware/"):
            dev_id = path.split("/api/hardware/")[1]
            hw_dir = PROJECT_ROOT / "hardware" / "devices"
            dev_file = hw_dir / f"{dev_id}.json"
            if not dev_file.exists():
                dev_file = hw_dir / f"{dev_id}"
            if dev_file.exists() and dev_file.is_file():
                try:
                    with open(dev_file, "r", encoding="utf-8") as jf:
                        d = json.load(jf)
                    self._send_json(d)
                    return
                except Exception as e:
                    self._send_error_json(f"Error reading hardware file: {e}", 500)
                    return
            self._send_error_json("Hardware device not found", 404)
            return

        # Default static file routing
        super().do_GET()

    def do_POST(self):
        parsed = urllib.parse.urlparse(self.path)
        path = parsed.path

        content_length = int(self.headers.get("Content-Length", 0))
        body = self.rfile.read(content_length) if content_length > 0 else b"{}"

        try:
            payload = json.loads(body.decode("utf-8")) if body else {}
        except Exception:
            payload = {}

        if path == "/api/test-dispatch":
            router = AlertRouter()
            recs = router.route_alert(
                alert_id=f"manual_{int(time.time())}",
                timestamp_s=payload.get("time_s", 50.0),
                severity=payload.get("severity", "WARNING"),
                estimated_position=payload.get("position", [95.0, 100.0]),
                eta_s=payload.get("eta_s", 15.0),
                species=payload.get("species", "ELEPHANT"),
                risk_score=payload.get("risk_score", 0.85),
            )
            self._send_json({"dispatches": [r.to_dict() for r in recs], "count": len(recs)})
            return

        if path == "/api/sound-alert":
            def _beep():
                try:
                    import winsound
                    if payload.get("alert_type") == "breach":
                        winsound.Beep(900, 200)
                        winsound.Beep(1200, 300)
                    else:
                        winsound.Beep(650, 150)
                except Exception:
                    pass
            threading.Thread(target=_beep, daemon=True).start()
            self._send_json({"status": "tone_triggered"})
            return

        if path == "/api/run":
            scenario_id = payload.get("scenario_id", "approach_crossing")
            seed = payload.get("seed")
            overrides = payload.get("overrides")
            try:
                res = execute_simulation(scenario_id, seed=seed, overrides=overrides)
                self._send_json(res)
            except Exception as e:
                import traceback
                self._send_error_json(f"Simulation failed: {e}\n{traceback.format_exc()}", 500)
            return

        if path == "/api/batch":
            # Run all standard scenarios
            results = []
            suite = [
                "approach_crossing",
                "turns_away",
                "nuisance_triggers",
                "degraded_network",
                "camera_gating",
            ]
            base_seed = payload.get("seed", 42)
            for sc_id in suite:
                try:
                    res = execute_simulation(sc_id, seed=base_seed)
                    results.append({
                        "scenario_id": sc_id,
                        "metrics": res.get("metrics", {}),
                        "actual_crossings": res.get("metrics", {}).get("actual_crossings", 0),
                        "crossing_recall": res.get("metrics", {}).get("crossing_recall"),
                        "mean_lead_time_s": res.get("metrics", {}).get("mean_warning_lead_time_s"),
                        "camera_activations": res.get("metrics", {}).get("camera_activations", 0),
                        "energy_j": res.get("metrics", {}).get("estimated_energy_j", 0.0),
                        "total_alerts": res.get("metrics", {}).get("total_alerts", 0),
                        "run_id": res.get("run_id"),
                    })
                except Exception as e:
                    results.append({"scenario_id": sc_id, "error": str(e)})

            self._send_json({"suite": results, "seed": base_seed})
            return

        if path == "/api/counterfactual":
            scenario_id = payload.get("scenario_id", "approach_crossing")
            seed = payload.get("seed", 42)
            policies = [
                ("predictive", "Policy A: Full PRW-Wild (Predictive RF + Gated Camera)"),
                ("pir_only", "Policy B: PIR-Only Trigger (Reactive Camera)"),
                ("always_on", "Policy C: Always-On Camera (100% Duty Cycle)"),
                ("rf_only", "Policy D: RF/CSI-Only Trigger (No Corroboration)"),
            ]
            policy_results = {}
            for pol_key, pol_label in policies:
                try:
                    overrides = {"policies": {"active": pol_key}}
                    res = execute_simulation(scenario_id, seed=seed, overrides=overrides)
                    m = res.get("metrics", {})
                    policy_results[pol_key] = {
                        "label": pol_label,
                        "policy": pol_key,
                        "metrics": m,
                        "actual_crossings": m.get("actual_crossings", 0),
                        "crossing_recall": m.get("crossing_recall", 0.0),
                        "mean_lead_time_s": m.get("mean_warning_lead_time_s", 0.0),
                        "camera_activations": m.get("camera_activations", 0),
                        "camera_duty_cycle_pct": m.get("camera_duty_cycle_pct", 0.0),
                        "energy_j": m.get("estimated_energy_j", 0.0),
                        "total_alerts": m.get("total_alerts", 0),
                        "events_count": len(res.get("events", [])),
                        "events": res.get("events", [])[:50],
                    }
                except Exception as e:
                    policy_results[pol_key] = {
                        "label": pol_label,
                        "policy": pol_key,
                        "error": str(e),
                    }
            self._send_json({"scenario_id": scenario_id, "seed": seed, "policies": policy_results})
            return

        self._send_error_json("Not found", 404)


class ThreadingDigitalTwinServer(socketserver.ThreadingMixIn, http.server.HTTPServer):
    daemon_threads = True
    allow_reuse_address = True


def run_server(host: str = "127.0.0.1", port: int = 8000, open_browser: bool = False):
    """Run the Digital Twin Web server."""
    # Ensure static directory exists
    STATIC_DIR.mkdir(parents=True, exist_ok=True)

    server_address = (host, port)
    try:
        httpd = ThreadingDigitalTwinServer(server_address, DigitalTwinHTTPHandler)
    except OSError as e:
        if "address already in use" in str(e).lower() or e.errno in (98, 10048):
            # Try alternate port
            port = port + 1
            server_address = (host, port)
            httpd = ThreadingDigitalTwinServer(server_address, DigitalTwinHTTPHandler)
        else:
            raise

    url = f"http://{host}:{port}/"
    print(f"\n=======================================================")
    print(f"  PRW-Wild Digital Twin Web Dashboard is RUNNING")
    print(f"  Link: {url}")
    print(f"=======================================================\n")

    if open_browser:
        import webbrowser
        threading.Thread(target=lambda: (time.sleep(0.5), webbrowser.open(url))).start()

    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\nStopping PRW-Wild Web Server...")
        httpd.shutdown()
        httpd.server_close()


if __name__ == "__main__":
    port = 8000
    if len(sys.argv) > 1 and sys.argv[1].isdigit():
        port = int(sys.argv[1])
    run_server(port=port)
