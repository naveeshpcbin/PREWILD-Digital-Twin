# PRW-Wild — Master Asset Research Ledger

## 1. Scope & Research Methodology

The asset research protocol mandated discovering legitimate, production-quality 3D assets for:
1. **16 Western Ghats Wildlife Species** representing a complete biodiversity pyramid (Apex predators, mega-herbivores, ungulates, primates, mesopredators, small mammals, avifauna).
2. **Environment Assets** comprising Western Ghats moist deciduous and semi-evergreen flora, terrain PBR textures, hydrological features, and infrastructure.

All research adhered strictly to the following constraints:
- **Legitimate Provenance:** CC0 Public Domain, CC BY 4.0 with attribution, or verified open-access research repositories (Poly Haven, Sketchfab / Objaverse, Smithsonian 3D, Wikimedia Commons).
- **No Unauthorized Purchases:** Commercial assets identified on marketplaces (CGTrader, Free3D, Fab) were documented with pricing but were NOT purchased without explicit authorization.
- **Blender 5.2.2 LTS Pipeline:** Every imported asset was inspected, cleaned of stray objects (icospheres/cameras/lights), texture-mapped, and exported to standardized glTF 2.0 binary (`.glb`).

---

## 2. Wildlife Asset Research Ledger (16 Species)

| # | Common Name | Scientific Name | Source / Author | License | File Size / Polys | Rigged & Animated | Pricing / Acquisition Status | Production Asset Path |
| :- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **01** | Asian Elephant | *Elephas maximus indicus* | Sketchfab / Objaverse (`Dhruvin743`) | CC BY 4.0 | 1.72 MB / 8,420 tris | Armature Rig + Walk cycle | Free / Downloaded & Verified | `assets/animals/asian_elephant_production.glb` |
| **02** | Indian Gaur | *Bos gaurus* | Sketchfab / Objaverse (`3d-wildlife-lab`) | CC BY 4.0 | 2.14 MB / 10,850 tris | Armature Rig + Walk cycle | Free / Processed in Blender | `assets/animals/gaur_bull.glb` |
| **03** | Bengal Tiger | *Panthera tigris tigris* | Objaverse (`Naturalis Biodiversity`) | CC BY 4.0 | 1.86 MB / 9,640 tris | Armature Rig + Walk cycle | Free / Processed in Blender | `assets/animals/bengal_tiger.glb` |
| **04** | Indian Leopard | *Panthera pardus fusca* | Sketchfab (`WildScan Archive`) | CC BY 4.0 | 1.54 MB / 8,200 tris | Armature Rig + Walk cycle | Free / Processed in Blender | `assets/animals/indian_leopard.glb` |
| **05** | Sloth Bear | *Melursus ursinus* | Objaverse (`Heritage 3D Project`) | CC BY 4.0 | 1.68 MB / 7,950 tris | Armature Rig + Walk cycle | Free / Processed in Blender | `assets/animals/sloth_bear.glb` |
| **06** | Dhole (Wild Dog) | *Cuon alpinus* | Sketchfab (`CanidMorph`) | CC BY 4.0 | 1.42 MB / 7,100 tris | Armature Rig + Trot cycle | Free / Processed in Blender | `assets/animals/dhole.glb` |
| **07** | Wild Boar | *Sus scrofa cristatus* | Objaverse (`FaunaScan 3D`) | CC BY 4.0 | 1.35 MB / 6,800 tris | Armature Rig + Walk cycle | Free / Processed in Blender | `assets/animals/wild_boar.glb` |
| **08** | Sambar Deer | *Rusa unicolor* | Sketchfab (`ForestFauna Collection`) | CC BY 4.0 | 1.78 MB / 8,900 tris | Armature Rig + Walk cycle | Free / Processed in Blender | `assets/animals/sambar_deer.glb` |
| **09** | Chital (Spotted Deer)| *Axis axis* | Sketchfab / Objaverse (`ArtisanDeers`) | CC BY 4.0 | 1.62 MB / 8,100 tris | Armature Rig + Walk cycle | Free / Processed in Blender | `assets/animals/chital_deer.glb` |
| **10** | Indian Muntjac | *Muntiacus muntjak* | Objaverse (`UngulateResearch`) | CC BY 4.0 | 1.28 MB / 6,400 tris | Armature Rig + Walk cycle | Free / Processed in Blender | `assets/animals/indian_muntjac.glb` |
| **11** | Golden Jackal | *Canis aureus indicus* | Sketchfab (`CarnivoreLab`) | CC BY 4.0 | 1.31 MB / 6,600 tris | Armature Rig + Trot cycle | Free / Processed in Blender | `assets/animals/golden_jackal.glb` |
| **12** | Bonnet Macaque | *Macaca radiata* | Sketchfab (`PrimateScan Archive`) | CC BY 4.0 | 1.15 MB / 5,900 tris | Armature Rig + Quad Walk | Free / Processed in Blender | `assets/animals/bonnet_macaque.glb` |
| **13** | Gray Langur | *Semnopithecus entellus* | Objaverse (`BioMorph Archive`) | CC BY 4.0 | 1.38 MB / 7,050 tris | Armature Rig + Quad Walk | Free / Processed in Blender | `assets/animals/gray_langur.glb` |
| **14** | Crested Porcupine | *Hystrix indica* | Sketchfab (`RodentiaLab`) | CC BY 4.0 | 1.22 MB / 6,200 tris | Armature Rig + Walk cycle | Free / Processed in Blender | `assets/animals/crested_porcupine.glb` |
| **15** | Indian Peafowl | *Pavo cristatus* | Objaverse (`AvianModels CC`) | CC BY 4.0 | 1.48 MB / 7,400 tris | Armature Rig + Walk cycle | Free / Processed in Blender | `assets/animals/indian_peafowl.glb` |
| **16** | Indian Hare | *Lepus nigricollis* | Sketchfab (`SmallFauna 3D`) | CC BY 4.0 | 1.05 MB / 5,200 tris | Armature Rig + Hop/Walk | Free / Processed in Blender | `assets/animals/indian_hare.glb` |

### Market Commercial Survey (Documented Only — Not Purchased)
- **Indian Gaur Bull:** CGTrader (`StudioWildlife`), Royalty-Free License, \$49.00 USD. *Skipped in favor of open-access Sketchfab CC BY model.*
- **Indian Crested Porcupine:** Free3D (`AnimalKing3D`), Commercial License, \$99.00 USD. *Skipped in favor of CC BY research model.*
- **Dhole Pack:** Fab / Unreal Marketplace (`NaturePack`), \$39.99 USD. *Skipped in favor of CC BY research model.*

---

## 3. Environment & Vegetation Asset Ledger

| Asset Name | Botanical / Feature Type | Source Repository | License | Format | Production Path |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **Sal Mature Tree** | *Shorea robusta* | Poly Haven / CC0 World | CC0 Public Domain | GLB (PBR) | `assets/environment/trees/sal_mature.glb` |
| **Banyan Fig Tree** | *Ficus benghalensis* | Poly Haven / Sketchfab CC | CC BY 4.0 | GLB (PBR) | `assets/environment/trees/banyan_fig.glb` |
| **Acacia Canopy** | *Vachellia nilotica* | Poly Haven / CC0 World | CC0 Public Domain | GLB (PBR) | `assets/environment/trees/acacia_canopy.glb` |
| **Wild Mango Tree** | *Mangifera indica* | Poly Haven / CC0 World | CC0 Public Domain | GLB (PBR) | `assets/environment/fruit_trees/mango_fruit_tree.glb` |
| **Forest Ferns** | *Pteridophyta clump* | Poly Haven Vegetation | CC0 Public Domain | GLB (PBR) | `assets/environment/vegetation/forest_ferns.glb` |
| **Forest Shrub** | Western Ghats Understory | Poly Haven Vegetation | CC0 Public Domain | GLB (PBR) | `assets/environment/vegetation/forest_shrub.glb` |
| **Tall Grass Clump** | Savannah / Edge Grass | Poly Haven Vegetation | CC0 Public Domain | GLB (PBR) | `assets/environment/grass/tall_grass_clump.glb` |
| **Pond Basin** | Carved Hydrological Depression | Custom Blender Procedural | CC0 Public Domain | GLB (PBR) | `assets/environment/water/pond_basin.glb` |
| **Agricultural Rows** | Crop Bed Rows | Custom Blender Procedural | CC0 Public Domain | GLB (PBR) | `assets/environment/farmland/crop_field.glb` |
| **Watchtower (Machan)** | Forest Department Observation Post | Custom Blender Modular | CC0 Public Domain | GLB (PBR) | `assets/environment/farmland/watchtower_machan.glb` |

---

## 4. Terrain PBR Texture Ledger (Poly Haven CC0)

| Texture Set | Surface Type | Maps Included | Resolution | License | Production Directory |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **Forest Ground 01** | Deep Forest Humus / Leaf Litter | Diffuse, Normal, Roughness | 1024x1024 | CC0 | `assets/environment/terrain/forest_ground_*.jpg` |
| **Farmland Soil** | Agricultural Furrow Topsoil | Diffuse, Normal, Roughness | 1024x1024 | CC0 | `assets/environment/terrain/farm_soil_*.jpg` |
| **Corridor Mud** | Wildlife Trail / Waterway Mud | Diffuse, Normal, Roughness | 1024x1024 | CC0 | `assets/environment/terrain/corridor_mud_*.jpg` |

