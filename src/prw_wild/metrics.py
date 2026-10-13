"""Metrics calculation from simulation run outputs.

Computes detection performance, warning lead time, camera usage,
and estimated energy from the event logs and ground-truth records.

All energy values are ESTIMATED from configurable power profiles,
not measured on physical hardware.
"""

from __future__ import annotations

import csv
import json
import math
from dataclasses import dataclass, field, asdict
from pathlib import Path
from typing import Any, Optional

from prw_wild.event_log import EventType, load_events


@dataclass
class RunMetrics:
    """Metrics for a single simulation run."""
    scenario_id: str = ""
    run_id: str = ""
    seed: int = 0
    duration_s: float = 0.0

    # Crossing metrics
    actual_crossings: int = 0
    predicted_crossings: int = 0
    true_positive_detections: int = 0
    false_alerts: int = 0
    missed_crossings: int = 0

    # Derived
    crossing_recall: float = float("nan")
    crossing_precision: float = float("nan")
    f1_score: float = float("nan")

    # Timing
    warning_lead_times_s: list[float] = field(default_factory=list)
    mean_warning_lead_time_s: float = float("nan")
    crossing_time_errors_s: list[float] = field(default_factory=list)
    mean_crossing_time_error_s: float = float("nan")

    # Camera
    camera_activations: int = 0
    camera_duty_cycle: float = 0.0

    # Alerts
    total_alerts: int = 0
    alert_latency_s: float = float("nan")

    # Energy (ESTIMATED)
    estimated_energy_j: float = 0.0
    energy_note: str = "Estimated from configurable power profiles; not measured."

    def to_dict(self) -> dict[str, Any]:
        d = asdict(self)
        # Replace NaN with None for JSON
        for k, v in d.items():
            if isinstance(v, float) and math.isnan(v):
                d[k] = None
        return d


def compute_metrics(
    run_dir: Path,
    cfg: dict,
) -> RunMetrics:
    """Compute metrics from a completed run directory.

    Expects:
        run_dir/events.jsonl
        run_dir/ground_truth.jsonl
        run_dir/config_used.json
    """
    events_path = run_dir / "events.jsonl"
    gt_path = run_dir / "ground_truth.jsonl"

    events = load_events(events_path) if events_path.exists() else []
    gt_records = load_events(gt_path) if gt_path.exists() else []

    m = RunMetrics(
        scenario_id=cfg.get("scenario_id", ""),
        run_id=cfg.get("_run_id", ""),
        seed=cfg.get("random_seed", 0),
        duration_s=cfg["simulation"]["duration_s"],
    )

    # --- Ground truth crossings ---
    crossing_times: list[float] = []
    for r in gt_records:
        if r.get("crossed", False):
            t = r.get("timestamp_s", 0)
            if not crossing_times or t != crossing_times[-1]:
                crossing_times.append(t)
    # Deduplicate to first crossing per animal
    unique_crossings: dict[str, float] = {}
    for r in gt_records:
        aid = r.get("animal_id", "")
        if r.get("crossed", False) and aid not in unique_crossings:
            unique_crossings[aid] = r["timestamp_s"]
    m.actual_crossings = len(unique_crossings)

    # --- Controller alerts ---
    alert_events = [e for e in events if e.get("event_type") == EventType.ALERT.value]
    m.total_alerts = len(alert_events)

    # --- Boundary predictions ---
    boundary_preds = [
        e for e in events
        if e.get("event_type") == EventType.BOUNDARY_PREDICTION.value
        and e.get("metadata", {}).get("intersects", False)
    ]
    m.predicted_crossings = len(boundary_preds)

    # --- True positives / false alerts ---
    # An alert is a TP if it occurs within a window around an actual crossing
    alert_window_s = 30.0
    matched_crossings: set[str] = set()
    tp = 0
    fp = 0
    lead_times: list[float] = []

    for ae in alert_events:
        at = ae.get("timestamp_s", 0)
        matched = False
        for aid, ct in unique_crossings.items():
            if aid not in matched_crossings:
                if ct - alert_window_s <= at <= ct + 5.0:
                    tp += 1
                    matched_crossings.add(aid)
                    lead_time = ct - at
                    lead_times.append(lead_time)
                    matched = True
                    break
        if not matched:
            fp += 1

    m.true_positive_detections = tp
    m.false_alerts = fp
    m.missed_crossings = m.actual_crossings - tp
    m.warning_lead_times_s = lead_times
    if lead_times:
        m.mean_warning_lead_time_s = sum(lead_times) / len(lead_times)

    # Recall / precision / F1
    if m.actual_crossings > 0:
        m.crossing_recall = tp / m.actual_crossings
    if m.total_alerts > 0:
        m.crossing_precision = tp / m.total_alerts
    if not math.isnan(m.crossing_recall) and not math.isnan(m.crossing_precision):
        if m.crossing_recall + m.crossing_precision > 0:
            m.f1_score = (2 * m.crossing_recall * m.crossing_precision
                          / (m.crossing_recall + m.crossing_precision))

    # --- Crossing-time prediction error ---
    for bp in boundary_preds:
        pred_eta = bp.get("eta_s")
        bp_t = bp.get("timestamp_s", 0)
        if pred_eta is not None:
            pred_crossing_t = bp_t + pred_eta
            for aid, ct in unique_crossings.items():
                err = abs(pred_crossing_t - ct)
                m.crossing_time_errors_s.append(err)
    if m.crossing_time_errors_s:
        m.mean_crossing_time_error_s = (
            sum(m.crossing_time_errors_s) / len(m.crossing_time_errors_s)
        )

    # --- Camera metrics ---
    cam_events = [e for e in events
                  if e.get("event_type") == EventType.CAMERA_ACTIVATION.value]
    m.camera_activations = len(cam_events)
    cam_cfg = cfg.get("camera", {})
    active_time = m.camera_activations * (
        cam_cfg.get("startup_delay_s", 1.5)
        + cam_cfg.get("capture_latency_s", 0.5)
        + 2.0  # assumed active dwell
    )
    m.camera_duty_cycle = round(active_time / max(m.duration_s, 1), 4)

    # --- Energy estimate ---
    power = cfg.get("power", {})
    n_sensors = len(cfg.get("sensors", {}).get("nodes", []))
    sensor_energy = (
        n_sensors * power.get("sensor_sleep_w", 0.001) * m.duration_s
        + n_sensors * power.get("sensor_active_w", 0.05) * m.duration_s * 0.1
    )
    camera_energy = (
        len(cam_cfg.get("nodes", [])) * power.get("camera_sleep_w", 0.005) * m.duration_s
        + m.camera_activations * power.get("camera_active_w", 2.5) * active_time / max(m.camera_activations, 1)
    )
    gateway_energy = (
        power.get("gateway_idle_w", 0.1) * m.duration_s
        + power.get("gateway_transmit_w", 0.5) * m.total_alerts * 2.0
    )
    m.estimated_energy_j = round(sensor_energy + camera_energy + gateway_energy, 4)

    return m


def save_metrics(m: RunMetrics, run_dir: Path) -> None:
    """Save metrics as JSON and CSV."""
    run_dir.mkdir(parents=True, exist_ok=True)

    with open(run_dir / "metrics.json", "w", encoding="utf-8") as f:
        json.dump(m.to_dict(), f, indent=2)

    with open(run_dir / "metrics.csv", "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(m.to_dict().keys()))
        writer.writeheader()
        row = m.to_dict()
        # Flatten lists for CSV
        for k, v in row.items():
            if isinstance(v, list):
                row[k] = ";".join(str(x) for x in v)
        writer.writerow(row)


def save_experiment_summary(
    all_metrics: list[RunMetrics],
    output_path: Path,
) -> None:
    """Save aggregated CSV across multiple runs."""
    if not all_metrics:
        return
    output_path.parent.mkdir(parents=True, exist_ok=True)
    keys = list(all_metrics[0].to_dict().keys())
    with open(output_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=keys)
        writer.writeheader()
        for m in all_metrics:
            row = m.to_dict()
            for k, v in row.items():
                if isinstance(v, list):
                    row[k] = ";".join(str(x) for x in v)
            writer.writerow(row)
