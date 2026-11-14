"""PRW-Wild Digital Twin Web Server.

Provides a robust HTTP server serving the interactive Digital Twin visualizer,
scenario runner, real-time telemetry streaming, and REST API.
"""

from __future__ import annotations

import base64
import http.server
import json
import mimetypes
import os
import re
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
from prw_wild.ecosystem import PopulationEcosystem, SPECIES_REGISTRY
from prw_wild.hardware.control_service import (
    GLOBAL_HARDWARE_MANAGER,
    HardwareOperatingMode,
    LayerAction,
)
from prw_wild.vision import (
    WildlifeVisionDetector,
    MultiObjectTracker,
    VisualRiskEstimator,
    TARGET_CLASSES,
)

mimetypes.add_type("model/gltf-binary", ".glb")
mimetypes.add_type("model/gltf+json", ".gltf")

# Global Ecosystem and Vision Singletons
ECOSYSTEM_LOCK = threading.RLock()
GLOBAL_ECOSYSTEM = PopulationEcosystem(population_size=75, seed=42)
GLOBAL_VISION_DETECTOR = WildlifeVisionDetector()
GLOBAL_VISION_TRACKER = MultiObjectTracker()
GLOBAL_VISION_RISK = VisualRiskEstimator()

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

    def end_headers(self):
        self.send_header("Cache-Control", "no-cache, no-store, must-revalidate")
        self.send_header("Pragma", "no-cache")
        self.send_header("Expires", "0")
        self.send_header("X-Content-Type-Options", "nosniff")
        self.send_header("X-Frame-Options", "SAMEORIGIN")
        self.send_header("X-XSS-Protection", "1; mode=block")
        self.send_header("Referrer-Policy", "strict-origin-when-cross-origin")
        self.send_header("Permissions-Policy", "camera=(), microphone=(), geolocation=()")
        self.send_header(
            "Content-Security-Policy",
            "default-src 'self' 'unsafe-inline' 'unsafe-eval' data: blob:; "
            "script-src 'self' 'unsafe-inline' 'unsafe-eval' blob:; "
            "style-src 'self' 'unsafe-inline' https://fonts.googleapis.com; "
            "font-src 'self' data: https://fonts.gstatic.com; "
            "img-src 'self' data: blob:; "
            "connect-src 'self' data: blob:; "
            "worker-src 'self' blob:; "
            "media-src 'self' data: blob:;"
        )
        super().end_headers()

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
            if not re.match(r"^[a-zA-Z0-9_\-]+$", sc_id):
                self._send_error_json("Invalid scenario ID format", 400)
                return
            candidates = list(SCENARIOS_DIR.glob(f"{sc_id}.json"))
            if not candidates:
                candidates = [c for c in SCENARIOS_DIR.glob("*.json") if c.stem == sc_id]
            if candidates:
                try:
                    target_file = candidates[0].resolve()
                    if not str(target_file).startswith(str(SCENARIOS_DIR.resolve())):
                        self._send_error_json("Access denied", 403)
                        return
                    with open(target_file, "r", encoding="utf-8") as f:
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

        if path == "/api/ecosystem/population":
            self._send_json({
                "population": [a.to_dict() for a in GLOBAL_ECOSYSTEM.agents],
                "count": len(GLOBAL_ECOSYSTEM.agents),
                "time_s": GLOBAL_ECOSYSTEM.time_s,
                "world_bounds": GLOBAL_ECOSYSTEM.world_bounds,
                "boundary_x": GLOBAL_ECOSYSTEM.boundary_x,
                "resources": [
                    {
                        "patch_id": r.patch_id,
                        "resource_type": r.resource_type,
                        "position": {"x": r.position.x, "y": r.position.y},
                        "radius_m": r.radius_m,
                        "current_amount": round(r.current_amount, 1),
                        "max_capacity": r.max_capacity,
                    }
                    for r in GLOBAL_ECOSYSTEM.resources
                ],
                "species_profiles": {
                    k: {
                        "species_id": v.species_id,
                        "common_name": v.common_name,
                        "scientific_name": v.scientific_name,
                        "mass_kg": v.mass_kg,
                        "visual_model": v.visual_model,
                        "radar_color": v.radar_color,
                        "diet": v.diet,
                    }
                    for k, v in SPECIES_REGISTRY.items()
                }
            })
            return

        if path == "/api/vision/status":
            self._send_json({
                "backend": GLOBAL_VISION_DETECTOR.backend,
                "active_tracks_count": len(GLOBAL_VISION_TRACKER.trackers),
                "confidence_calibration": "RAW (NOT CALIBRATED)",
                "classes": [
                    {
                        "class_id": c.class_id,
                        "name": c.name,
                        "scientific_name": c.scientific_name,
                        "is_supported": c.is_supported_by_model,
                    }
                    for c in TARGET_CLASSES.values()
                ]
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

        if path == "/api/hardware/status":
            self._send_json(GLOBAL_HARDWARE_MANAGER.get_status())
            return

        if path == "/api/hardware/telemetry":
            from prw_wild.hardware.lora_bridge import LoraSerialBridge
            bridge = LoraSerialBridge.get_instance()
            self._send_json({
                "latest": bridge.get_latest_telemetry(),
                "history": bridge.get_telemetry_history(50),
                "status": bridge.get_status()
            })
            return

        if path == "/api/hardware/events":
            from prw_wild.hardware.lora_bridge import LoraSerialBridge
            bridge = LoraSerialBridge.get_instance()
            self._send_json({
                "physical_alerts": bridge.get_alerts(50),
                "hardware_commands": GLOBAL_HARDWARE_MANAGER.command_history[:50]
            })
            return

        if path == "/api/hardware/alerts":
            from prw_wild.hardware.lora_bridge import LoraSerialBridge
            bridge = LoraSerialBridge.get_instance()
            self._send_json({
                "alerts": bridge.get_alerts(50),
                "unacknowledged_count": bridge.get_status().get("unacknowledged_alerts_count", 0)
            })
            return

        if path == "/api/hardware/calibration":
            from prw_wild.hardware.lora_bridge import LoraSerialBridge
            bridge = LoraSerialBridge.get_instance()
            self._send_json({
                "mic_threshold": bridge.mic_threshold,
                "piezo_threshold": bridge.piezo_threshold,
                "piezo_enabled": bridge.piezo_enabled
            })
            return

        if path == "/api/hardware/nodes":
            from prw_wild.hardware.lora_bridge import LoraSerialBridge
            bridge = LoraSerialBridge.get_instance()
            self._send_json(bridge.get_node_modes())
            return

        if path == "/api/hardware/wiring":
            manifest_file = PROJECT_ROOT / "hardware" / "wiring_manifest_actual.json"
            if not manifest_file.exists():
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
            if not re.match(r"^[a-zA-Z0-9_\-]+$", dev_id):
                self._send_error_json("Invalid device identifier format", 400)
                return
            hw_dir = PROJECT_ROOT / "hardware" / "devices"
            dev_file = hw_dir / f"{dev_id}.json"
            if not dev_file.exists():
                dev_file = hw_dir / f"{dev_id}"
            if dev_file.exists() and dev_file.is_file():
                resolved_file = dev_file.resolve()
                if not str(resolved_file).startswith(str(hw_dir.resolve())):
                    self._send_error_json("Access denied", 403)
                    return
                try:
                    with open(resolved_file, "r", encoding="utf-8") as jf:
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
        global GLOBAL_ECOSYSTEM
        parsed = urllib.parse.urlparse(self.path)
        path = parsed.path

        content_length = int(self.headers.get("Content-Length", 0))
        body = self.rfile.read(content_length) if content_length > 0 else b"{}"

        try:
            payload = json.loads(body.decode("utf-8")) if body else {}
        except Exception:
            payload = {}

        if path == "/api/hardware/mode":
            mode_str = str(payload.get("mode", "SIMULATION_ONLY")).upper()
            valid_modes = (
                "SIMULATION_ONLY", "HARDWARE_TEST", "AUTO_HARDWARE_CONTROL",
                "AUTO_SENSOR", "AUTO", "MANUAL", "SIMULATION"
            )
            if mode_str not in valid_modes:
                self._send_error_json("Invalid hardware operating mode; must be AUTO_SENSOR, MANUAL, SIMULATION (or legacy SIMULATION_ONLY, HARDWARE_TEST, AUTO_HARDWARE_CONTROL)", 400)
                return
            res = GLOBAL_HARDWARE_MANAGER.set_mode(mode_str)
            self._send_json(res)
            return

        if path == "/api/hardware/nodes":
            node = payload.get("node")
            mode = payload.get("mode")
            if not node or mode is None:
                self._send_error_json("Missing 'node' ('A' or 'B') or 'mode' ('ON' or 'OFF')", 400)
                return
            from prw_wild.hardware.lora_bridge import LoraSerialBridge
            bridge = LoraSerialBridge.get_instance()
            res = bridge.set_node_mode(str(node), mode)
            if not res.get("success"):
                self._send_error_json(res.get("error", "Failed to set node mode"), 400)
                return
            self._send_json(res)
            return

        if path == "/api/hardware/command":
            raw_layer = payload.get("layer", 1)
            try:
                layer = int(raw_layer)
            except (ValueError, TypeError):
                self._send_error_json("Invalid layer parameter; must be 1, 2, or 3", 400)
                return
            if layer not in (1, 2, 3):
                self._send_error_json("Layer out of range; must be 1, 2, or 3", 400)
                return
            action = str(payload.get("action", "OFF")).upper()
            if action not in ("ON", "OFF"):
                self._send_error_json("Invalid action parameter; must be 'ON' or 'OFF'", 400)
                return
            res = GLOBAL_HARDWARE_MANAGER.send_manual_command(layer, action)
            self._send_json(res.to_dict())
            return

        if path == "/api/hardware/led":
            from prw_wild.hardware.lora_bridge import LoraSerialBridge
            bridge = LoraSerialBridge.get_instance()
            if "all" in payload:
                all_state = bool(payload.get("all"))
                res = bridge.set_all_manual_leds(all_state)
                self._send_json(res)
                return
            try:
                led_num = int(payload.get("led", 1))
            except (ValueError, TypeError):
                self._send_error_json("Invalid led parameter; must be 1..6", 400)
                return
            if led_num < 1 or led_num > 6:
                self._send_error_json("LED number out of range; must be 1..6", 400)
                return
            state = bool(payload.get("state", False))
            res = bridge.set_manual_led(led_num, state)
            self._send_json(res)
            return

        if path == "/api/hardware/event":
            animal_id = payload.get("animal_id", "ELEPHANT_01")
            layer = payload.get("layer", "L1")
            transition = payload.get("transition", "ENTER")
            timestamp_s = float(payload.get("timestamp_s", 0.0))
            res = GLOBAL_HARDWARE_MANAGER.process_event(animal_id, layer, transition, timestamp_s)
            self._send_json(res)
            return

        if path == "/api/hardware/connect":
            target_port = payload.get("port")
            from prw_wild.hardware.lora_bridge import LoraSerialBridge
            bridge = LoraSerialBridge.get_instance()
            ok = bridge.connect(target_port)
            self._send_json({
                "success": ok,
                "connected": bridge.is_connected,
                "port": bridge.connected_port,
                "error": bridge.last_error
            })
            return

        if path == "/api/hardware/emergency_stop":
            results = GLOBAL_HARDWARE_MANAGER.emergency_all_off()
            self._send_json({
                "success": True,
                "action": "EMERGENCY_ALL_OFF",
                "results": [r.to_dict() for r in results]
            })
            return

        if path.startswith("/api/hardware/alerts/") and path.endswith("/acknowledge") or path in ["/api/hardware/alerts/acknowledge", "/api/hardware/alert/acknowledge"]:
            alert_id = None
            if "/api/hardware/alerts/" in path:
                parts = path.split("/")
                if len(parts) >= 5:
                    alert_id = parts[4]
            if not alert_id:
                alert_id = payload.get("alert_id") or payload.get("id")
            from prw_wild.hardware.lora_bridge import LoraSerialBridge
            bridge = LoraSerialBridge.get_instance()
            ok = bridge.acknowledge_alert(str(alert_id)) if alert_id else False
            self._send_json({"success": ok, "alert_id": alert_id})
            return

        if path == "/api/hardware/connection/configure":
            port = payload.get("port")
            baud = int(payload.get("baud_rate", 115200))
            from prw_wild.hardware.lora_bridge import LoraSerialBridge
            bridge = LoraSerialBridge.get_instance()
            ok = bridge.configure_port(port, baud) if port else False
            self._send_json({
                "success": ok,
                "port": bridge.connected_port,
                "baud_rate": bridge.baud_rate,
                "is_connected": bridge.is_connected,
                "error": bridge.last_error
            })
            return

        if path == "/api/hardware/connection/reconnect":
            port = payload.get("port")
            from prw_wild.hardware.lora_bridge import LoraSerialBridge
            bridge = LoraSerialBridge.get_instance()
            ok = bridge.reconnect(port)
            self._send_json({
                "success": ok,
                "port": bridge.connected_port,
                "is_connected": bridge.is_connected,
                "error": bridge.last_error
            })
            return

        if path == "/api/hardware/calibration":
            from prw_wild.hardware.lora_bridge import LoraSerialBridge
            bridge = LoraSerialBridge.get_instance()
            raw_mic = payload.get("mic_threshold")
            raw_piezo = payload.get("piezo_threshold")
            raw_p_enabled = payload.get("piezo_enabled")

            mic_thresh = None
            if raw_mic is not None:
                try:
                    mic_thresh = max(0, min(1000000, int(raw_mic)))
                except (ValueError, TypeError):
                    self._send_error_json("Invalid mic_threshold format", 400)
                    return

            piezo_thresh = None
            if raw_piezo is not None:
                try:
                    piezo_thresh = max(0, min(4095, int(raw_piezo)))
                except (ValueError, TypeError):
                    self._send_error_json("Invalid piezo_threshold format", 400)
                    return

            piezo_en = bool(raw_p_enabled) if raw_p_enabled is not None else None

            res = bridge.set_calibration(
                mic_threshold=mic_thresh,
                piezo_threshold=piezo_thresh,
                piezo_enabled=piezo_en
            )
            self._send_json({"success": True, "calibration": res})
            return

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

        if path == "/api/ecosystem/step":
            try:
                try:
                    dt = max(0.01, min(5.0, float(payload.get("dt", 0.5))))
                except (ValueError, TypeError):
                    dt = 0.5
                with ECOSYSTEM_LOCK:
                    snapshots = GLOBAL_ECOSYSTEM.step(dt)
                    layer_counts = {1: 0, 2: 0, 3: 0}
                    for a in GLOBAL_ECOSYSTEM.agents:
                        px = a.position.x
                        if 45.0 <= px < 70.0:
                            layer_counts[1] += 1
                        elif 70.0 <= px < 85.0:
                            layer_counts[2] += 1
                        elif px >= 85.0:
                            layer_counts[3] += 1

                    hw_events = GLOBAL_HARDWARE_MANAGER.process_simulation_occupancy(layer_counts)
                    cur_time = GLOBAL_ECOSYSTEM.time_s
                    resources = [
                        {
                            "patch_id": r.patch_id,
                            "resource_type": r.resource_type,
                            "current_amount": round(r.current_amount, 1),
                            "max_capacity": r.max_capacity,
                        }
                        for r in GLOBAL_ECOSYSTEM.resources
                    ]

                self._send_json({
                    "time_s": cur_time,
                    "agents": snapshots,
                    "layer_counts": layer_counts,
                    "hardware_events": [e.to_dict() for e in hw_events],
                    "hardware_status": GLOBAL_HARDWARE_MANAGER.get_status(),
                    "resources": resources
                })
            except Exception as e:
                import traceback
                print(f"[PRW-Wild Server] Ecosystem step error: {e}")
                self._send_json({
                    "time_s": 0.0,
                    "agents": [],
                    "layer_counts": {1: 0, 2: 0, 3: 0},
                    "hardware_events": [],
                    "hardware_status": GLOBAL_HARDWARE_MANAGER.get_status(),
                    "resources": [],
                    "warning": str(e)
                })
            return

        if path == "/api/ecosystem/inject":
            aid = str(payload.get("animal_id", ""))
            intent = str(payload.get("intent", "approach"))
            with ECOSYSTEM_LOCK:
                ok = GLOBAL_ECOSYSTEM.inject_event(aid, intent)
            self._send_json({"success": ok, "animal_id": aid, "intent": intent})
            return

        if path == "/api/ecosystem/reset":
            try:
                pop_sz = max(1, min(150, int(payload.get("population_size", 60))))
                seed = max(0, min(2147483647, int(payload.get("seed", 42))))
            except (ValueError, TypeError):
                self._send_error_json("Invalid reset parameters", 400)
                return
            with ECOSYSTEM_LOCK:
                GLOBAL_ECOSYSTEM = PopulationEcosystem(population_size=pop_sz, seed=seed)
            self._send_json({
                "success": True,
                "count": len(GLOBAL_ECOSYSTEM.agents),
                "seed": seed
            })
            return

        if path == "/api/vision/detect":
            # Genuine computer vision endpoint processing camera pixels
            img_data = payload.get("image", "")
            if not img_data:
                self._send_error_json("No image data provided", 400)
                return

            try:
                # Strip data URL header if present (e.g. data:image/jpeg;base64,...)
                if "," in img_data:
                    img_data = img_data.split(",", 1)[1]
                raw_bytes = base64.b64decode(img_data)

                # Run detector on actual rendered image
                t0 = time.time()
                detections = GLOBAL_VISION_DETECTOR.detect(raw_bytes)
                det_time_ms = round((time.time() - t0) * 1000.0, 2)

                # Feed detections to multi-object tracker
                det_dicts = [d.to_dict() for d in detections]
                active_tracks = GLOBAL_VISION_TRACKER.update(det_dicts)

                # Compute boundary crossing risks independently
                risks = []
                for trk in active_tracks:
                    risk_assessment = GLOBAL_VISION_RISK.evaluate_track(trk)
                    risks.append(risk_assessment.to_dict())

                self._send_json({
                    "success": True,
                    "detections": det_dicts,
                    "tracks": active_tracks,
                    "risk_assessments": risks,
                    "backend": GLOBAL_VISION_DETECTOR.backend,
                    "inference_time_ms": det_time_ms,
                    "timestamp": time.time(),
                })
                return
            except Exception as e:
                import traceback
                print(f"[PRW-Wild Server] Vision inference error: {e}\n{traceback.format_exc()}")
                self._send_error_json(f"Vision inference error: {e}", 500)
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
            scenario_id = str(payload.get("scenario_id", "approach_crossing"))
            raw_seed = payload.get("seed")
            seed = int(raw_seed) if raw_seed is not None and str(raw_seed).lstrip("-").isdigit() else None
            overrides = payload.get("overrides")
            try:
                res = execute_simulation(scenario_id, seed=seed, overrides=overrides)
                self._send_json(res)
            except Exception as e:
                import traceback
                print(f"[PRW-Wild Server] Simulation execution error: {e}\n{traceback.format_exc()}")
                self._send_error_json(f"Simulation failed: {e}", 500)
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
