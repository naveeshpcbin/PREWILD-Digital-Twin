"""Experiment runner — the main simulation loop.

Orchestrates world, sensors, fusion, tracker, risk engine, camera
gate/emulator, alert engine, and logging for one simulation run.
"""

from __future__ import annotations

import json
import random
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from prw_wild.config import load_config, save_config
from prw_wild.world import World, AnimalState
from prw_wild.geometry import Point, Segment, estimate_eta, BoundaryIntersection
from prw_wild.sensor_models import (
    SensorNode, SensorParams,
    build_sensor_nodes, get_sensor_params, generate_observation,
)
from prw_wild.fusion import SensorFusion
from prw_wild.tracker import Tracker
from prw_wild.ecology import EcologyPrior
from prw_wild.risk_engine import RiskEngine
from prw_wild.camera_gate import CameraGate, CameraEmulator
from prw_wild.alert_engine import AlertEngine
from prw_wild.dispatch import AlertRouter
from prw_wild.event_log import (
    Event, EventType, EventLogger, GroundTruthLogger, RiskLevel,
)
from prw_wild.metrics import compute_metrics, save_metrics, RunMetrics


def run_experiment(
    cfg: dict,
    output_dir: Path | None = None,
    seed_override: int | None = None,
) -> tuple[RunMetrics, Path]:
    """Execute one complete simulation run.

    Returns (metrics, run_dir).
    """
    # --- Setup ---
    seed = seed_override if seed_override is not None else cfg["random_seed"]
    rng = random.Random(seed)
    run_id = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S") + "_" + uuid.uuid4().hex[:6]
    scenario_id = cfg["scenario_id"]

    if output_dir is None:
        output_dir = Path("outputs/runs") / run_id
    run_dir = output_dir
    run_dir.mkdir(parents=True, exist_ok=True)

    cfg["_run_id"] = run_id
    save_config(cfg, run_dir / "config_used.json")

    # --- Initialise components ---
    world = World.from_config(cfg)
    boundary = world.boundary

    sensor_nodes = build_sensor_nodes(cfg)
    sensor_params: dict[str, SensorParams] = {}
    for stype in ("rf_csi", "pir", "vibration", "acoustic"):
        sensor_params[stype] = get_sensor_params(cfg, stype)

    fusion = SensorFusion(cfg)
    tracker = Tracker(cfg)
    ecology = EcologyPrior(cfg)
    risk_engine = RiskEngine(cfg)
    camera_gate = CameraGate(cfg)
    camera_emulator = CameraEmulator(cfg)
    alert_engine = AlertEngine(cfg)
    alert_router = AlertRouter()
    breach_confirmed = False

    # Policy override
    policy = cfg.get("policies", {}).get("active", "predictive")

    dt = cfg["simulation"]["time_step_s"]
    duration = cfg["simulation"]["duration_s"]
    n_steps = int(duration / dt)

    # --- Loggers ---
    event_logger = EventLogger(run_dir / "events.jsonl", scenario_id, run_id)
    gt_logger = GroundTruthLogger(run_dir / "ground_truth.jsonl", scenario_id, run_id)

    # System start event
    event_logger.log(Event(
        timestamp_s=0.0,
        event_type=EventType.SYSTEM.value,
        provenance="system",
        metadata={"action": "simulation_start", "seed": seed, "policy": policy},
    ))

    # --- Main loop ---
    camera_result_str = ""
    for step_i in range(n_steps):
        t = round(step_i * dt, 4)

        # 1. World step — ground truth
        animal_states = world.step(dt)
        for state in animal_states:
            gt_logger.log(
                timestamp_s=t,
                animal_id=state.animal_id,
                true_x=state.position.x,
                true_y=state.position.y,
                true_vx=state.velocity.x,
                true_vy=state.velocity.y,
                crossed=state.crossed_boundary,
                metadata={
                    "wp_idx": state.waypoint_index,
                    "crossing_time_s": state.crossing_time_s,
                },
            )

        # For single-animal scenarios, use the first animal
        animal = animal_states[0]

        # 2. Sensor observations (use ground truth internally)
        for node in sensor_nodes:
            if policy == "rf_only" and node.sensor_type != "rf_csi":
                continue
            if policy == "pir_only" and node.sensor_type != "pir":
                continue
            params = sensor_params[node.sensor_type]
            obs = generate_observation(
                node=node,
                params=params,
                true_position=animal.position,
                true_speed=animal.speed_m_s,
                time_s=t,
                dt=dt,
                rng=rng,
                scenario_id=scenario_id,
                run_id=run_id,
            )
            if obs is not None:
                event_logger.log(obs)
                # Feed to fusion
                fusion.add_observation(
                    timestamp_s=obs.timestamp_s,
                    sensor_type=node.sensor_type,
                    score=obs.score,
                    estimated_position_xy=obs.estimated_position_xy,
                    measurement_uncertainty=obs.measurement_uncertainty,
                )

        # 3. Sensor fusion
        eco_val = ecology.evaluate(
            tracker._build_state(t).position if tracker.is_initialised
            else Point(0, 0)
        )
        fused = fusion.fuse(t, eco_prior=eco_val)

        if fused.fused_confidence >= fusion.min_confidence:
            event_logger.log(Event(
                timestamp_s=t,
                event_type=EventType.FUSION_RESULT.value,
                confidence=fused.fused_confidence,
                estimated_position_xy=fused.estimated_position_xy,
                measurement_uncertainty=fused.position_uncertainty,
                provenance=fused.provenance,
                metadata={"contributing": fused.contributing_sensors},
            ))

        # 4. Tracker update
        track_state = tracker.predict(t)
        if fused.estimated_position_xy is not None and fused.fused_confidence >= fusion.min_confidence:
            track_state = tracker.update(
                t,
                fused.estimated_position_xy[0],
                fused.estimated_position_xy[1],
                fused.position_uncertainty,
            )
            event_logger.log(Event(
                timestamp_s=t,
                event_type=EventType.TRACK_UPDATE.value,
                estimated_position_xy=[track_state.estimated_x, track_state.estimated_y],
                measurement_uncertainty=track_state.position_uncertainty,
                confidence=track_state.track_confidence,
                provenance="kalman_tracker",
                metadata={
                    "vx": track_state.estimated_vx,
                    "vy": track_state.estimated_vy,
                    "obs_count": track_state.observation_count,
                    "stale": track_state.stale,
                },
            ))

        # 5. Boundary prediction
        boundary_pred = BoundaryIntersection(intersects=False)
        if track_state.is_valid:
            boundary_pred = estimate_eta(
                track_state.position,
                track_state.velocity,
                boundary,
            )
            if boundary_pred.intersects:
                event_logger.log(Event(
                    timestamp_s=t,
                    event_type=EventType.BOUNDARY_PREDICTION.value,
                    predicted_crossing_xy=(
                        [round(boundary_pred.point.x, 2),
                         round(boundary_pred.point.y, 2)]
                        if boundary_pred.point else None
                    ),
                    eta_s=round(boundary_pred.time_s, 2) if boundary_pred.time_s else None,
                    confidence=track_state.track_confidence,
                    provenance="geometric_prediction",
                    metadata={
                        "distance_m": round(boundary_pred.distance_m, 2) if boundary_pred.distance_m else None,
                        "intersects": True,
                    },
                ))

        # 6. Risk assessment
        risk = risk_engine.evaluate(
            timestamp_s=t,
            fused_confidence=fused.fused_confidence,
            track=track_state,
            boundary_pred=boundary_pred,
            eco_prior=eco_val,
        )
        if risk.risk_level != risk.previous_level:
            event_logger.log(Event(
                timestamp_s=t,
                event_type=EventType.RISK_CHANGE.value,
                risk_level=risk.risk_level.value,
                score=risk.risk_score,
                provenance="risk_engine",
                metadata={
                    "previous": risk.previous_level.value,
                    "components": risk.components,
                    "reason": risk.reason,
                },
            ))

        # 7. Camera gate
        camera_gate.step(t)

        if policy == "always_on":
            # Always-on: activate camera every step if not already active
            for cam in camera_gate.cameras:
                if cam.state == "sleep":
                    camera_gate.activate(cam, t, "always_on_policy")
                    event_logger.log(Event(
                        timestamp_s=t,
                        event_type=EventType.CAMERA_ACTIVATION.value,
                        camera_id=cam.camera_id,
                        provenance="always_on_policy",
                    ))
        elif policy == "pir_only":
            # PIR-only: activate if any PIR triggered recently
            pir_obs = [
                obs for obs in fusion._buffer.get("pir", [])
                if obs[0] >= t - 2.0  # within 2s
            ]
            if pir_obs:
                cam = camera_gate.should_activate(
                    risk.risk_score, risk.risk_level,
                    fused.fused_confidence, t,
                )
                if cam is None:
                    # Force activate regardless of risk for PIR-only
                    for c in camera_gate.cameras:
                        if c.state == "sleep":
                            elapsed = t - c.last_activation_s
                            if elapsed >= camera_gate.cooldown_s:
                                cam = c
                                break
                if cam:
                    camera_gate.activate(cam, t, "pir_only_policy")
                    event_logger.log(Event(
                        timestamp_s=t,
                        event_type=EventType.CAMERA_ACTIVATION.value,
                        camera_id=cam.camera_id,
                        provenance="pir_only_policy",
                    ))
        elif policy == "rf_only":
            # RF-only: activate when RF CSI observes disturbance
            rf_obs = [
                obs for obs in fusion._buffer.get("rf_csi", [])
                if obs[0] >= t - 2.5
            ]
            if rf_obs:
                cam = camera_gate.should_activate(
                    risk.risk_score, risk.risk_level,
                    fused.fused_confidence, t,
                )
                if cam is None:
                    for c in camera_gate.cameras:
                        if c.state == "sleep":
                            elapsed = t - c.last_activation_s
                            if elapsed >= camera_gate.cooldown_s:
                                cam = c
                                break
                if cam:
                    camera_gate.activate(cam, t, "rf_only_policy")
                    event_logger.log(Event(
                        timestamp_s=t,
                        event_type=EventType.CAMERA_ACTIVATION.value,
                        camera_id=cam.camera_id,
                        provenance="rf_only_policy",
                    ))
        else:
            # Predictive policy
            cam = camera_gate.should_activate(
                risk.risk_score, risk.risk_level,
                fused.fused_confidence, t,
            )
            if cam:
                camera_gate.activate(cam, t, risk.reason)
                event_logger.log(Event(
                    timestamp_s=t,
                    event_type=EventType.CAMERA_ACTIVATION.value,
                    camera_id=cam.camera_id,
                    score=risk.risk_score,
                    risk_level=risk.risk_level.value,
                    provenance="predictive_gate",
                    metadata={"reason": risk.reason},
                ))

        # 8. Camera emulator — capture when active
        for cam in camera_gate.cameras:
            if cam.state == "active":
                cap_event = camera_emulator.capture(
                    cam=cam,
                    true_position=animal.position,
                    true_species=animal.species,
                    current_time_s=t,
                    rng=rng,
                    scenario_id=scenario_id,
                    run_id=run_id,
                )
                if cap_event:
                    event_logger.log(cap_event)
                    camera_result_str = cap_event.classification
                # Deactivate after capture
                camera_gate.deactivate(cam, t)

        # 9. Alert engine
        alert_ev = alert_engine.evaluate(
            timestamp_s=t,
            risk_score=risk.risk_score,
            risk_level=risk.risk_level,
            estimated_position=(
                [track_state.estimated_x, track_state.estimated_y]
                if track_state.is_valid else None
            ),
            predicted_crossing=(
                [round(boundary_pred.point.x, 2), round(boundary_pred.point.y, 2)]
                if boundary_pred.intersects and boundary_pred.point else None
            ),
            eta_s=(
                round(boundary_pred.time_s, 2)
                if boundary_pred.intersects and boundary_pred.time_s else None
            ),
            sensor_evidence=fused.contributing_sensors,
            camera_result=camera_result_str,
        )
        if alert_ev:
            event_logger.log(alert_ev)
            det_ev = alert_engine.last_deterrent_event
            if det_ev:
                event_logger.log(det_ev)

            # Inferred species from operational sensors (optical classification if verified, else candidate prior)
            inferred_species = (
                camera_result_str
                if (camera_result_str and camera_result_str not in ("no_detection", "not_in_fov", "capture_failed"))
                else "ESTIMATED_MEGAFAUNA"
            )

            # Route approach warning dispatches
            warning_dispatches = alert_router.route_alert(
                alert_id=alert_ev.event_id,
                timestamp_s=t,
                severity=alert_ev.risk_level or "WARNING",
                estimated_position=alert_ev.estimated_position_xy,
                eta_s=alert_ev.eta_s,
                species=inferred_species,
                risk_score=alert_ev.score,
            )
            for d in warning_dispatches:
                event_logger.log(Event(
                    timestamp_s=t,
                    event_type=EventType.DISPATCH.value,
                    event_id=d.dispatch_id,
                    score=alert_ev.score,
                    risk_level=alert_ev.risk_level,
                    provenance="alert_dispatch_service",
                    metadata=d.to_dict(),
                ))

        # 10. Boundary breach detection & escalation (Operational Controller — Ground-Truth Isolated)
        # The controller detects a breach strictly via its own estimated track or corroborating perimeter sensor observations.
        is_breach = False
        if track_state.is_valid and track_state.estimated_x >= (boundary.a.x - 2.0) and track_state.track_confidence > 0.25:
            is_breach = True
        elif (
            fused.estimated_position_xy is not None
            and fused.estimated_position_xy[0] >= (boundary.a.x - 2.0)
            and fused.fused_confidence >= 0.65
        ):
            is_breach = True

        if is_breach and not breach_confirmed:
            breach_confirmed = True
            if track_state.is_valid:
                est_pos = [track_state.estimated_x, track_state.estimated_y]
                breach_conf = track_state.track_confidence
            elif fused.estimated_position_xy is not None:
                est_pos = fused.estimated_position_xy
                breach_conf = fused.fused_confidence
            else:
                est_pos = [boundary.a.x, 100.0]
                breach_conf = 0.75

            inferred_species = (
                camera_result_str
                if (camera_result_str and camera_result_str not in ("no_detection", "not_in_fov", "capture_failed"))
                else "ESTIMATED_MEGAFAUNA"
            )

            breach_event = Event(
                timestamp_s=t,
                event_type=EventType.BOUNDARY_BREACH.value,
                event_id=uuid.uuid4().hex[:12],
                risk_level=RiskLevel.BREACH.value,
                score=1.0,
                estimated_position_xy=est_pos,
                confidence=breach_conf,
                provenance="controller_boundary_monitor",
                metadata={
                    "status": "BREACH_CONFIRMED",
                    "boundary_x": boundary.a.x,
                    "species": inferred_species,
                    "action": "activate_laptop_siren_and_escalate_dispatch",
                },
            )
            event_logger.log(breach_event)

            # Escalate dispatch to all nearby residents and authorities
            critical_dispatches = alert_router.route_alert(
                alert_id=breach_event.event_id,
                timestamp_s=t,
                severity="CRITICAL_BREACH",
                estimated_position=est_pos,
                eta_s=0.0,
                species=inferred_species,
                risk_score=1.0,
            )
            for d in critical_dispatches:
                event_logger.log(Event(
                    timestamp_s=t,
                    event_type=EventType.DISPATCH.value,
                    event_id=d.dispatch_id,
                    score=1.0,
                    risk_level=RiskLevel.BREACH.value,
                    provenance="alert_dispatch_service",
                    metadata=d.to_dict(),
                ))

    # --- End simulation ---
    event_logger.log(Event(
        timestamp_s=round(n_steps * dt, 4),
        event_type=EventType.SYSTEM.value,
        provenance="system",
        metadata={"action": "simulation_end"},
    ))
    event_logger.close()
    gt_logger.close()

    # Save dispatches
    dispatches_data = [d.to_dict() for d in alert_router.history]
    with open(run_dir / "dispatches.json", "w", encoding="utf-8") as f:
        json.dump(dispatches_data, f, indent=2)

    # --- Compute and save metrics ---
    metrics = compute_metrics(run_dir, cfg)
    save_metrics(metrics, run_dir)

    # --- Summary markdown ---
    _write_summary(metrics, run_dir, cfg)

    # --- Run metadata ---
    meta = {
        "run_id": run_id,
        "scenario_id": scenario_id,
        "seed": seed,
        "policy": policy,
        "started_at": datetime.now(timezone.utc).isoformat(),
        "duration_s": duration,
        "events_logged": event_logger.count,
    }
    with open(run_dir / "run_metadata.json", "w", encoding="utf-8") as f:
        json.dump(meta, f, indent=2)

    return metrics, run_dir


def _write_summary(m: RunMetrics, run_dir: Path, cfg: dict) -> None:
    lines = [
        f"# PRW-Wild Run Summary",
        f"",
        f"**Scenario:** {m.scenario_id}",
        f"**Run ID:** {m.run_id}",
        f"**Seed:** {m.seed}",
        f"**Policy:** {cfg.get('policies', {}).get('active', 'predictive')}",
        f"**Duration:** {m.duration_s}s",
        f"",
        f"## Detection Performance",
        f"| Metric | Value |",
        f"|--------|-------|",
        f"| Actual crossings | {m.actual_crossings} |",
        f"| Predicted crossings | {m.predicted_crossings} |",
        f"| True positive detections | {m.true_positive_detections} |",
        f"| False alerts | {m.false_alerts} |",
        f"| Missed crossings | {m.missed_crossings} |",
        f"| Crossing recall | {_fmt(m.crossing_recall)} |",
        f"| Crossing precision | {_fmt(m.crossing_precision)} |",
        f"| F1 score | {_fmt(m.f1_score)} |",
        f"",
        f"## Timing",
        f"| Metric | Value |",
        f"|--------|-------|",
        f"| Mean warning lead time | {_fmt(m.mean_warning_lead_time_s)} s |",
        f"| Mean crossing time error | {_fmt(m.mean_crossing_time_error_s)} s |",
        f"",
        f"## Camera & Energy",
        f"| Metric | Value |",
        f"|--------|-------|",
        f"| Camera activations | {m.camera_activations} |",
        f"| Camera duty cycle | {_fmt(m.camera_duty_cycle)} |",
        f"| Total alerts | {m.total_alerts} |",
        f"| Estimated energy (J) | {m.estimated_energy_j} |",
        f"",
        f"> **Note:** All metrics are from a synthetic simulation.",
        f"> Energy values are *estimated*, not measured.",
        f"> Sensor models are phenomenological assumptions.",
    ]
    with open(run_dir / "summary.md", "w", encoding="utf-8") as f:
        f.write("\n".join(lines))


def _fmt(v: float) -> str:
    import math
    if v is None or (isinstance(v, float) and math.isnan(v)):
        return "N/A"
    return f"{v:.4f}"
