"""PRW-Wild Vision Package.

Contains real computer vision inference, species classification,
SORT multi-object tracking, and independent visual boundary risk estimation.
"""

from prw_wild.vision.class_registry import TARGET_CLASSES, DetectionClass, map_detection_class
from prw_wild.vision.detector import WildlifeVisionDetector, DetectionResult
from prw_wild.vision.tracker import MultiObjectTracker, KalmanBoxTracker
from prw_wild.vision.risk_estimator import VisualRiskEstimator, TrackRiskAssessment

__all__ = [
    "TARGET_CLASSES",
    "DetectionClass",
    "map_detection_class",
    "WildlifeVisionDetector",
    "DetectionResult",
    "MultiObjectTracker",
    "KalmanBoxTracker",
    "VisualRiskEstimator",
    "TrackRiskAssessment",
]

