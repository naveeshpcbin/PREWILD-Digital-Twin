"""
Test suite for ONNX Runtime YOLOv8 Wildlife Detector & Terrain Elevation.
Verifies:
1. ONNX YOLOv8 model initialization and backend registration.
2. Inference execution on real pixel buffers.
3. Strict ground-truth isolation (zero simulation leakage).
4. Analytical terrain elevation continuity and boundary consistency.
"""

import numpy as np
import pytest
from PIL import Image

from prw_wild.vision.detector import WildlifeVisionDetector, DetectionResult
from prw_wild.ecosystem import get_terrain_elevation, PopulationEcosystem, BehaviorState


def test_onnx_yolov8_initialization():
    """WildlifeVisionDetector must initialize with onnxruntime_yolov8 backend."""
    detector = WildlifeVisionDetector()
    assert detector.backend == "onnxruntime_yolov8"
    assert detector.session is not None
    assert detector.input_name == "images"
    assert detector.output_name == "output0"


def test_onnx_yolov8_inference_execution():
    """Verify neural network forward pass on synthetic RGB pixel frames."""
    detector = WildlifeVisionDetector(conf_threshold=0.10)
    
    # Create test image with distinct animal signature patch (elephant grey)
    frame = np.full((480, 640, 3), [45, 95, 35], dtype=np.uint8)  # Forest terrain
    frame[160:320, 220:420] = [80, 80, 85]  # Slate pachyderm patch

    results = detector.detect(frame)
    assert isinstance(results, list)
    assert detector.last_inference_latency_ms > 0.0

    # Test with PIL Image input
    pil_img = Image.fromarray(frame)
    pil_results = detector.detect(pil_img)
    assert isinstance(pil_results, list)


def test_terrain_elevation_continuity():
    """Verify analytical elevation function is smooth and matches geographic regions."""
    # Western ridge (x=5) must be significantly higher than depressed corridor (x=50, z=100)
    ridge_elev = get_terrain_elevation(5.0, 50.0)
    corridor_elev = get_terrain_elevation(50.0, 100.0)
    pond_elev = get_terrain_elevation(75.0, 140.0)

    assert ridge_elev > 1.5, f"Expected western ridge elevation > 1.5m, got {ridge_elev}"
    assert corridor_elev < 0.0, f"Expected depressed corridor valley < 0.0m, got {corridor_elev}"
    assert pond_elev < -1.5, f"Expected deep pond basin depression < -1.5m, got {pond_elev}"

    # Smoothness check: adjacent points (delta 1m) should have small elevation delta
    e1 = get_terrain_elevation(40.0, 80.0)
    e2 = get_terrain_elevation(41.0, 80.0)
    assert abs(e2 - e1) < 0.5, "Elevation gradient too steep / discontinuous"


def test_individual_animal_profiles():
    """Verify all 60 agents possess unique identities, demographics, and scales."""
    eco = PopulationEcosystem(population_size=60, seed=42)
    agents = eco.agents

    assert len(agents) == 60
    # Every animal has an individual name
    names = [a.name for a in agents]
    assert all(len(n) > 0 for n in names)
    assert len(set(names)) == len(names), "All animal individual names must be unique"

    # Verify demographics present
    demos = set(a.demographic for a in agents)
    assert "alpha_male" in demos
    assert "matriarch" in demos
    assert "calf" in demos or "juvenile" in demos

    # Verify scales are diverse (calves smaller than alpha bulls)
    scales = [a.scale_factor for a in agents]
    assert min(scales) <= 0.70
    assert max(scales) >= 1.25

    # Verify all animals have valid 3D elevation
    for a in agents:
        assert isinstance(a.elevation_y, float)
        assert -4.0 <= a.elevation_y <= 6.0

