# PRW-Wild: Production Scene & Geometry Audit Report
**Exhaustive Structural, Geometrical & Visual Defect Analysis**
**Project:** PRW-Wild Digital Twin (`D:\Simulation For DT\prw-wild-digital-twin`)  
**Audit Date:** November 2, 2026  
**Auditor:** PRW-Wild Autonomous Engineering & Technical Art Team  

---

## 1. Executive Summary of Audit Findings

An in-depth audit of the production Three.js codebase (`src/prw_wild/web/static/app.js`), existing Blender master scene, and browser viewport captures identified ten primary defect classes responsible for the visual and architectural shortcomings noted by the client:

```
                                  IDENTIFIED DEFECT ARCHITECTURE
 ┌───────────────────────────────────────────────┴───────────────────────────────────────────────┐
 │                                                                                               │
 ▼                                               ▼                                               ▼
[A. PROCEDURAL GEOMETRIC PRIMITIVES]    [B. TERRAIN & LIGHTING ATROPHY]         [C. STRUCTURAL MISALIGNMENT]
- Faceted Dodecahedron leaf lobes       - Deep dark-slate void background       - Missing physical fence rails
- Stacked cylinder disc canopies        - Flat uniform furrow rectangles        - Floating post bases on slopes
- Flat cylinder pond water discs        - Texture repetition & low contrast     - Disconnected sensor masts
 │                                               │                                               │
 └───────────────────────────────────────────────┼───────────────────────────────────────────────┘
                                                 ▼
                                  [D. INSUFFICIENT ANIMAL MORPHOLOGY]
                                  - Only 6 base species models without sexual dimorphism
                                  - Stags and hinds sharing identical antler meshes
                                  - Reliance on simple scalar multiplication rather than distinct anatomical models
```

---

## 2. Granular Defect Catalog & Root Cause Analysis

### Defect 1: Primitive Rounded & Faceted Foliage Geometry
- **Root Cause in `app.js` (lines 530–575):** The procedural fallback generates trees using stacked cylinders (`CylinderGeometry(3.8, 4.5, 1.2, 9)`) and clustered `DodecahedronGeometry(2.6, 1)`. These low-subdivision primitives produce unmistakable polyhedral facets and stacked "pancake" canopies that immediately shatter open-world immersion.
- **Repair Mandate:** Replace procedural canopies entirely with high-detail photorealistic foliage meshes authored in Blender 5.2.2 LTS with organic branch bifurcation, alpha-tested leaf cards, and varying canopy silhouettes (Sal, Banyan, Acacia, Wild Mango).

### Defect 2: Bright-Green Stacked Circular Geometry
- **Root Cause in `app.js`:** The Acacia procedural generator layers multiple flat cylinder discs (`CylinderGeometry(2.4, 3.2, 0.8)`) with a high-saturation unshaded green material (`0x22c55e`).
- **Repair Mandate:** Reconstruct the Umbrella Acacia in Blender using realistic branch armatures with flat-topped umbrella branching, natural bark furrow normals, and olive-toned dry-deciduous leaf clusters.

### Defect 3: Dark, Empty Terrain Region & Flat Water
- **Root Cause:** The scene background was configured to an overly dark blue-slate (`0x1e293b`), and water was initially rendered using a flat cylinder disc (`CylinderGeometry(18, 18, 0.3)`).
- **Repair Mandate:** Implement a realistic day-sky lighting model with warm directional sunlight ($5200\text{K}$, intensity 1.45), subtle ambient sky illumination, natural ground splatting (forest loam, decomposed leaf litter, red clay corridor mud, tilled farmland soil), and physically based water with depth extinction, subtle Fresnel reflectance, and sculpted clay shoreline embankments.

### Defect 4: Repetitive Agricultural Strips
- **Root Cause in `app.js` (lines 580–605):** Agricultural crops were generated as uniform geometric boxes (`BoxGeometry(85, 0.45, 1.8)`) spaced at rigid 5.5m intervals with identical height.
- **Repair Mandate:** Model authentic South Indian buffer farmland in Blender with varied crop parcels (sugarcane stalks, paddy bunds, tilled earth furrows, irrigation channels), height jitter ($\pm 25\%$), and organic weed/path margins.

### Defect 5: Structural Misalignment (Posts, Rails, Masts & Beams)
- **Root Cause in `app.js` (lines 620–670):** The boundary fence at $x = 100\text{m}$ placed vertical posts along a mathematical line but lacked physical horizontal cross-rails connecting post to post. Posts on sloped terrain exhibited floating bases or penetrated uneven ground. Camera masts and sensors were rendered as disconnected primitives.
- **Repair Mandate:** Reconstruct all structural components in Blender with exact mortise/bracket joints, twin horizontal timber/steel tension rails connecting consecutive posts, concrete footer footings buried in terrain, and perfectly plumb verticality.

### Defect 6: Animal Assets Insufficient in Diversity & Detail
- **Root Cause:** The system only deployed 6 single-model assets with client-side scaling to represent calves and alpha males. Male and female ungulates (stags vs. hinds) were not anatomically distinguished.
- **Repair Mandate:** Produce and acquire **at least 12 distinct production animal models** (2 distinct anatomical variants per species):
  1. Asian Elephant: Alpha Tusker Bull vs. Matriarch Cow / Calf
  2. Chital Deer: Branched Antler Stag vs. Spotted Hind
  3. Sambar Deer: Rugged Dark Mane Stag vs. Slender Hornless Cow
  4. Indian Wild Boar: Tusked Razorback Boar vs. Compact Foraging Sow
  5. Gaur: Titan Muscular Bull with crest hump vs. Grazing Cow
  6. Bonnet Macaque: Dominant Troop Leader vs. Nimble Ground Forager

---

## 3. World Coordinate Contract & Single Source of Truth

To ensure zero drift across Blender, GLTF exports, Python backend, and Three.js runtime:
- **Unit Scale:** $1.0\text{ Unit} = 1.0\text{ Metre}$.
- **Blender Coordinate Convention:** Right-handed, $Z$-up, $Y$-forward.
- **Three.js Coordinate Convention:** Right-handed, $Y$-up, $Z$-backward.
- **Exporter Transformation:** Blender glTF 2.0 exporter converts $Z$-up to $Y$-up ($+Y_{\text{Three}} = +Z_{\text{Blender}}$, $+Z_{\text{Three}} = -Y_{\text{Blender}}$).
- **Runtime Terrain Heightmap:** $y = \text{getTerrainElevation}(x, z)$ serves as the single mathematical contract for all object placement and animal ground contact.

---

## 4. Next Implementation Steps

1. Research and acquire 12+ distinct wildlife models and environmental PBR assets ([docs/ASSET_RESEARCH_AND_LICENSING.md](file:///D:/Simulation%20For%20DT/prw-wild-digital-twin/docs/ASSET_RESEARCH_AND_LICENSING.md)).
2. Build `assets/blender_source/PRW_WILD_RECONSTRUCTED_WORLD.blend` with 13 required collections.
3. Fix all structural joints and create automated geometric validation ([docs/GEOMETRY_ALIGNMENT_REPORT.md](file:///D:/Simulation%20For%20DT/prw-wild-digital-twin/docs/GEOMETRY_ALIGNMENT_REPORT.md)).
4. Export modular GLBs and integrate into production Three.js website.

