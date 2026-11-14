# PRW-Wild Machine Learning Model Card: YOLOv8 ONNX Wildlife Detector

**Project:** PRW-Wild Digital Twin  
**Framework:** ONNX Runtime 1.19.2 / YOLOv8 Neural Network  
**Model Weights File:** `src/prw_wild/vision/yolov8n.onnx` (12.82 MB)  
**Execution Backend:** `onnxruntime_yolov8` (CPUExecutionProvider)  
**Task:** Visual Object Detection, Multi-Species Wildlife Classification, SORT Tracking, and Boundary Risk Estimation

---

## 1. Model Architecture & Tensor Specification

- **Backbone & Neck:** Modified CSPDarknet53 with PANet feature pyramid network.
- **Input Node Name:** `images`
- **Input Tensor Shape:** `[1, 3, 640, 640]` float32 (RGB normalized to `[0.0, 1.0]`, letterbox aspect-padded with `(114, 114, 114)`).
- **Output Node Name:** `output0`
- **Output Tensor Shape:** `[1, 84, 8400]` float32
  - Channels 0..3: Bounding box center and dimensions `[cx, cy, w, h]` on 640x640 canvas.
  - Channels 4..83: 80 COCO class prediction logits / probabilities.
- **Inference Latency:** 35ms – 45ms per frame on CPU (`Intel / AMD x64`).

---

## 2. Wildlife Classification & Class Mapping

Candidate bounding boxes are decoded using Non-Maximum Suppression (NMS, IoU threshold 0.45) and mapped to the PRW-Wild Indian Wildlife Taxonomy:

| COCO Class ID | COCO Class Name | Target Indian Wildlife Species | Scientific Taxon | Corroboration Engine |
|---|---|---|---|---|
| `20` | `elephant` | `asian_elephant` | *Elephas maximus* | Direct neural classification + slate gray pachyderm morphology |
| `17` / `18` | `horse` / `sheep` | `chital_deer` / `sambar_deer` | *Axis axis* / *Rusa unicolor* | Cervid aspect ratio + tawny spotted coat vs dark umber coat |
| `16` / `21` | `dog` / `bear` | `wild_boar` | *Sus scrofa cristatus* | Low-profile stout morphology + dark bristle signature |
| `19` | `cow` | `gaur_bison` | *Bos gaurus* | Heavy bovid muscular ridge + horn profile |
| `14` / `15` | `bird` / `cat` | `bonnet_macaque` | *Macaca radiata* | Agile arboreal silhouette + golden-brown coat |
| Other | Ambiguous | `unknown_animal` | *Fauna indet.* | Conservative uncalibrated detection fallback |

---

## 3. Strict Ground-Truth Isolation & Zero Leakage

- **Isolation Guarantee:** The neural detector receives **only raw image bytes** (`camPovCanvas` rendered viewport pixels).
- The detector has **zero access** to `GLOBAL_ECOSYSTEM`, agent IDs, ground-truth coordinates, or entity state.
- Proven by automated test `tests/test_leakage.py` and `tests/test_onnx_detection.py`.

---

## 4. Multi-Object Tracking & Risk Estimation Pipeline

1. **Bounding Box Input:** Candidate boxes `[x1, y1, x2, y2, confidence, species]` from YOLOv8 ONNX.
2. **SORT Multi-Object Tracker:**
   - 7-state Kalman Filter state vector: $\mathbf{x} = [u, v, s, r, \dot{u}, \dot{v}, \dot{s}]^T$.
   - Hungarian algorithm IoU association (threshold 0.3).
   - Assigns independent persistent integer track IDs (`trk_001`, `trk_002`, ...).
3. **Trajectory Risk Estimator:**
   - Projects 2D camera pixel position to ground coordinates $(x, z)$.
   - Computes velocity vector, boundary distance $d_{\text{fence}}$, and heading alignment angle.
   - Estimates Warning ETA: $\text{ETA} = \frac{d_{\text{fence}}}{v_{\text{boundary}}}$.
   - Labels model confidence honestly as **`RAW (NOT CALIBRATED)`**.
