import os

APP_JS = r"D:\Simulation For DT\prw-wild-digital-twin\src\prw_wild\web\static\app.js"

with open(APP_JS, "r", encoding="utf-8") as f:
    content = f.read()

# 1. Elephant Material Diffuse Fix (White tint so 2K leathery hide texture displays vibrantly)
old_elephant_mat = """              if (child.material) {
                child.material.color.setHex(0x605c56); // Warm leathery slate grey
                child.material.roughness = 0.72;
                child.material.metalness = 0.02;
              }"""

new_elephant_mat = """              if (child.material) {
                // Full white diffuse tint preserves 2K photorealistic leathery hide texture
                child.material.color.setHex(0xffffff);
                child.material.roughness = 0.65;
                child.material.metalness = 0.02;
              }"""

if old_elephant_mat in content:
    content = content.replace(old_elephant_mat, new_elephant_mat, 1)
    print("[1] Elephant material fix applied successfully.")
else:
    print("[1] Note: old_elephant_mat not found directly.")

# 2. Add Boulder to glbAssets in buildDiverseForest
old_glb_assets = """      const glbAssets = [
        { id: 'sal', url: 'assets/environment/trees/sal_mature.glb' },
        { id: 'banyan', url: 'assets/environment/trees/banyan_fig.glb' },
        { id: 'acacia', url: 'assets/environment/trees/acacia_canopy.glb' },
        { id: 'mango', url: 'assets/environment/fruit_trees/mango_fruit_tree.glb' },
        { id: 'fern', url: 'assets/environment/vegetation/forest_ferns.glb' },
        { id: 'shrub', url: 'assets/environment/vegetation/forest_shrub.glb' },
        { id: 'grass', url: 'assets/environment/grass/tall_grass_clump.glb' },
      ];"""

new_glb_assets = """      const glbAssets = [
        { id: 'sal', url: 'assets/environment/trees/sal_mature.glb' },
        { id: 'banyan', url: 'assets/environment/trees/banyan_fig.glb' },
        { id: 'acacia', url: 'assets/environment/trees/acacia_canopy.glb' },
        { id: 'mango', url: 'assets/environment/fruit_trees/mango_fruit_tree.glb' },
        { id: 'fern', url: 'assets/environment/vegetation/forest_ferns.glb' },
        { id: 'shrub', url: 'assets/environment/vegetation/forest_shrub.glb' },
        { id: 'grass', url: 'assets/environment/grass/tall_grass_clump.glb' },
        { id: 'boulder', url: 'assets/environment/rocks/boulder_01.glb' },
      ];"""

if old_glb_assets in content:
    content = content.replace(old_glb_assets, new_glb_assets, 1)
    print("[2] glbAssets updated with boulder_01.")

# 3. Add boulder placement logic in glbAssets loading
old_grass_block = """          } else if (id === 'grass') {
            const grassPositions = [
              [18, 35], [26, 88], [42, 130], [55, 140], [32, 170], [62, 160],
              [88, 70], [92, 85], [94, 105], [90, 120], [86, 150], [92, 165],
              [102, 40], [105, 80], [104, 120], [102, 160], [45, 95], [52, 105]
            ];
            grassPositions.forEach(([gx, gz]) => {
              const inst = gltf.scene.clone(true);
              inst.position.set(gx, getTerrainElevation(gx, gz), gz);
              const sc = 1.2 + Math.random() * 0.5;
              inst.scale.set(sc, sc, sc);
              inst.rotation.y = Math.random() * Math.PI * 2;
              inst.traverse(c => { if (c.isMesh) { c.receiveShadow = true; } });
              forestContainer.add(inst);
            });
          }"""

new_grass_boulder_block = """          } else if (id === 'grass') {
            const grassPositions = [
              [18, 35], [26, 88], [42, 130], [55, 140], [32, 170], [62, 160],
              [88, 70], [92, 85], [94, 105], [90, 120], [86, 150], [92, 165],
              [102, 40], [105, 80], [104, 120], [102, 160], [45, 95], [52, 105]
            ];
            grassPositions.forEach(([gx, gz]) => {
              const inst = gltf.scene.clone(true);
              inst.position.set(gx, getTerrainElevation(gx, gz), gz);
              const sc = 1.2 + Math.random() * 0.5;
              inst.scale.set(sc, sc, sc);
              inst.rotation.y = Math.random() * Math.PI * 2;
              inst.traverse(c => { if (c.isMesh) { c.receiveShadow = true; } });
              forestContainer.add(inst);
            });
          } else if (id === 'boulder') {
            const boulderPositions = [
              [16, 32], [28, 55], [38, 22], [48, 72], [62, 28],
              [18, 145], [32, 158], [46, 140], [64, 162], [76, 135],
              [24, 88], [35, 110], [52, 92], [68, 105], [82, 75]
            ];
            boulderPositions.forEach(([bx, bz]) => {
              const inst = gltf.scene.clone(true);
              const gy = getTerrainElevation(bx, bz);
              inst.position.set(bx, gy, bz);
              const sc = 1.0 + Math.random() * 0.6;
              inst.scale.set(sc, sc, sc);
              inst.rotation.y = Math.random() * Math.PI * 2;
              inst.rotation.x = (Math.random() - 0.5) * 0.15;
              inst.traverse(c => {
                if (c.isMesh) {
                  c.castShadow = true;
                  c.receiveShadow = true;
                }
              });
              forestContainer.add(inst);
            });
          }"""

if old_grass_block in content:
    content = content.replace(old_grass_block, new_grass_boulder_block, 1)
    print("[3] Boulder placement logic added.")

# 4. Remove crude procedural red cone shed in buildFarmStructures
old_farm_structures = """  function buildFarmStructures() {
    // Farm House & Shed
    const shedGroup = new THREE.Group();
    const wallGeo = new THREE.BoxGeometry(9, 4.8, 6.5);
    const wallMat = new THREE.MeshStandardMaterial({ map: PBRTextures.woodPlank, roughness: 0.8 });
    const walls = new THREE.Mesh(wallGeo, wallMat);
    walls.position.y = 2.4;
    walls.castShadow = true;
    shedGroup.add(walls);

    // Corrugated pitched roof
    const roofGeo = new THREE.ConeGeometry(6.6, 2.8, 4);
    roofGeo.rotateY(Math.PI / 4);
    const roofMat = new THREE.MeshStandardMaterial({ color: 0xb91c1c, roughness: 0.5, metalness: 0.3 });
    const roof = new THREE.Mesh(roofGeo, roofMat);
    roof.position.y = 6.0;
    roof.castShadow = true;
    shedGroup.add(roof);

    // Front porch pillars
    const pillarGeo = new THREE.CylinderGeometry(0.12, 0.12, 3.2, 6);
    const pillarMat = new THREE.MeshStandardMaterial({ color: 0x334155 });
    const p1 = new THREE.Mesh(pillarGeo, pillarMat);
    p1.position.set(3.8, 1.6, 3.8);
    const p2 = new THREE.Mesh(pillarGeo, pillarMat);
    p2.position.set(-3.8, 1.6, 3.8);
    shedGroup.add(p1); shedGroup.add(p2);

    shedGroup.position.set(138, 0, 115);
    threeScene.add(shedGroup);

    // Production Watchtower Machan & Crop Field GLBs
    if (window.THREE && typeof THREE.GLTFLoader === 'function') {
      const loader = new THREE.GLTFLoader();
      loader.load('assets/environment/farmland/watchtower_machan.glb', (gltf) => {
        const machan = gltf.scene;
        machan.name = 'Blender_Watchtower_Machan';
        machan.position.set(118, getTerrainElevation(118, 102), 102);
        machan.scale.set(1.1, 1.1, 1.1);
        machan.traverse((c) => { if (c.isMesh) { c.castShadow = true; c.receiveShadow = true; } });
        threeScene.add(machan);
        console.log('[PRW-Wild] Loaded Blender Production Watchtower Machan GLB');
      }, undefined, (e) => { console.warn('[PRW-Wild] Machan note:', e); });

      loader.load('assets/environment/farmland/crop_field.glb', (gltf) => {
        const cropsNorth = gltf.scene;
        cropsNorth.name = 'Blender_Crop_Field_North';
        cropsNorth.position.set(145, getTerrainElevation(145, 75), 75);
        cropsNorth.traverse((c) => { if (c.isMesh) { c.receiveShadow = true; c.castShadow = true; } });
        threeScene.add(cropsNorth);

        const cropsSouth = cropsNorth.clone();
        cropsSouth.name = 'Blender_Crop_Field_South';
        cropsSouth.position.set(145, getTerrainElevation(145, 145), 145);
        threeScene.add(cropsSouth);
        console.log('[PRW-Wild] Loaded Blender Production Crop Field Parcels');
      }, undefined, (e) => { console.warn('[PRW-Wild] Crop parcel note:', e); });
    }
  }"""

new_farm_structures = """  function buildFarmStructures() {
    // Production Watchtower Machan (Authentic Timber Observation Platform)
    if (window.THREE && typeof THREE.GLTFLoader === 'function') {
      const loader = new THREE.GLTFLoader();
      loader.load('assets/environment/farmland/watchtower_machan.glb', (gltf) => {
        const machan = gltf.scene;
        machan.name = 'Blender_Watchtower_Machan';
        machan.position.set(118, getTerrainElevation(118, 102), 102);
        machan.scale.set(1.15, 1.15, 1.15);
        machan.traverse((c) => { if (c.isMesh) { c.castShadow = true; c.receiveShadow = true; } });
        threeScene.add(machan);
        console.log('[PRW-Wild] Loaded Blender Production Watchtower Machan GLB');
      }, undefined, (e) => { console.warn('[PRW-Wild] Machan note:', e); });
    }
  }"""

if old_farm_structures in content:
    content = content.replace(old_farm_structures, new_farm_structures, 1)
    print("[4] Crude red-cone shed and duplicate crop boxes removed.")

# 5. Remove crude caneStalk stick loops & duplicate crop field loader in buildContinuousTerrain
old_crop_loops = """    // =========================================================================
    // 4. ORGANIC SUGARCANE CROPS & FARMLAND VEGETATION (NO FLOATING PLANKS)
    // =========================================================================
    const cropGroup = new THREE.Group();
    cropGroup.name = 'Organic_Sugarcane_Farmland_Group';
    const caneStalkGeo = new THREE.CylinderGeometry(0.045, 0.055, 1.8, 6);
    const caneStalkMat = new THREE.MeshStandardMaterial({ color: 0x65a30d, roughness: 0.7 });
    const caneLeafGeo = new THREE.ConeGeometry(0.35, 0.9, 4);
    const caneLeafMat = new THREE.MeshStandardMaterial({ color: 0x4d7c0f, roughness: 0.65 });

    for (let z = 25; z <= 175; z += 9) {
      for (let cx = 115; cx <= 185; cx += 8) {
        const cgy = getTerrainElevation(cx, z);
        const cluster = new THREE.Group();
        cluster.position.set(cx, cgy, z);

        for (let s = 0; s < 4; s++) {
          const ox = (Math.random() - 0.5) * 1.2;
          const oz = (Math.random() - 0.5) * 1.2;
          const stalk = new THREE.Mesh(caneStalkGeo, caneStalkMat);
          stalk.position.set(ox, 0.9, oz);
          stalk.rotation.z = (Math.random() - 0.5) * 0.15;
          stalk.castShadow = true;
          cluster.add(stalk);

          const leaf = new THREE.Mesh(caneLeafGeo, caneLeafMat);
          leaf.position.set(ox, 1.85, oz);
          leaf.rotation.y = Math.random() * Math.PI * 2;
          cluster.add(leaf);
        }
        cropGroup.add(cluster);
      }
    }
    threeScene.add(cropGroup);

    // Load Organic Blender Crop Field GLB if available
    if (window.THREE && typeof THREE.GLTFLoader === 'function') {
      const cropLoader = new THREE.GLTFLoader();
      cropLoader.load('assets/environment/farmland/crop_field.glb', (gltf) => {
        const cropsNorth = gltf.scene;
        cropsNorth.name = 'Blender_Crop_Field_North';
        cropsNorth.position.set(145, getTerrainElevation(145, 75), 75);
        cropsNorth.traverse((c) => { if (c.isMesh) { c.receiveShadow = true; c.castShadow = true; } });
        threeScene.add(cropsNorth);

        const cropsSouth = cropsNorth.clone();
        cropsSouth.name = 'Blender_Crop_Field_South';
        cropsSouth.position.set(145, getTerrainElevation(145, 145), 145);
        threeScene.add(cropsSouth);
      }, undefined, () => {});
    }"""

new_crop_clean = """    // Farmland soil terrain is rendered with high-resolution PBR agricultural soil maps."""

if old_crop_loops in content:
    content = content.replace(old_crop_loops, new_crop_clean, 1)
    print("[5] Crude sugarcane sticks and crop slabs eradicated.")

# 6. Remove duplicate pond_basin.glb loader in initMultiAnimalEcosystem
old_dup_pond = """    // Production Carved Pond Basin GLB (Blender Production World)
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
        basinSouth.traverse((c) => { if (c.isMesh) { c.receiveShadow = true; } });
        threeScene.add(basinSouth);

        console.log('[PRW-Wild] Loaded Blender Production Carved Pond Basins');
      }, undefined, (e) => { console.warn('[PRW-Wild] Pond basin note:', e); });
    }"""

new_dup_pond = """    // Pond basins are loaded once with proper ground-level shoreline boulders in buildContinuousTerrain."""

if old_dup_pond in content:
    content = content.replace(old_dup_pond, new_dup_pond, 1)
    print("[6] Duplicate pond basin loader removed.")

with open(APP_JS, "w", encoding="utf-8") as f:
    f.write(content)

print("Successfully written changes to app.js!")

