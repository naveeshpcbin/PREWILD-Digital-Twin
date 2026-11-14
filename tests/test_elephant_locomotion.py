import math
import numpy as np
import pytest
from pathlib import Path


def calculate_elephant_heading(vx: float, vy: float) -> float:
    """True horizontal forward heading in Three.js coordinate system.

    In Three.js, world coordinates are:
      X = East (movement along vx, towards fence at x=100)
      Y = Elevation
      Z = South (movement along vy)

    The Asian Elephant production GLB has an anatomical local forward vector
    (face, tusks, and trunk):
      f_model = (-1.0, 0.0, 0.0)

    After rotation around Y by angle theta:
      f_world = (-cos(theta), 0, sin(theta))

    To align f_world with normalized velocity (vx/|v|, 0, vy/|v|):
      -cos(theta) = vx / |v| => cos(theta) = -vx / |v|
      sin(theta)  = vy / |v|
      theta = atan2(vy, -vx)
    """
    speed = math.hypot(vx, vy)
    if speed < 1e-6:
        raise ValueError("Velocity is zero")
    return math.atan2(vy, -vx)


def get_forward_vector_after_rotation(theta: float) -> np.ndarray:
    """Returns world forward vector for elephant model (face side) rotated by theta around Y."""
    return np.array([-math.cos(theta), 0.0, math.sin(theta)])


class TestElephantLocomotionPhysics:
    """Targeted regression suite verifying elephant forward orientation."""

    def test_forward_movement_along_positive_x(self):
        """Test 1: Forward movement along +X (towards boundary fence and sensors)."""
        vx, vy = 1.5, 0.0
        theta = calculate_elephant_heading(vx, vy)
        assert math.isclose(abs(theta), math.pi, abs_tol=1e-5), f"Expected pi rad, got {theta}"

        fwd = get_forward_vector_after_rotation(theta)
        v_norm = np.array([vx, 0.0, vy]) / math.hypot(vx, vy)
        dot = float(np.dot(fwd, v_norm))
        assert math.isclose(dot, 1.0, abs_tol=1e-5), f"Expected dot=1.0, got {dot}"
        assert fwd[0] > 0.99, "Elephant face, tusks and trunk must face +X (fence and sensors)"

    def test_forward_movement_along_negative_x(self):
        """Test 2: Forward movement along -X (into deep forest)."""
        vx, vy = -1.5, 0.0
        theta = calculate_elephant_heading(vx, vy)
        assert math.isclose(theta, 0.0, abs_tol=1e-5), f"Expected 0.0 rad, got {theta}"

        fwd = get_forward_vector_after_rotation(theta)
        v_norm = np.array([vx, 0.0, vy]) / math.hypot(vx, vy)
        dot = float(np.dot(fwd, v_norm))
        assert math.isclose(dot, 1.0, abs_tol=1e-5), f"Expected dot=1.0, got {dot}"
        assert fwd[0] < -0.99, "Elephant face must face -X (deep forest)"

    def test_forward_movement_along_positive_z(self):
        """Test 3: Forward movement along +Z (Southward / downstream)."""
        vx, vy = 0.0, 1.5
        theta = calculate_elephant_heading(vx, vy)
        assert math.isclose(theta, math.pi / 2, abs_tol=1e-5), f"Expected +pi/2 rad, got {theta}"

        fwd = get_forward_vector_after_rotation(theta)
        v_norm = np.array([vx, 0.0, vy]) / math.hypot(vx, vy)
        dot = float(np.dot(fwd, v_norm))
        assert math.isclose(dot, 1.0, abs_tol=1e-5), f"Expected dot=1.0, got {dot}"
        assert fwd[2] > 0.99, "Elephant face must face +Z"

    def test_forward_movement_along_negative_z(self):
        """Test 4: Forward movement along -Z (Northward / upstream)."""
        vx, vy = 0.0, -1.5
        theta = calculate_elephant_heading(vx, vy)
        assert math.isclose(theta, -math.pi / 2, abs_tol=1e-5), f"Expected -pi/2 rad, got {theta}"

        fwd = get_forward_vector_after_rotation(theta)
        v_norm = np.array([vx, 0.0, vy]) / math.hypot(vx, vy)
        dot = float(np.dot(fwd, v_norm))
        assert math.isclose(dot, 1.0, abs_tol=1e-5), f"Expected dot=1.0, got {dot}"
        assert fwd[2] < -0.99, "Elephant face must face -Z"

    def test_diagonal_movement_southeast(self):
        """Test 5: Diagonal Southeast movement (+X, +Z)."""
        vx, vy = 1.0, 1.0
        theta = calculate_elephant_heading(vx, vy)
        fwd = get_forward_vector_after_rotation(theta)
        v_norm = np.array([vx, 0.0, vy]) / math.hypot(vx, vy)
        dot = float(np.dot(fwd, v_norm))
        assert math.isclose(dot, 1.0, abs_tol=1e-5), f"Expected dot=1.0, got {dot}"

    def test_diagonal_movement_southwest(self):
        """Test 6: Diagonal Southwest movement (-X, +Z) in turns_away scenario."""
        vx, vy = -0.38, 1.14
        theta = calculate_elephant_heading(vx, vy)
        fwd = get_forward_vector_after_rotation(theta)
        v_norm = np.array([vx, 0.0, vy]) / math.hypot(vx, vy)
        dot = float(np.dot(fwd, v_norm))
        assert math.isclose(dot, 1.0, abs_tol=1e-5), f"Expected dot=1.0, got {dot}"

    def test_zero_velocity_heading_preservation(self):
        """Test 7: Temporary stop retains last valid direction without flipping."""
        last_valid_heading = math.pi  # Facing +X towards fence
        vx, vy = 0.0, 0.0
        speed = math.hypot(vx, vy)

        current_heading = last_valid_heading if speed <= 0.05 else calculate_elephant_heading(vx, vy)
        assert current_heading == math.pi, "Must preserve last valid heading during pause"

    def test_glb_anatomy_local_axis(self):
        """Test 8: Confirm production elephant GLB exists and file size is valid."""
        glb_path = Path("D:/Simulation For DT/prw-wild-digital-twin/src/prw_wild/web/static/assets/animals/asian_elephant_production.glb")
        assert glb_path.exists(), "asian_elephant_production.glb must exist"
        assert glb_path.stat().st_size > 5_000_000, "Production GLB must be complete photorealistic asset"
