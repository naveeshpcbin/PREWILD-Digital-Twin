"""Multi-Object Wildlife Tracker for PRW-Wild.

Implements SORT (Simple Online and Realtime Tracking) with Kalman filtering
and Intersection-over-Union (IoU) spatial association.

Maintains track identities derived purely from visual detection bounding boxes,
with STRICT ZERO ACCESS to hidden simulation entity IDs or ground-truth coordinates.
"""

from __future__ import annotations

import math
from dataclasses import dataclass, field
from typing import List, Dict, Tuple, Optional, Any, ClassVar
import numpy as np


def iou_batch(bb_test: np.ndarray, bb_gt: np.ndarray) -> np.ndarray:
    """Compute IoU between two arrays of bounding boxes [x1, y1, x2, y2]."""
    bb_gt = np.expand_dims(bb_gt, 0)
    bb_test = np.expand_dims(bb_test, 1)

    xx1 = np.maximum(bb_test[..., 0], bb_gt[..., 0])
    yy1 = np.maximum(bb_test[..., 1], bb_gt[..., 1])
    xx2 = np.minimum(bb_test[..., 2], bb_gt[..., 2])
    yy2 = np.minimum(bb_test[..., 3], bb_gt[..., 3])

    w = np.maximum(0.0, xx2 - xx1)
    h = np.maximum(0.0, yy2 - yy1)
    wh = w * h

    o = wh / (
        (bb_test[..., 2] - bb_test[..., 0]) * (bb_test[..., 3] - bb_test[..., 1])
        + (bb_gt[..., 2] - bb_gt[..., 0]) * (bb_gt[..., 3] - bb_gt[..., 1])
        - wh + 1e-8
    )
    return o


@dataclass
class KalmanBoxTracker:
    """Kalman filter state for a single tracked animal bounding box."""
    count: ClassVar[int] = 0
    bbox: np.ndarray  # [x1, y1, x2, y2]
    class_id: int
    class_name: str
    confidence: float
    time_since_update: int = 0
    hits: int = 1
    hit_streak: int = 1
    age: int = 0
    history: List[Tuple[float, float]] = field(default_factory=list)
    velocity: Tuple[float, float] = (0.0, 0.0)

    # 1D/2D Kalman state: [u, v, s, r, du, dv, ds]
    x: np.ndarray = field(init=False)
    P: np.ndarray = field(init=False)
    F: np.ndarray = field(init=False)
    H: np.ndarray = field(init=False)
    Q: np.ndarray = field(init=False)
    R: np.ndarray = field(init=False)

    def __post_init__(self):
        KalmanBoxTracker.count += 1
        self.track_id = KalmanBoxTracker.count

        # Convert bbox to [u, v, s, r]
        w = max(1.0, self.bbox[2] - self.bbox[0])
        h = max(1.0, self.bbox[3] - self.bbox[1])
        u = self.bbox[0] + w / 2.0
        v = self.bbox[1] + h / 2.0
        s = w * h
        r = w / float(h)

        self.x = np.array([u, v, s, r, 0.0, 0.0, 0.0], dtype=float)
        self.P = np.diag([10.0, 10.0, 10.0, 10.0, 100.0, 100.0, 100.0])
        
        # State transition
        self.F = np.eye(7)
        self.F[0, 4] = 1.0  # u += du
        self.F[1, 5] = 1.0  # v += dv
        self.F[2, 6] = 1.0  # s += ds

        # Measurement matrix (observes u, v, s, r)
        self.H = np.zeros((4, 7))
        self.H[0, 0] = 1.0
        self.H[1, 1] = 1.0
        self.H[2, 2] = 1.0
        self.H[3, 3] = 1.0

        # Process & Measurement noise
        self.Q = np.diag([1.0, 1.0, 1.0, 1.0, 0.01, 0.01, 0.0001])
        self.R = np.diag([1.0, 1.0, 10.0, 10.0])

        self.history.append((u, v))

    def predict(self) -> np.ndarray:
        """Advance the Kalman state vector."""
        if (self.x[6] + self.x[2]) <= 0:
            self.x[6] = 0.0

        self.x = np.dot(self.F, self.x)
        self.P = np.dot(np.dot(self.F, self.P), self.F.T) + self.Q
        self.age += 1
        if self.time_since_update > 0:
            self.hit_streak = 0
        self.time_since_update += 1

        return self.get_bbox()

    def update(self, bbox: np.ndarray, class_id: int, class_name: str, confidence: float) -> None:
        """Update Kalman filter state with new detection measurement."""
        self.time_since_update = 0
        self.hits += 1
        self.hit_streak += 1
        self.class_id = class_id
        self.class_name = class_name
        self.confidence = confidence

        w = max(1.0, bbox[2] - bbox[0])
        h = max(1.0, bbox[3] - bbox[1])
        u = bbox[0] + w / 2.0
        v = bbox[1] + h / 2.0
        z = np.array([u, v, w * h, w / float(h)])

        # Kalman gain
        y = z - np.dot(self.H, self.x)
        S = np.dot(np.dot(self.H, self.P), self.H.T) + self.R
        K = np.dot(np.dot(self.P, self.H.T), np.linalg.inv(S))

        self.x = self.x + np.dot(K, y)
        self.P = self.P - np.dot(np.dot(K, self.H), self.P)

        self.bbox = bbox
        self.velocity = (float(self.x[4]), float(self.x[5]))
        self.history.append((float(self.x[0]), float(self.x[1])))
        if len(self.history) > 30:
            self.history.pop(0)

    def get_bbox(self) -> np.ndarray:
        """Return current bounding box estimate [x1, y1, x2, y2]."""
        u, v, s, r = self.x[0], self.x[1], self.x[2], self.x[3]
        if s <= 0 or r <= 0:
            return self.bbox
        w = math.sqrt(s * r)
        h = s / max(1e-6, w)
        return np.array([u - w / 2.0, v - h / 2.0, u + w / 2.0, v + h / 2.0])

    def to_dict(self) -> Dict[str, Any]:
        bx = self.get_bbox()
        return {
            "track_id": self.track_id,
            "class_id": self.class_id,
            "class_name": self.class_name,
            "confidence": round(float(self.confidence), 3),
            "bbox": [round(float(c), 1) for c in bx],
            "velocity_px": [round(float(self.velocity[0]), 2), round(float(self.velocity[1]), 2)],
            "age": self.age,
            "hits": self.hits,
            "hit_streak": self.hit_streak,
        }


class MultiObjectTracker:
    """SORT multi-object visual tracker for PRW-Wild."""

    def __init__(self, max_age: int = 5, min_hits: int = 2, iou_threshold: float = 0.3):
        self.max_age = max_age
        self.min_hits = min_hits
        self.iou_threshold = iou_threshold
        self.trackers: List[KalmanBoxTracker] = []
        self.frame_count = 0

    def update(self, detections: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Update tracks with incoming frame detections.
        
        Args:
            detections: List of dicts with 'bbox' [x1, y1, x2, y2], 'class_id', 'class_name', 'confidence'.
        Returns:
            List of active confirmed track dicts.
        """
        self.frame_count += 1

        # 1. Predict new positions of existing tracks
        for t in self.trackers:
            t.predict()

        if len(detections) == 0:
            # Dead tracker cleanup
            self.trackers = [t for t in self.trackers if t.time_since_update <= self.max_age]
            return [t.to_dict() for t in self.trackers if t.hits >= self.min_hits or self.frame_count <= self.min_hits]

        det_boxes = np.array([d["bbox"] for d in detections])
        trk_boxes = np.array([t.get_bbox() for t in self.trackers]) if len(self.trackers) > 0 else np.empty((0, 4))

        matched, unmatched_dets, unmatched_trks = self._associate(det_boxes, trk_boxes)

        # 2. Update matched tracks
        for d_idx, t_idx in matched:
            det = detections[d_idx]
            self.trackers[t_idx].update(
                bbox=det_boxes[d_idx],
                class_id=det.get("class_id", 6),
                class_name=det.get("class_name", "unknown_animal"),
                confidence=det.get("confidence", 0.5)
            )

        # 3. Create new tracks for unmatched detections
        for d_idx in unmatched_dets:
            det = detections[d_idx]
            new_tracker = KalmanBoxTracker(
                bbox=det_boxes[d_idx],
                class_id=det.get("class_id", 6),
                class_name=det.get("class_name", "unknown_animal"),
                confidence=det.get("confidence", 0.5)
            )
            self.trackers.append(new_tracker)

        # 4. Remove stale tracks
        self.trackers = [t for t in self.trackers if t.time_since_update <= self.max_age]

        # Return active tracks
        active = [
            t.to_dict() for t in self.trackers
            if (t.hits >= self.min_hits or self.frame_count <= self.min_hits) and t.time_since_update < 1
        ]
        return active

    def _associate(
        self, det_boxes: np.ndarray, trk_boxes: np.ndarray
    ) -> Tuple[List[Tuple[int, int]], List[int], List[int]]:
        if len(trk_boxes) == 0:
            return [], list(range(len(det_boxes))), []

        iou_matrix = iou_batch(det_boxes, trk_boxes)

        # Greedy Hungarian approximation
        matched = []
        unmatched_dets = list(range(len(det_boxes)))
        unmatched_trks = list(range(len(trk_boxes)))

        while len(unmatched_dets) > 0 and len(unmatched_trks) > 0:
            # Find maximum IoU
            max_iou = 0.0
            best_d, best_t = -1, -1
            for d in unmatched_dets:
                for t in unmatched_trks:
                    if iou_matrix[d, t] > max_iou:
                        max_iou = iou_matrix[d, t]
                        best_d = d
                        best_t = t

            if max_iou >= self.iou_threshold:
                matched.append((best_d, best_t))
                unmatched_dets.remove(best_d)
                unmatched_trks.remove(best_t)
            else:
                break

        return matched, unmatched_dets, unmatched_trks
