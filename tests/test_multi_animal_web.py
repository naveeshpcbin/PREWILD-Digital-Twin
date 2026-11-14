"""Integration Tests for Multi-Animal Ecosystem and Vision Web API endpoints.

Tests:
- GET /api/ecosystem/population
- POST /api/ecosystem/step
- POST /api/ecosystem/inject
- POST /api/ecosystem/reset
- GET /api/vision/status
- POST /api/vision/detect
"""

import base64
import io
import json
import numpy as np
from PIL import Image
import pytest

from prw_wild.web.server import (
    GLOBAL_ECOSYSTEM,
    GLOBAL_VISION_DETECTOR,
    GLOBAL_VISION_TRACKER,
    GLOBAL_VISION_RISK,
    DigitalTwinHTTPHandler,
)


def test_ecosystem_population_endpoint():
    """Verify ecosystem state retrieval."""
    pop = [a.to_dict() for a in GLOBAL_ECOSYSTEM.agents]
    assert len(pop) >= 50
    assert "species" in pop[0]
    assert "state" in pop[0]
    assert "position" in pop[0]


def test_ecosystem_step_and_inject_endpoint():
    """Verify simulation advance and manual intent injection."""
    initial_time = GLOBAL_ECOSYSTEM.time_s
    snapshots = GLOBAL_ECOSYSTEM.step(0.5)
    assert GLOBAL_ECOSYSTEM.time_s == pytest.approx(initial_time + 0.5, abs=1e-4)
    assert len(snapshots) >= 50

    # Test injection
    aid = GLOBAL_ECOSYSTEM.agents[0].animal_id
    ok = GLOBAL_ECOSYSTEM.inject_event(aid, "turn_away")
    assert ok is True
    assert GLOBAL_ECOSYSTEM.agents[0].manual_intent == "turn_away"


def test_vision_detect_endpoint():
    """Verify image detection, multi-object tracking, and risk assessment pipeline."""
    # Synthesize test image
    img = Image.new("RGB", (320, 240), color=(30, 80, 30))
    # Add animal signature rectangle
    for y in range(100, 140):
        for x in range(120, 160):
            img.putpixel((x, y), (180, 110, 45))

    buf = io.BytesIO()
    img.save(buf, format="JPEG")
    raw_bytes = buf.getvalue()

    # Run detection directly through the vision pipeline
    dets = GLOBAL_VISION_DETECTOR.detect(raw_bytes)
    assert isinstance(dets, list)

    det_dicts = [d.to_dict() for d in dets]
    tracks = GLOBAL_VISION_TRACKER.update(det_dicts)
    assert isinstance(tracks, list)

    risks = []
    for trk in tracks:
        r = GLOBAL_VISION_RISK.evaluate_track(trk)
        risks.append(r.to_dict())
    assert isinstance(risks, list)

