# PRW-Wild AAA Visual Environment Production Report
**Date:** 2026-11-02  
**Role:** Principal 3D Game Environment Architect & Three.js Graphics Engineer  
**Workspace:** `D:\Simulation For DT\prw-wild-digital-twin`  
**Quality Benchmark:** AAA Open-World Survival Aesthetic (PUBG-grade visual fidelity)

---

## 1. Architectural Overview & Design Philosophy

The PRW-Wild 3D Digital Twin visualizer has been transformed from an empty dark simulation viewport into an expansive, believable South Indian forest-to-farmland ecosystem. The scene seamlessly merges natural wildlife habitats with realistic agricultural buffers and physical early-warning detection infrastructure.

```
+---------------------------------------------------------------------------------------------------+
|                                  PRW-WILD OPEN-WORLD ECOSYSTEM                                     |
|                                                                                                   |
|  [WESTERN FOREST ECOSYSTEM]              [CORRIDOR & BOUNDARY]             [EASTERN FARMLAND]    |
|  - Shorea robusta (Sal Mature)          - Ancient Migratory Riverbed        - Stepped Terraces     |
|  - Ficus benghalensis (Banyan)           - Layer 1: Outer CSI / ESP32        - Agricultural Furrows |
|  - Acacia Canopy Trees                  - Layer 2: Vibration & Acoustic     - Watchtower (Machan)  |
|  - Dense Understory & Ferns             - Layer 3: Inner Camera CAM_01      - High-Yield Crops     |
|  - North & South Carved Ponds           - 26 Concrete Grounded Fence Posts  - Fruit Orchard Trees  |
+---------------------------------------------------------------------------------------------------+
```

---

## 2. Terrain & Ground Surface Construction

### 2.1 Unified Continuous Elevation Grid
- **Resolution:** 120 × 120 tessellation grid spanning the 225m × 200m primary operational sector.
- **Analytical Elevation Grounding:**
  Every vertex is calculated using the shared analytical height equation `get_terrain_elevation(x, z)`:
  - **Forest Zone ($X < 100\text{m}$):** Multi-frequency harmonic sinusoids creating organic rolling hills (elevations $+1.2\text{m}$ to $+4.8\text{m}$) and steep western ridgelines ($X < 40\text{m}$).
  - **Wildlife Corridor Valley ($Z \approx 100\text{m}$):** Parabolic natural depression ($2.2\text{m}$ depth) providing animal passage between the forest and agricultural boundary.
  - **Carved Water Basins:** North pond at $(75, 140)$ with $22\text{m}$ radius and $2.4\text{m}$ basin depth; South pond at $(60, 45)$ with $18\text{m}$ radius and $2.1\text{m}$ depth.
  - **Farmland Zone ($X \ge 100\text{m}$):** Stepped agricultural terraces dropping $0.35\text{m}$ every $28\text{m}$, etched with micro-furrow wave modulation ($Z \cdot 1.1$).
- **Horizon Skirt Mesh:**
  A $1200\text{m} \times 1200\text{m}$ horizon skirt eliminates edge-clipping voids and seamlessly connects the operational sector with the atmospheric backdrop.

### 2.2 Multi-Texture PBR Material Splatting
The terrain utilizes genuine PBR textures (albedo, normal, and roughness maps):
1. **Forest Floor (`assets/environment/terrain/forest_ground_*.jpg`):** Organic humus, decomposed leaf litter, damp forest soil, and roots.
2. **Agricultural Soil (`assets/environment/terrain/farm_soil_*.jpg`):** Tilled red-laterite loam, aerated clods, and furrow compaction.
3. **Corridor Mud (`assets/environment/terrain/corridor_mud_*.jpg`):** Compacted silt and riverbed mud along migratory animal paths.

---

## 3. Atmospheric Perspective & Lighting Architecture

To match professional open-world game titles, lighting was rebuilt from dark-void monochrome into vibrant, natural daylight:

| Light Component | Configuration | Color / Hex | Intensity | Function |
|---|---|---|---|---|
| **Sky Dome** | SphereGeometry (R=750, Inverted normals) | `#8ecae6` (Daylight Blue) | N/A | Panoramic daytime atmospheric backdrop |
| **Sun (Directional)** | Vector3(120, 160, 85) | `#fff7ed` (Warm Sunlight) | 1.40 | Primary cast shadows, highlights, PBR sheen |
| **Hemisphere Sky** | Top: Sky Blue / Bottom: Warm Soil | `#bae6fd` / `#475569` | 0.75 | Ambient environmental bounce and fill |
| **Sun Accent** | Vector3(-80, 50, -50) | `#f59e0b` (Warm Amber) | 0.35 | Twilight rim illumination on vegetation |
| **Exponential Fog** | `THREE.FogExp2(0xb0cddb, 0.0030)` | `#b0cddb` (Horizon Mist) | Density 0.0030 | Depth cueing and distant tree fading |

### Shadow Mapping Configuration
- Directional sun shadows are rendered using `THREE.PCFSoftShadowMap` with a high-resolution 2048 × 2048 shadow map.
- Normal bias (`normalBias = 0.02`) and depth bias (`bias = -0.0004`) prevent shadow acne and self-shadowing artifacts on complex animal limbs and foliage planes.

---

## 4. Vegetation Ecosystem & Asset Diversity

The environment replaces primitive boxes and spheres with detailed 3D foliage and tree models:
- **Sal Forest Canopy (`sal_mature.glb` - 208 KB):** High-canopy hardwood dominant in South Indian moist deciduous tracts.
- **Banyan Fig (`banyan_fig.glb` - 212 KB):** Expansive canopy with characteristic aerial prop roots.
- **Acacia Umbrella Canopy (`acacia_canopy.glb` - 18.6 KB):** Flat-topped dry deciduous acacia.
- **Mango & Fruit Trees (`mango_fruit_tree.glb` - 284 KB):** Cultivated orchard trees along the agricultural buffer.
- **Understory & Ground Cover:**
  - Forest Ferns (`forest_ferns.glb` - 28.6 KB)
  - Forest Shrubs (`forest_shrub.glb` - 44.7 KB & `shrub_01.glb` - 8.3 MB)
  - Clump Grass (`tall_grass_clump.glb` - 24.3 KB & `grass_medium_01.glb` - 3.3 MB)
  - Granite Boulders (`boulder_01.glb` - 4.48 MB)

All instanced trees and rocks receive random yaw rotations ($0 \dots 2\pi$) and scale variations ($0.85 \dots 1.25$) to eliminate visual repetition.

---

## 5. Detection Infrastructure & Agricultural Structures

1. **Boundary Fence Line ($X = 100\text{m}$):**
   - 26 vertical steel posts spaced along the $200\text{m}$ north-south boundary.
   - Each post is grounded with concrete footings flush with analytical terrain elevation.
   - Dual horizontal tension rails and welded wire mesh prevent floating visuals.
2. **Layer 1 (Wi-Fi CSI / ESP32 Network):**
   - Outer detection envelope centered at $X = 65\text{m}$ with a $35\text{m}$ radius corridor.
   - ESP32 CSI router station model with omnidirectional antenna and active status LED.
3. **Layer 2 (Physical Sensor Stations):**
   - Middle detection envelope at $X = 85\text{m}$ with a $20\text{m}$ radius corridor.
   - Sensor stations housing PIR (`hc_sr501_pir.glb`), acoustic (`inmp441_microphone.glb`), and geophone vibration (`sw420_vibration.glb`) units.
4. **Layer 3 (Camera Surveillance Tower):**
   - Inner visual-confirmation envelope at $X = 95\text{m}$ with a $15\text{m}$ radius corridor.
   - High-mast camera tower (`esp32_cam_ov2640.glb`) with a dynamic $60^\circ$ optical FOV frustum.
5. **Agricultural Buildings:**
   - Watchtower Machan (`watchtower_machan.glb` - 13.8 KB) elevated for community safety.
   - Crop fields (`crop_field.glb` - 53.9 KB) with realistic rows and irrigation channels.

---

## 6. Camera Viewpoints & Navigation

The environment includes comprehensive camera modes:
1. **Third-Person Perspective (Observer Eye-Level - Default):** $65^\circ$ FOV camera positioned $2.4\text{m}$ above terrain elevation, offering an immersive walking perspective.
2. **Follow Animal View:** Orbit camera bound to individual animals with smooth lerp tracking.
3. **Free Orbit / Tactical Inspection View:** Full 360-degree rotation and zoom ($4\text{m} \dots 500\text{m}$).
4. **Isometric Overview:** High-angle tactical view ($45^\circ$ elevation) covering the full forest-to-farm corridor.
5. **Top-Down Spatial Radar:** Orthographic-style surveillance monitoring for perimeter security.
6. **Camera Mast POV (CAM_01):** Real-time optical viewport rendering the scene from the camera's perspective.

