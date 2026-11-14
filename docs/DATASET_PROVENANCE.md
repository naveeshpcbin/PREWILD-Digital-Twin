# PRW-Wild Dataset Provenance & Synthetic Pipeline

## 1. Overview & Provenance Standards

In accordance with scientific integrity guidelines:
- Real-world wildlife image datasets (such as LILA BC / iWildCam, Eikelboom aerial wildlife, and WildEye) require strict licence compliance (CC-BY 4.0, CC0, or ODC-BY).
- To enable closed-loop digital twin verification without data leakage, synthetic camera frames generated from Three.js and Blender virtual camera viewports are used for offline calibration and testing.

## 2. Synthetic Data Generation Architecture

```
+-------------------------------------------------------------+
| BLENDER & THREE.JS HIGH-FIDELITY VIRTUAL ENVIRONMENT       |
| - Photorealistic Indian Forest, Corridor & Farmland         |
| - 3D Rigged Animal Meshes with Animated Quadruped Gaits     |
| - Dynamic Lighting: Morning Sun, Dusk, Direct Overhead, Fog |
+-------------------------------------------------------------+
                              |
                              v
+-------------------------------------------------------------+
| OFFLINE SYNTHETIC DATASET GENERATOR                         |
| - Varied Camera Heights (2.5m - 6.0m), Angles (15 deg - 60) |
| - Partial Occlusion from Trees, Shrubs, and Terrain Props   |
| - Realistic Distance Variation (5m to 60m from Camera)      |
| - Automatic 2D Bounding Box Extraction from Screen Proj     |
|   (Strictly used for offline training & validation only)    |
+-------------------------------------------------------------+
                              |
                              v
+-------------------------------------------------------------+
| DATASET SPLITS (DISJOINT SEEDS & LIGHTING CONDITIONS)       |
| - Train (70%): Diverse weather, poses, backgrounds          |
| - Val (15%): Independent camera viewpoints and seeds        |
| - Test (15%): Completely held-out corridor conditions       |
+-------------------------------------------------------------+
```

## 3. Data Isolation Contract

- **Training & Calibration:** Annotations generated offline with ground-truth geometry projections.
- **Runtime Inference:** The live Python inference server receives ONLY RGB image pixels via POST / WebSocket. No annotations, bounding boxes, or animal entity attributes are transmitted to the inference engine.

