app_path = r"D:\Simulation For DT\prw-wild-digital-twin\src\prw_wild\web\static\app.js"
with open(app_path, "r", encoding="utf-8") as f:
    text = f.read()

old_forest = """    // 2. High-Fidelity Blender GLB Forest Asset Loading
    if (window.THREE && typeof THREE.GLTFLoader === 'function') {
      const loader = new THREE.GLTFLoader();
      const glbAssets = [
        { id: 'sal', url: 'assets/environment/trees/sal_mature.glb' },
        { id: 'banyan', url: 'assets/environment/trees/banyan_fig.glb' },
        { id: 'acacia', url: 'assets/environment/trees/acacia_canopy.glb' },
        { id: 'mango', url: 'assets/environment/fruit_trees/mango_fruit_tree.glb' },
        { id: 'fern', url: 'assets/environment/vegetation/forest_ferns.glb' },
        { id: 'shrub', url: 'assets/environment/vegetation/forest_shrub.glb' },
        { id: 'grass', url: 'assets/environment/grass/tall_grass_clump.glb' },
      ];

      glbAssets.forEach(({ id, url }) => {
        loader.load(url, (gltf) => {
          if (id === 'fern') {
            const fernPositions = [[22, 45], [35, 52], [50, 36], [25, 75], [38, 80], [60, 72], [30, 162], [45, 142], [62, 166]];
            fernPositions.forEach(([fx, fz]) => {
              const inst = gltf.scene.clone();
              inst.position.set(fx, getTerrainElevation(fx, fz), fz);
              inst.scale.set(1.2, 1.2, 1.2);
              inst.rotation.y = Math.random() * Math.PI * 2;
              forestContainer.add(inst);
            });
          } else if (id === 'grass') {
            const grassPositions = [[18, 35], [26, 88], [42, 130], [55, 140], [32, 170], [62, 160]];
            grassPositions.forEach(([gx, gz]) => {
              const inst = gltf.scene.clone();
              inst.position.set(gx, getTerrainElevation(gx, gz), gz);
              inst.scale.set(1.4, 1.4, 1.4);
              inst.rotation.y = Math.random() * Math.PI * 2;
              forestContainer.add(inst);
            });
          }
        }, undefined, () => {});
      });
    }"""

new_forest = """    // 2. High-Fidelity Blender GLB Forest Asset Loading & Instantiation
    if (window.THREE && typeof THREE.GLTFLoader === 'function') {
      const loader = new THREE.GLTFLoader();
      const glbAssets = [
        { id: 'sal', url: 'assets/environment/trees/sal_mature.glb' },
        { id: 'banyan', url: 'assets/environment/trees/banyan_fig.glb' },
        { id: 'acacia', url: 'assets/environment/trees/acacia_canopy.glb' },
        { id: 'mango', url: 'assets/environment/fruit_trees/mango_fruit_tree.glb' },
        { id: 'fern', url: 'assets/environment/vegetation/forest_ferns.glb' },
        { id: 'shrub', url: 'assets/environment/vegetation/forest_shrub.glb' },
        { id: 'grass', url: 'assets/environment/grass/tall_grass_clump.glb' },
      ];

      glbAssets.forEach(({ id, url }) => {
        loader.load(url, (gltf) => {
          console.log(`[PRW-Wild] Loaded environment asset: ${id}`);
          if (id === 'sal' || id === 'banyan' || id === 'acacia' || id === 'mango') {
            // Instantiate real Blender tree model at every matching coordinate
            treePositions.filter(tp => tp[2] === id).forEach(([tx, tz]) => {
              const inst = gltf.scene.clone(true);
              const gy = getTerrainElevation(tx, tz);
              inst.position.set(tx, gy, tz);
              const sVar = 0.9 + Math.random() * 0.35;
              inst.scale.set(sVar, sVar, sVar);
              inst.rotation.y = Math.random() * Math.PI * 2;
              inst.traverse(c => {
                if (c.isMesh) {
                  c.castShadow = true;
                  c.receiveShadow = true;
                  if (c.material) {
                    c.material.roughness = 0.82;
                  }
                }
              });
              forestContainer.add(inst);
            });
            // Hide primitive placeholder trees once real GLB trees are attached
            if (organicTreeGroup && organicTreeGroup.parent) {
              forestContainer.remove(organicTreeGroup);
            }
          } else if (id === 'shrub') {
            const shrubPositions = [
              [12, 32], [22, 28], [35, 45], [48, 26], [62, 34],
              [18, 62], [32, 58], [45, 68], [58, 52], [72, 45],
              [15, 145], [28, 155], [42, 138], [58, 152], [75, 162],
              [24, 182], [38, 172], [52, 185], [68, 176], [82, 165],
              [16, 92], [26, 85], [40, 98], [56, 90], [70, 82],
              [84, 95], [88, 65], [86, 125], [78, 132], [65, 142]
            ];
            shrubPositions.forEach(([sx, sz]) => {
              const inst = gltf.scene.clone(true);
              inst.position.set(sx, getTerrainElevation(sx, sz), sz);
              const sc = 0.85 + Math.random() * 0.45;
              inst.scale.set(sc, sc, sc);
              inst.rotation.y = Math.random() * Math.PI * 2;
              inst.traverse(c => { if (c.isMesh) { c.castShadow = true; c.receiveShadow = true; } });
              forestContainer.add(inst);
            });
          } else if (id === 'fern') {
            const fernPositions = [
              [22, 45], [35, 52], [50, 36], [25, 75], [38, 80], [60, 72],
              [30, 162], [45, 142], [62, 166], [70, 135], [78, 142], [42, 58],
              [48, 64], [52, 55], [68, 145], [74, 152], [20, 130], [28, 110]
            ];
            fernPositions.forEach(([fx, fz]) => {
              const inst = gltf.scene.clone(true);
              inst.position.set(fx, getTerrainElevation(fx, fz), fz);
              const sc = 1.0 + Math.random() * 0.4;
              inst.scale.set(sc, sc, sc);
              inst.rotation.y = Math.random() * Math.PI * 2;
              inst.traverse(c => { if (c.isMesh) { c.castShadow = true; c.receiveShadow = true; } });
              forestContainer.add(inst);
            });
          } else if (id === 'grass') {
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
          }
        }, undefined, () => {});
      });
    }"""

assert old_forest in text, "old_forest block not found"
text = text.replace(old_forest, new_forest, 1)

with open(app_path, "w", encoding="utf-8") as f:
    f.write(text)

print("SUCCESS: Upgraded buildDiverseForest to instantiate real 3D GLB trees, shrubs, and ground vegetation")

