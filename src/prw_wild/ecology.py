"""Ecological / contextual prior.

Provides a simple spatial weight based on configured approach corridors.
This is a *static heuristic*, not live satellite tracking.

When disabled or no corridors are defined, returns a neutral prior (0.5).
"""

from __future__ import annotations

from prw_wild.geometry import Point


class EcologyPrior:
    """Static corridor-based ecological prior."""

    def __init__(self, cfg: dict):
        eco = cfg.get("ecology", {})
        self.enabled: bool = eco.get("enabled", False)
        self.corridor_boost: float = eco.get("corridor_boost", 0.15)
        self.neutral: float = eco.get("neutral_prior", 0.5)
        self.corridors: list[dict] = cfg.get("world", {}).get("corridors", [])

    def evaluate(self, position: Point) -> float:
        """Return ecological prior at *position*.  In [0, 1]."""
        if not self.enabled or not self.corridors:
            return self.neutral

        best_boost = 0.0
        for c in self.corridors:
            cy = c.get("center_y_m", 0)
            w = c.get("width_m", 1)
            weight = c.get("weight", 1.0)
            dy = abs(position.y - cy)
            if dy < w / 2:
                # Inside corridor — boost proportional to centrality
                centrality = 1.0 - (dy / (w / 2))
                boost = self.corridor_boost * centrality * weight
                best_boost = max(best_boost, boost)

        return min(1.0, self.neutral + best_boost)
