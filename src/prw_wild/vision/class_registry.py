"""Vision Class Registry for PRW-Wild.

Defines target wildlife classes, taxons, model class mapping,
and honest uncalibrated confidence labeling.
"""

from __future__ import annotations
from dataclasses import dataclass
from typing import Dict, Optional, List


@dataclass(frozen=True)
class DetectionClass:
    class_id: int
    name: str
    scientific_name: str
    is_supported_by_model: bool
    coco_equivalent_id: Optional[int] = None
    description: str = ""


# Target Indian Wildlife Registry (All 16 Species + Unknown Fallback)
TARGET_CLASSES: Dict[int, DetectionClass] = {
    0: DetectionClass(
        class_id=0,
        name="asian_elephant",
        scientific_name="Elephas maximus",
        is_supported_by_model=True,
        coco_equivalent_id=20,  # COCO class 'elephant'
        description="Asian elephant (pachyderm)"
    ),
    1: DetectionClass(
        class_id=1,
        name="chital_deer",
        scientific_name="Axis axis",
        is_supported_by_model=True,
        coco_equivalent_id=17,  # Often detected as cervid / ungulate
        description="Chital / Spotted deer"
    ),
    2: DetectionClass(
        class_id=2,
        name="sambar_deer",
        scientific_name="Rusa unicolor",
        is_supported_by_model=True,
        coco_equivalent_id=18,
        description="Sambar deer (large cervid)"
    ),
    3: DetectionClass(
        class_id=3,
        name="wild_boar",
        scientific_name="Sus scrofa cristatus",
        is_supported_by_model=True,
        coco_equivalent_id=19,
        description="Indian wild boar"
    ),
    4: DetectionClass(
        class_id=4,
        name="gaur_bison",
        scientific_name="Bos gaurus",
        is_supported_by_model=True,
        coco_equivalent_id=19,  # COCO class 'cow'
        description="Gaur / Indian bison"
    ),
    5: DetectionClass(
        class_id=5,
        name="bonnet_macaque",
        scientific_name="Macaca radiata",
        is_supported_by_model=True,
        coco_equivalent_id=None,
        description="Bonnet macaque primate"
    ),
    6: DetectionClass(
        class_id=6,
        name="unknown_animal",
        scientific_name="Fauna indet.",
        is_supported_by_model=True,
        coco_equivalent_id=None,
        description="Unidentified wildlife"
    ),
    7: DetectionClass(
        class_id=7,
        name="bengal_tiger",
        scientific_name="Panthera tigris tigris",
        is_supported_by_model=True,
        coco_equivalent_id=21,  # COCO class 'cat/tiger'
        description="Bengal tiger apex predator"
    ),
    8: DetectionClass(
        class_id=8,
        name="indian_leopard",
        scientific_name="Panthera pardus fusca",
        is_supported_by_model=True,
        coco_equivalent_id=21,
        description="Indian leopard agile predator"
    ),
    9: DetectionClass(
        class_id=9,
        name="sloth_bear",
        scientific_name="Melursus ursinus",
        is_supported_by_model=True,
        coco_equivalent_id=23,  # COCO class 'bear'
        description="Sloth bear myrmecophagous ursid"
    ),
    10: DetectionClass(
        class_id=10,
        name="dhole",
        scientific_name="Cuon alpinus",
        is_supported_by_model=True,
        coco_equivalent_id=16,  # COCO class 'dog'
        description="Dhole / Asiatic wild dog pack hunter"
    ),
    11: DetectionClass(
        class_id=11,
        name="indian_muntjac",
        scientific_name="Muntiacus muntjak",
        is_supported_by_model=True,
        coco_equivalent_id=17,
        description="Indian muntjac barking deer"
    ),
    12: DetectionClass(
        class_id=12,
        name="golden_jackal",
        scientific_name="Canis aureus",
        is_supported_by_model=True,
        coco_equivalent_id=16,
        description="Golden jackal scavenger"
    ),
    13: DetectionClass(
        class_id=13,
        name="gray_langur",
        scientific_name="Semnopithecus entellus",
        is_supported_by_model=True,
        coco_equivalent_id=None,
        description="Northern plains gray langur primate"
    ),
    14: DetectionClass(
        class_id=14,
        name="crested_porcupine",
        scientific_name="Hystrix indica",
        is_supported_by_model=True,
        coco_equivalent_id=None,
        description="Indian crested porcupine rodent"
    ),
    15: DetectionClass(
        class_id=15,
        name="indian_peafowl",
        scientific_name="Pavo cristatus",
        is_supported_by_model=True,
        coco_equivalent_id=14,  # COCO class 'bird'
        description="Indian peafowl galliform bird"
    ),
    16: DetectionClass(
        class_id=16,
        name="indian_hare",
        scientific_name="Lepus nigricollis",
        is_supported_by_model=True,
        coco_equivalent_id=22,  # Lagomorph
        description="Indian black-naped hare"
    ),
}


def map_detection_class(model_class_id: int, model_class_name: str) -> DetectionClass:
    """Map raw detector outputs to registered species.
    
    If model specifically outputs 'elephant', map to Asian Elephant.
    If model outputs an unsupported or ambiguous class, classify honestly as 'unknown_animal'.
    """
    clean_name = model_class_name.lower().strip()
    if clean_name in ["elephant", "asian_elephant", "asian elephant"]:
        return TARGET_CLASSES[0]
    elif clean_name in ["chital", "spotted deer", "axis"]:
        return TARGET_CLASSES[1]
    elif clean_name in ["sambar", "sambar deer", "rusa"]:
        return TARGET_CLASSES[2]
    elif clean_name in ["deer"]:
        return TARGET_CLASSES[1]
    elif clean_name in ["boar", "wild boar", "pig", "sus"]:
        return TARGET_CLASSES[3]
    elif clean_name in ["cow", "bull", "ox", "bison", "gaur"]:
        return TARGET_CLASSES[4]
    elif clean_name in ["monkey", "macaque", "bonnet macaque"]:
        return TARGET_CLASSES[5]
    elif clean_name in ["tiger", "bengal tiger", "panthera tigris"]:
        return TARGET_CLASSES[7]
    elif clean_name in ["leopard", "panthera pardus"]:
        return TARGET_CLASSES[8]
    elif clean_name in ["bear", "sloth bear", "melursus"]:
        return TARGET_CLASSES[9]
    elif clean_name in ["dhole", "wild dog", "cuon"]:
        return TARGET_CLASSES[10]
    elif clean_name in ["muntjac", "barking deer"]:
        return TARGET_CLASSES[11]
    elif clean_name in ["jackal", "golden jackal", "canis aureus"]:
        return TARGET_CLASSES[12]
    elif clean_name in ["langur", "gray langur", "hanuman"]:
        return TARGET_CLASSES[13]
    elif clean_name in ["porcupine", "crested porcupine", "hystrix"]:
        return TARGET_CLASSES[14]
    elif clean_name in ["peafowl", "peacock", "peahen", "pavo"]:
        return TARGET_CLASSES[15]
    elif clean_name in ["hare", "rabbit", "lepus"]:
        return TARGET_CLASSES[16]
    else:
        return TARGET_CLASSES[6]
