"""
Script to integrate Blender production 3D assets into app.js
Replaces flat procedural planes and primitives with:
- terrain_world.glb
- sal_mature.glb, banyan_fig.glb, acacia_canopy.glb, mango_fruit_tree.glb
- forest_ferns.glb, forest_shrub.glb, tall_grass_clump.glb
- pond_basin.glb
- watchtower_machan.glb, crop_field.glb
"""

import re
import os

APP_JS = r"D:\Simulation For DT\prw-wild-digital-twin\src\prw_wild\web\static\app.js"

with open(APP_JS, "r", encoding="utf-8") as f:
    content = f.read()

# 1. Update buildProceduralEnvironment to load terrain_world.glb
target_proc_env = """  function buildProceduralEnvironment() {
    // 1. Forest Zone Ground Plane (x: -25 to 100, z: -30 to 230) with organic elevation slope
    const forestGeo = new THREE.PlaneGeometry(125, 260, 64, 64);"""

replacement_proc_env = """  function buildProceduralEnvironment() {
    // 0. Production Blender Sculpted 3D Terrain GLB
    if (window.THREE && typeof THREE.GLTFLoader === 'function') {
      const terrainLoader = new THREE.GLTFLoader();
      terrainLoader.load('assets/environment/terrain/terrain_world.glb', (gltf) => {
        const terrainObj = gltf.scene;
        terrainObj.name = 'Blender_Production_Terrain_World';
        terrainObj.traverse((c) => {
          if (c.isMesh) {
            c.receiveShadow = true;
          }
        });
        threeScene.add(terrainObj);
        // Seamlessly replace flat ground planes with sculpted terrain
        if (typeof forestMesh !== 'undefined') forestMesh.visible = false;
        if (typeof farmMesh !== 'undefined') farmMesh.visible = false;
        console.log('[PRW-Wild] Loaded Blender Production Sculpted Terrain World GLB');
      }, undefined, (err) => {
        console.warn('[PRW-Wild] Terrain GLB fallback notice:', err);
      });
    }

    // 1. Forest Zone Ground Plane (x: -25 to 100, z: -30 to 230) with organic elevation slope
    const forestGeo = new THREE.PlaneGeometry(125, 260, 64, 64);"""

assert target_proc_env in content, "target_proc_env not found"
content = content.replace(target_proc_env, replacement_proc_env)

# 2. Update buildDiverseForest with production tree assets and expanded population
target_forest = """    // 2. High-Fidelity 3D GLB Forest Asset Loading
    if (window.THREE && typeof THREE.GLTFLoader === 'function') {
      const loader = new THREE.GLTFLoader();
      const glbModels = {};
      const assetsToLoad = [
        { id: 'acacia', url: 'assets/environment/trees/tree_acacia_umbrella.glb' },
        { id: 'sal', url: 'assets/environment/trees/tree_sal_forest.glb' },
        { id: 'banyan', url: 'assets/environment/trees/tree_ficus_banyan.glb' },
        { id: 'boulder', url: 'assets/environment/rocks/boulder_01.glb' },
        { id: 'fern', url: 'assets/environment/vegetation/fern_02.glb' },
        { id: 'shrub', url: 'assets/environment/vegetation/shrub_01.glb' },
        { id: 'grass', url: 'assets/environment/vegetation/grass_medium_01.glb' },
      ];"""

replacement_forest = """    // 2. High-Fidelity 3D GLB Forest Asset Loading (Blender Production World)
    if (window.THREE && typeof THREE.GLTFLoader === 'function') {
      const loader = new THREE.GLTFLoader();
      const glbModels = {};
      const assetsToLoad = [
        { id: 'acacia', url: 'assets/environment/trees/acacia_canopy.glb' },
        { id: 'sal', url: 'assets/environment/trees/sal_mature.glb' },
        { id: 'banyan', url: 'assets/environment/trees/banyan_fig.glb' },
        { id: 'mango', url: 'assets/environment/fruit_trees/mango_fruit_tree.glb' },
        { id: 'boulder', url: 'assets/environment/rocks/boulder_01.glb' },
        { id: 'fern', url: 'assets/environment/vegetation/forest_ferns.glb' },
        { id: 'shrub', url: 'assets/environment/vegetation/forest_shrub.glb' },
        { id: 'grass', url: 'assets/environment/grass/tall_grass_clump.glb' },
      ];"""

assert target_forest in content, "target_forest not found"
content = content.replace(target_forest, replacement_forest)

# 3. Update buildFarmStructures with Watchtower Machan and Crop Field
target_farm = """    shedGroup.position.set(138, 0, 115);
    threeScene.add(shedGroup);
  }"""

replacement_farm = """    shedGroup.position.set(138, 0, 115);
    threeScene.add(shedGroup);

    // Production Watchtower Machan & Crop Field GLBs
    if (window.THREE && typeof THREE.GLTFLoader === 'function') {
      const loader = new THREE.GLTFLoader();
      loader.load('assets/environment/farmland/watchtower_machan.glb', (gltf) => {
        const machan = gltf.scene;
        machan.name = 'Blender_Watchtower_Machan';
        machan.position.set(118, 0, 102);
        machan.scale.set(1.1, 1.1, 1.1);
        machan.traverse((c) => { if (c.isMesh) { c.castShadow = true; c.receiveShadow = true; } });
        threeScene.add(machan);
        console.log('[PRW-Wild] Loaded Blender Production Watchtower Machan GLB');
      }, undefined, (e) => { console.warn('[PRW-Wild] Machan note:', e); });

      loader.load('assets/environment/farmland/crop_field.glb', (gltf) => {
        const cropsNorth = gltf.scene;
        cropsNorth.name = 'Blender_Crop_Field_North';
        cropsNorth.position.set(145, 0, 75);
        cropsNorth.traverse((c) => { if (c.isMesh) { c.castShadow = true; c.receiveShadow = true; } });
        threeScene.add(cropsNorth);

        const cropsSouth = cropsNorth.clone();
        cropsSouth.name = 'Blender_Crop_Field_South';
        cropsSouth.position.set(145, 0, 145);
        threeScene.add(cropsSouth);
        console.log('[PRW-Wild] Loaded Blender Production Crop Field Parcels');
      }, undefined, (e) => { console.warn('[PRW-Wild] Crop parcel note:', e); });
    }
  }"""

assert target_farm in content, "target_farm not found"
content = content.replace(target_farm, replacement_farm)

# 4. Update initMultiAnimalEcosystem with sculpted pond basin
target_ponds = """    threeObjects.ecosystemPonds.push(pondNorth, pondSouth);

    // 2. Preload Species 3D GLB Models"""

replacement_ponds = """    threeObjects.ecosystemPonds.push(pondNorth, pondSouth);

    // Production Carved Pond Basin GLB (Blender Production World)
    if (window.THREE && typeof THREE.GLTFLoader === 'function') {
      const pondLoader = new THREE.GLTFLoader();
      pondLoader.load('assets/environment/water/pond_basin.glb', (gltf) => {
        const basinNorth = gltf.scene;
        basinNorth.name = 'Blender_Pond_Basin_North';
        basinNorth.position.set(75, 0.05, 140);
        basinNorth.scale.set(1.0, 1.0, 1.0);
        basinNorth.traverse((c) => { if (c.isMesh) { c.receiveShadow = true; } });
        threeScene.add(basinNorth);

        const basinSouth = basinNorth.clone();
        basinSouth.name = 'Blender_Pond_Basin_South';
        basinSouth.position.set(60, 0.05, 45);
        basinSouth.scale.set(0.85, 0.85, 0.85);
        threeScene.add(basinSouth);

        // Hide primitive flat cylinder discs once sculpted basins are loaded
        pondNorth.visible = false;
        pondSouth.visible = false;
        console.log('[PRW-Wild] Loaded Blender Production Carved Pond Basins');
      }, undefined, (e) => { console.warn('[PRW-Wild] Pond basin note:', e); });
    }

    // 2. Preload Species 3D GLB Models"""

assert target_ponds in content, "target_ponds not found"
content = content.replace(target_ponds, replacement_ponds)

with open(APP_JS, "w", encoding="utf-8") as f:
    f.write(content)

print("Successfully patched app.js with production 3D assets!")

