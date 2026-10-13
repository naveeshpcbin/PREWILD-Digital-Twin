"""CSI replay adapter — future real-data integration point.

This module defines the adapter interface for replaying real Wi-Fi CSI
recordings through the PRW-Wild observation pipeline.

STATUS: Interface definition only.  No real CSI data is processed.
Real CSI integration requires:
  - A separately trained CSI classifier or feature extractor.
  - Timestamped CSI sample files (e.g., from ESP32-CSI-Tool).
  - Calibration against physical deployment geometry.

The rest of the PRW-Wild architecture operates without this adapter.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from pathlib import Path
from typing import Iterator, Optional


@dataclass
class CSIObservation:
    """A single CSI-derived observation.

    Fields mirror the observation interface used by the fusion module.
    """
    timestamp_s: float
    sensor_id: str
    disturbance_score: float        # [0, 1] — classifier output
    confidence: float               # model confidence
    estimated_position_xy: Optional[list[float]] = None
    measurement_uncertainty: Optional[float] = None
    provenance: str = "csi_replay"
    raw_features: Optional[dict] = None


class CSIReplayAdapter(ABC):
    """Abstract adapter for real CSI data replay.

    Subclass this to integrate actual CSI recordings.
    """

    @abstractmethod
    def load(self, path: Path) -> None:
        """Load CSI sample file(s) from *path*."""
        ...

    @abstractmethod
    def observations(self) -> Iterator[CSIObservation]:
        """Yield timestamped CSI observations in chronological order."""
        ...

    @abstractmethod
    def reset(self) -> None:
        """Reset replay to the beginning."""
        ...


class SyntheticCSIAdapter(CSIReplayAdapter):
    """Placeholder adapter that produces no observations.

    Used as the default when no real CSI data is available.
    """

    def load(self, path: Path) -> None:
        pass  # No-op

    def observations(self) -> Iterator[CSIObservation]:
        return iter([])  # Empty

    def reset(self) -> None:
        pass
