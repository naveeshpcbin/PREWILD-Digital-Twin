# PRW-Wild Asset Manifest & Blender Production Registry

**Project:** PRW-Wild Digital Twin  
**Target Environment:** Three.js r165 / Blender 5.2.2 LTS  
**Master Blend File:** `assets/blender_source/PRW_WILD_PRODUCTION_WORLD.blend` (2.68 MB)  
**Blender MCP Bridge:** Active on `127.0.0.1:9876` (TCP JSON-RPC)

---

## 1. Master Blender Production Collections (15 Collections)

| Collection Name | Role / Subsystem | Primary Meshes & Objects | Materials Used | Exported Target GLB |
|---|---|---|---|---|
| `ENV_TERRAIN` | Sculpted natural topography | `Terrain_Production_World` (120x120 vertices, rolling forest hills, corridor depression, pond basins, farm terraces) | `M_Terrain_Natural` (Principled BSDF) | `assets/environment/terrain/terrain_world.glb` (516.6 KB) |
| `ENV_FOREST` | Native forest trees | `Tree_Sal_Mature` (rugged trunk, multi-tier foliage), `Tree_Banyan_Sprawling` (prop root pillars), `Tree_Acacia_Canopy` (umbrella crown) | `M_Bark_Sal`, `M_Foliage_Sal`, `M_Bark_Banyan`, `M_Foliage_Banyan`, `M_Bark_Acacia`, `M_Foliage_Acacia` | `assets/environment/trees/sal_mature.glb` (200.5 KB)<br>`assets/environment/trees/banyan_fig.glb` (211.3 KB)<br>`assets/environment/trees/acacia_canopy.glb` (18.2 KB) |
| `ENV_FRUIT_TREES` | Ecological forage resources | `Tree_Wild_Mango` (broadleaf dome + 18 hanging mango fruits) | `M_Bark_Mango`, `M_Foliage_Mango`, `M_Mango_Fruit` | `assets/environment/fruit_trees/mango_fruit_tree.glb` (1.28 MB) |
| `ENV_VEGETATION` | Understory & ground foliage | `Forest_Fern_Clump` (12 arched bipinnate fronds), `Forest_Shrub_Lantana` (flowering cluster bush) | `M_Fern_Frond`, `M_Shrub_Foliage`, `M_Shrub_Stem` | `assets/environment/vegetation/forest_ferns.glb` (16.6 KB)<br>`assets/environment/vegetation/forest_shrub.glb` (36.1 KB) |
| `ENV_GRASS` | Pasture grass tufts | `Tall_Grass_Tuft` (18 arched blade clusters) | `M_Tall_Grass` | `assets/environment/grass/tall_grass_clump.glb` (16.5 KB) |
| `ENV_WATER` | Sculpted ponds & riparian zones | `Pond_Basin_Carved` (sculpted basin, shoreline boulders, cattail reeds, water disc) | `M_Pond_Shore`, `M_Water_Surface`, `M_Pond_Boulder`, `M_Pond_Reeds` | `assets/environment/water/pond_basin.glb` (131.9 KB) |
| `ENV_FARMLAND` | Agricultural structures & crops | `Farmland_Crop_Parcels` (ridged furrows, sugarcane stalks), `Watchtower_Machan` (4-stilt timber tower, deck platform, railing, roof) | `M_Farm_Furrow`, `M_Sugarcane_Stalk`, `M_Machan_Wood`, `M_Machan_Roof` | `assets/environment/farmland/crop_field.glb` (53.9 KB)<br>`assets/environment/farmland/watchtower_machan.glb` (13.8 KB) |
| `ENV_BOUNDARY` | Boundary fence post | `Boundary_Sensor_Post` (reinforced post, solar micro-panel, SW-420 enclosure, PIR dome) | `M_Fence_Post`, `M_Solar_Panel`, `M_Sensor_Box` | `assets/environment/boundary/boundary_fence_sensor.glb` (6.5 KB) |
| `SPECIES_ELEPHANT` | Asian Elephant | `asian_elephant_production.glb` (rigged quadruped mesh, armature, `Walk` clip) | Production Elephant PBR | `assets/animals/elephant/asian_elephant_production.glb` (1.71 MB) |
| `SPECIES_DEER` | Chital & Sambar Deer | `chital_deer.glb` (spotted cervid), `sambar_deer.glb` (robust brown cervid) | Antler PBR, Cervid Coat | `assets/animals/deer/chital_deer.glb` (44.5 KB)<br>`assets/animals/deer/sambar_deer.glb` (45.1 KB) |
| `SPECIES_WILD_BOAR`| Indian Wild Boar | `wild_boar.glb` (suid mesh, tusks, bristle ridge, armature) | Bristle & Tusk PBR | `assets/animals/boar/wild_boar.glb` (36.5 KB) |
| `SPECIES_GAUR` | Gaur (Indian Bison) | `gaur_bison.glb` (muscular shoulder ridge, curved horns, armature) | Horn & Bovid PBR | `assets/animals/gaur/gaur_bison.glb` (46.8 KB) |
| `SPECIES_MONKEY` | Bonnet Macaque | `bonnet_macaque.glb` (primate mesh, long tail, armature) | Macaque Coat PBR | `assets/animals/monkey/bonnet_macaque.glb` (22.5 KB) |
| `SENSOR_ASSETS` | Physical hardware sensor nodes | ESP32-S3 DevKit, SW-420 vibration unit, HC-SR501 PIR sensor, INMP441 mic | Hardware Lab PBR | `assets/hardware/*.glb` |
| `CAMERA_ASSETS` | Virtual Camera Stations | `Camera_Mast_ESP32` (tubular mast, weatherproof enclosure, lens aperture) | `M_Camera_Mast`, `M_ESP32_Cam`, `M_Cam_Lens` | `assets/cameras/camera_tower.glb` (8.7 KB) |

---

## 2. Web Static Assets Mirror

All production GLB assets are mirrored in `src/prw_wild/web/static/assets/` to ensure zero HTTP 404s and seamless instancing by Three.js `GLTFLoader`.
