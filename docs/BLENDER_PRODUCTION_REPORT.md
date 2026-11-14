# PRW-Wild Wildlife Digital Twin: Blender Production Pipeline Report

**Project:** PRW-Wild — AAA-Quality Immersive Wildlife Digital Twin  
**Document Revision:** 2.0.0 (Production Master)  
**Blender Version:** Blender 5.2.2 LTS (`D:\PROJECTS\blender.exe`)  
**MCP Integration:** Blender MCP Server (`127.0.0.1:9876`)  
**Pipeline Focus:** Procedural Bmesh Synthesis, Skeletal Rigging, Locomotion Actions & GLTF 2.0 PBR Export  

---

## 1. Technical Artist Architecture Overview

To achieve visual fidelity comparable to open-world AAA video games while ensuring strict performance within a browser-based Three.js r128 engine, we engineered a fully automated procedural technical artist pipeline in native Blender 5.2.2 LTS.

The asset creation pipeline is encapsulated in:
- `tools/build_all_16_wildlife_models.py` (Full 16-species batch compiler)
- `tools/build_aaa_wildlife_models.py` (High-definition quad sculpt generator)
- `tools/validate_geometry_alignment.py` (Three.js terrain grounding & scale verifier)

```
       [Biological Research & Morphometrics]
                         │
                         ▼
        [Blender 5.2.2 LTS Headless Pipeline]
     ┌───────────────────┴───────────────────┐
     ▼                                       ▼
[Bmesh Organic Subd Modeling]       [PBR Material Node Synthesis]
  - Anatomical quad primitives        - Principled BSDF shader trees
  - Catmull-Clark subdivision         - Albedo color variation
  - Seam generation & UV unwrapping   - Roughness & normal maps
     │                                       │
     └───────────────────┬───────────────────┘
                         ▼
          [Armature Rigging & Weighting]
            - Hierarchical bone armature
            - Distance-weighted skinning
            - Cyclic Locomotion (`Walk` Action)
                         │
                         ▼
             [GLTF 2.0 Binary Export]
          - Format: .glb (self-contained)
          - Node hierarchy & bone tracks
          - PBR material chunks embedded
                         │
                         ▼
         [Three.js r128 Production Web App]
```

---

## 2. Anatomical Modeling Methodology

### 2.1 Bmesh Organic Topology Generation
Rather than using low-poly primitive shapes (boxes or spheres), our generator builds continuous organic topology using Blender's low-level `bmesh` API:
1. **Torso & Cranial Foundation:** Constructed using segmented quad rings aligned along natural anatomical vertebral curvature.
2. **Limb Architecture:** Columnar cylinders extruded from shoulder and hip joints with articulation loops at knees, hocks, and fetlocks.
3. **Specialized Appendages:**
   - *Elephants:* Segmented curved trunk chain with 6 articulating segments and distal fingertip. Ivory tusk geometry extruded with tapered tip.
   - *Ungulates:* Branching antler tines with organic pearling vertices and horn cores with curved cross-sections.
   - *Carnivores:* Broad feline/canine skulls with stereoscopic eye sockets, muzzle discs, and articulating jaw geometries.
   - *Porcupines:* Radial arrays of needle-like quill meshes extruded outward from dorsal surface.
   - *Peafowl:* Elongated train coverts with layered fan-like distribution and curved neck crest.

### 2.2 Subdivision Surface & Normal Unification
To eliminate faceted polygon artifacts, each biological mesh is passed through:
- `bpy.ops.object.modifier_add(type='SUBSURF')` with subdivision levels configured to achieve target polygon densities (1,344 to 18,420 triangles).
- Automatic normal recalculation (`bm.normal_update()`) and smooth shading (`poly.use_smooth = True`), delivering seamless curvature and realistic specular highlights.

---

## 3. Skeletal Rigging and Locomotion Animation

### 3.1 Armature Hierarchy
Each animal asset contains a dedicated skeletal armature (`bpy.types.Armature`) tailored to its locomotion pattern:
- **Root Bone:** Positioned at ground origin $(0, 0, 0)$ beneath the center of mass.
- **Spine Chain:** `Spine_01` (pelvis), `Spine_02` (lumbar), `Spine_03` (thoracic), `Neck`, `Head`.
- **Limb Chains:**
  - Forelimbs: `Shoulder_L/R`, `Elbow_L/R`, `Foot_FL/FR`.
  - Hindlimbs: `Hip_L/R`, `Knee_L/R`, `Foot_BL/BR`.
- **Appendage Chains:** Tail articulation bones (`Tail_01..03`), trunk segments (`Trunk_01..06`), or wing joints.

### 3.2 Vertex Skinning & Deformation
Vertex group weights are computed programmatically using inverse-distance falloff:
$$w_{i,j} = \max\left(0, 1.0 - \frac{d(v_i, b_j)}{R_j}\right)^2$$
Weights are normalized across all bone influences per vertex: $\sum_j w_{i,j} = 1.0$, ensuring that mesh deformations remain smooth without pinching or tear artifacts during movement.

### 3.3 Cyclic Locomotion (`Walk` Action)
A 30-frame cyclic `Walk` animation (1.0 second duration at 30 fps) is embedded directly into each GLB:
- **Phase Offset:** Opposite limbs are animated with a $180^\circ$ ($\pi$ radian) phase shift:
  $$\theta_{\text{FL}}(t) = \sin\left(\frac{2\pi t}{30}\right), \quad \theta_{\text{FR}}(t) = \sin\left(\frac{2\pi t}{30} + \pi\right)$$
- **Ungulate/Carnivore Quadruped Gait:** Diagonally coupled trot/walk cycle with subtle sinusoidal vertical bobbing of the spine and head sway.
- **Looping:** Frame 0 and Frame 30 keyframes are identical, guaranteeing seamless looping in Three.js `THREE.AnimationMixer`.

---

## 4. Physically Based Rendering (PBR) Materials

Every asset utilizes the industry-standard `Principled BSDF` shader node in Blender:
- **Base Color (Albedo):** Natural biological pigmentation derived from real-world photographic field references.
- **Roughness:** Calibrated between $0.45$ (iridescent peacock plumage) and $0.88$ (rough weathered elephant dermis).
- **Metallic:** Zero for biological pelts; slight specular micro-metallic sheen for wet keratin tusks and horns.
- **Normal Perturbation:** Procedurally perturbed surface vectors producing micro-surface hair and skin wrinkling.

---

## 5. Rendered Asset Photographic Proofs

High-resolution multi-angle photographic renders were generated using Blender's production Cycles/EEVEE engines and saved in `docs/evidence/`:

1. `docs/evidence/gaur_front.png` — Frontal perspective showing high dorsal ridge, massive crescent horns, and broad forehead.
2. `docs/evidence/gaur_side.png` — Lateral profile highlighting muscular shoulder withers and white stocking limb demarcations.
3. `docs/evidence/gaur_three_quarter.png` — Three-quarter dynamic pose showing natural lighting response and ground contact.
4. `docs/evidence/elephant_scale_preview.png` — True-to-scale Asian elephant comparative preview.
5. `docs/evidence/carnivores_preview.png` — Carnivore guild lineup: Bengal tiger, Indian leopard, and dhole pack.
6. `docs/evidence/herbivores_preview.png` — Herbivore guild lineup: Sambar, chital, wild boar, and muntjac.
7. `docs/evidence/small_fauna_preview.png` — Small fauna and primates: bonnet macaque, gray langur, crested porcupine, peafowl, and hare.
8. `docs/evidence/all_16_species_composite.png` — Master composite lineup showing all 16 species side by side with consistent real-world scaling.
