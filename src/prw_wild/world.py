"""World model — ground-truth animal movement and environment.

This module owns the *hidden* ground truth.  The controller never
imports or reads from this module directly; it receives only the
observations produced by sensor models.
"""

from __future__ import annotations

import math
from dataclasses import dataclass, field
from typing import Optional

from prw_wild.geometry import Point, Segment


# ---------------------------------------------------------------------------
# Animal agent
# ---------------------------------------------------------------------------

@dataclass
class AnimalState:
    """Instantaneous ground-truth state of an animal agent."""
    animal_id: str
    species: str
    position: Point
    velocity: Point  # m/s components
    speed_m_s: float
    waypoint_index: int
    paused: bool = False
    crossed_boundary: bool = False
    crossing_time_s: Optional[float] = None


@dataclass
class AnimalAgent:
    """An animal that follows a waypoint path with optional pauses.

    Movement is interpolated at constant speed between successive
    waypoints.  When the agent reaches the final waypoint it stops.
    """

    animal_id: str
    species: str
    waypoints: list[Point]
    speed_m_s: float
    pause_s: float = 0.0

    # internal state
    _wp_idx: int = field(default=1, init=False)
    _pos: Point = field(default_factory=lambda: Point(0, 0), init=False)
    _vel: Point = field(default_factory=lambda: Point(0, 0), init=False)
    _pause_remaining: float = field(default=0.0, init=False)
    _crossed: bool = field(default=False, init=False)
    _crossing_time: Optional[float] = field(default=None, init=False)

    def __post_init__(self):
        if len(self.waypoints) < 2:
            raise ValueError("Need >= 2 waypoints")
        self._pos = self.waypoints[0]
        self._update_velocity()

    def _update_velocity(self) -> None:
        if self._wp_idx >= len(self.waypoints):
            self._vel = Point(0.0, 0.0)
            return
        target = self.waypoints[self._wp_idx]
        d = self._pos.distance_to(target)
        if d < 1e-6:
            self._advance_waypoint()
            return
        self._vel = Point(
            (target.x - self._pos.x) / d * self.speed_m_s,
            (target.y - self._pos.y) / d * self.speed_m_s,
        )

    def _advance_waypoint(self) -> None:
        self._wp_idx += 1
        if self._wp_idx < len(self.waypoints):
            self._pause_remaining = self.pause_s
            self._update_velocity()
        else:
            self._vel = Point(0.0, 0.0)

    def step(self, dt: float, boundary: Segment) -> AnimalState:
        """Advance by *dt* seconds, check boundary crossing, return state."""
        if self._pause_remaining > 0:
            self._pause_remaining -= dt
            if self._pause_remaining > 0:
                return self._snapshot(paused=True)
            self._pause_remaining = 0.0

        if self._wp_idx >= len(self.waypoints):
            return self._snapshot()

        target = self.waypoints[self._wp_idx]
        d_to_target = self._pos.distance_to(target)
        move_dist = self.speed_m_s * dt

        if move_dist >= d_to_target:
            self._pos = target
            self._advance_waypoint()
        else:
            self._pos = Point(
                self._pos.x + self._vel.x * dt,
                self._pos.y + self._vel.y * dt,
            )
            self._update_velocity()

        # Check boundary crossing (simple: did x cross boundary x for a vertical boundary)
        if not self._crossed:
            self._check_crossing(boundary)

        return self._snapshot()

    def _check_crossing(self, boundary: Segment) -> None:
        """Detect if animal has crossed past the boundary segment.

        For a vertical boundary (common default), checks if x >= boundary x.
        For general segments, checks which side of the directed line the point is on.
        """
        # Cross product of boundary direction with (point - boundary.a)
        bdir_x = boundary.b.x - boundary.a.x
        bdir_y = boundary.b.y - boundary.a.y
        to_pt_x = self._pos.x - boundary.a.x
        to_pt_y = self._pos.y - boundary.a.y
        cross = bdir_x * to_pt_y - bdir_y * to_pt_x
        # Convention: negative cross = crossed to the "farm" side
        if cross < 0:
            self._crossed = True

    def set_crossing_time(self, t: float) -> None:
        if self._crossed and self._crossing_time is None:
            self._crossing_time = t

    @property
    def crossed(self) -> bool:
        return self._crossed

    @property
    def position(self) -> Point:
        return self._pos

    def _snapshot(self, paused: bool = False) -> AnimalState:
        return AnimalState(
            animal_id=self.animal_id,
            species=self.species,
            position=self._pos,
            velocity=self._vel,
            speed_m_s=self.speed_m_s,
            waypoint_index=self._wp_idx,
            paused=paused,
            crossed_boundary=self._crossed,
            crossing_time_s=self._crossing_time,
        )


# ---------------------------------------------------------------------------
# World
# ---------------------------------------------------------------------------

@dataclass
class World:
    """The simulation world — maintains ground-truth state."""

    width_m: float
    height_m: float
    boundary: Segment
    corridors: list[dict]
    animals: list[AnimalAgent]
    time_s: float = 0.0

    @classmethod
    def from_config(cls, cfg: dict) -> "World":
        w = cfg["world"]
        bnd = w["boundary"]
        boundary = Segment(
            Point(*bnd["start"]),
            Point(*bnd["end"]),
        )
        animals = []
        for ac in cfg["animals"]:
            waypoints = [Point(*wp) for wp in ac["waypoints"]]
            animals.append(AnimalAgent(
                animal_id=ac["id"],
                species=ac.get("species", "unknown"),
                waypoints=waypoints,
                speed_m_s=ac["speed_m_s"],
                pause_s=ac.get("pause_s", 0.0),
            ))
        return cls(
            width_m=w["width_m"],
            height_m=w["height_m"],
            boundary=boundary,
            corridors=w.get("corridors", []),
            animals=animals,
        )

    def step(self, dt: float) -> list[AnimalState]:
        """Advance all agents by *dt* seconds, return their states."""
        self.time_s += dt
        states = []
        for animal in self.animals:
            prev_crossed = animal.crossed
            state = animal.step(dt, self.boundary)
            if state.crossed_boundary and not prev_crossed:
                animal.set_crossing_time(self.time_s)
                state = animal._snapshot()  # refresh with crossing time
            states.append(state)
        return states
