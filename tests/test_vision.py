"""Unit and Integration Tests for Computer Vision, Tracking, and Risk Pipeline.

Verifies:
- Species class mapping and registry
- Visual detection on RGB image arrays
- Multi-object tracking (SORT) identity assignment (zero ground-truth leakage)
- Independent visual boundary crossing risk estimation
- Honest uncalibrated confidence labeling
"""

import numpy as np
import pytest
from prw_wild.vision import (
    WildlifeVisionDetector,
    MultiObjectTracker,
    VisualRiskEstimator,
    TARGET_CLASSES,
    map_detection_class,
)


def test_target_classes_and_mapping():
    """Verify target classes exist and mapping functions correctly."""
    assert 0 in TARGET_CLASSES  # Asian elephant
    assert 1 in TARGET_CLASSES  # Chital deer
    assert 3 in TARGET_CLASSES  # Wild boar
    assert 6 in TARGET_CLASSES  # Unknown animal

    # Direct mapping checks
    assert map_detection_class(20, "elephant").class_id == 0
    assert map_detection_class(17, "deer").class_id == 1
    assert map_detection_class(19, "wild boar").class_id == 3
    assert map_detection_class(99, "bicycle").class_id == 6  # Unknown animal fallback


def test_vision_detector_execution():
    """WildlifeVisionDetector must process real RGB pixel arrays."""
    detector = WildlifeVisionDetector()
    assert detector.backend in ("onnxruntime_yolov8", "ultralytics_yolo", "spatial_cv_pixel_engine")

    # Create synthetic frame with animal patch
    frame = np.full((480, 640, 3), [50, 110, 45], dtype=np.uint8)  # Forest green
    frame[200:260, 250:330] = [180, 100, 50]  # Amber-tawny deer patch

    dets = detector.detect(frame)
    assert isinstance(dets, list)
    if len(dets) > 0:
        d = dets[0]
        assert len(d.bbox) == 4
        assert d.bbox[2] > d.bbox[0]
        assert d.bbox[3] > d.bbox[1]
        assert 0.0 <= d.confidence <= 1.0
        assert not d.is_calibrated
        assert d.to_dict()["confidence_label"] == "RAW (NOT CALIBRATED)"


def test_multi_object_tracker_identity_isolation():
    """Tracker must maintain independent integer track IDs without ground truth entity IDs."""
    tracker = MultiObjectTracker(max_age=3, min_hits=1)

    # Frame 1: Animal detected at (100, 100, 150, 150)
    det_f1 = [{
        "bbox": [100.0, 100.0, 150.0, 150.0],
        "class_id": 0,
        "class_name": "asian_elephant",
        "confidence": 0.85
    }]
    tracks_f1 = tracker.update(det_f1)
    assert len(tracks_f1) == 1
    t1_id = tracks_f1[0]["track_id"]
    assert isinstance(t1_id, int)

    # Frame 2: Animal moves slightly to (105, 102, 155, 152)
    det_f2 = [{
        "bbox": [105.0, 102.0, 155.0, 152.0],
        "class_id": 0,
        "class_name": "asian_elephant",
        "confidence": 0.88
    }]
    tracks_f2 = tracker.update(det_f2)
    assert len(tracks_f2) == 1
    assert tracks_f2[0]["track_id"] == t1_id, "Track ID must remain persistent across frames"


def test_visual_risk_estimation():
    """Risk estimator calculates independent crossing risk from visual track vectors."""
    risk_est = VisualRiskEstimator(boundary_pixel_x=500.0)

    # Track moving towards boundary (positive velocity)
    track_approaching = {
        "track_id": 101,
        "class_name": "asian_elephant",
        "confidence": 0.90,
        "bbox": [420.0, 200.0, 480.0, 280.0],
        "velocity_px": [4.0, 0.5]
    }
    risk = risk_est.evaluate_track(track_approaching)
    assert risk.trajectory_intersects_boundary is True
    assert risk.crossing_risk_score > 0.4
    assert risk.eta_seconds is not None
    assert risk.eta_seconds > 0

    # Track moving away from boundary (negative velocity)
    track_fleeing = {
        "track_id": 102,
        "class_name": "chital_deer",
        "confidence": 0.80,
        "bbox": [300.0, 200.0, 340.0, 250.0],
        "velocity_px": [-3.0, 0.0]
    }
    risk_fleeing = risk_est.evaluate_track(track_fleeing)
    assert risk_fleeing.trajectory_intersects_boundary is False
    assert risk_fleeing.crossing_risk_score < risk.crossing_risk_score

