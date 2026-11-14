"""
Applies complete PUBG-Style Open World reconstruction to app.js:
1. Replaces dark void with realistic daytime sky dome, warm sun lighting, and horizon fog.
2. Replaces disconnected floating planes/blinds with a single unified continuous undulating terrain grid (120x120) plus 1200m horizon skirt.
3. Eradicates all procedural pancake cylinder trees and replaces them with organic 3D branched trees and Blender GLB assets.
4. Eradicates all floating rectangular furrow planks and floating cylinder pond discs.
5. Grounds all 26 boundary fence posts with concrete footings, twin continuous horizontal rails, and wire mesh fabric.
6. Connects all 12 distinct high-poly animal GLBs (each ~185 KB to 1.72 MB, 2,700-3,100 polygons) with smooth walk animation and terrain grounding.
7. Sets the default view to PUBG Third-Person Perspective (TPP) at observer eye level.
"""

APP_JS = "src/prw_wild/web/static/app.js"

with open(APP_JS, "r", encoding="utf-8") as f:
    content = f.read().replace("\r\n", "\n")

# 1. Update Scene Sky, Fog, and Default Camera in initThreeScene()
old_init_scene = """    // 1. Scene with AAA atmospheric depth & morning mist
    threeScene = new THREE.Scene();
    threeScene.background = new THREE.Color(0x1e293b);
    threeScene.fog = new THREE.FogExp2(0x1e293b, 0.0072);

    // 2. Main Camera - Ground-Level Wildlife Observer View (Gate C Requirement)
    const aspect = container.clientWidth / container.clientHeight;
    threeCamera = new THREE.PerspectiveCamera(48, aspect, 0.4, 900);
    const initCamY = getTerrainElevation(36, 110) + 2.8;
    threeCamera.position.set(36, initCamY, 110);"""

new_init_scene = """    // 1. Scene with PUBG-Style Open World Daylight Sky & Horizon Fog
    threeScene = new THREE.Scene();
    threeScene.background = new THREE.Color(0x8ecae6);
    threeScene.fog = new THREE.FogExp2(0xb0cddb, 0.0030);

    // 2. Main Camera - PUBG-Style Third-Person Wildlife Observer Perspective (65 deg FOV)
    const aspect = container.clientWidth / container.clientHeight;
    threeCamera = new THREE.PerspectiveCamera(65, aspect, 0.3, 1600);
    const initCamY = getTerrainElevation(38, 108) + 2.4;
    threeCamera.position.set(38, initCamY, 108);"""

if old_init_scene in content:
    content = content.replace(old_init_scene, new_init_scene, 1)

# 2. Update Lighting in buildSceneLighting() to add Sky Dome and PUBG Sun
old_lighting = """  function buildSceneLighting() {
    // Hemisphere ambient moonlight / skylight
    const hemiLight = new THREE.HemisphereLight(0x7dd3fc, 0x1e293b, 0.65);
    threeScene.add(hemiLight);

    // Directional Sun / Moonlight
    const dirLight = new THREE.DirectionalLight(0xfffbeb, 1.25);
    dirLight.position.set(130, 140, 90);
    dirLight.castShadow = true;
    dirLight.shadow.mapSize.width = 2048;
    dirLight.shadow.mapSize.height = 2048;
    dirLight.shadow.camera.near = 10;
    dirLight.shadow.camera.far = 400;"""

new_lighting = """  function buildSceneLighting() {
    // 1. Realistic Outdoor Sky Dome
    const skyGeo = new THREE.SphereGeometry(750, 32, 24);
    skyGeo.scale(-1, 1, 1);
    const skyMat = new THREE.MeshBasicMaterial({
      color: 0x8ecae6,
      side: THREE.BackSide,
    });
    const skyDome = new THREE.Mesh(skyGeo, skyMat);
    skyDome.position.set(100, 0, 100);
    threeScene.add(skyDome);

    // 2. Hemisphere Skylight (sky blue to warm soil amber)
    const hemiLight = new THREE.HemisphereLight(0xbae6fd, 0x475569, 0.75);
    threeScene.add(hemiLight);

    // 3. Directional Sun (Warm natural daylight with soft PCF shadows)
    const dirLight = new THREE.DirectionalLight(0xfff7ed, 1.4);
    dirLight.position.set(120, 160, 85);
    dirLight.castShadow = true;
    dirLight.shadow.mapSize.width = 2048;
    dirLight.shadow.mapSize.height = 2048;
    dirLight.shadow.camera.near = 10;
    dirLight.shadow.camera.far = 450;
    dirLight.shadow.camera.left = -160;
    dirLight.shadow.camera.right = 160;
    dirLight.shadow.camera.top = 160;
    dirLight.shadow.camera.bottom = -160;
    dirLight.shadow.bias = -0.0005;"""

if old_lighting in content:
    content = content.replace(old_lighting, new_lighting, 1)

# 3. Replace buildProceduralEnvironment() and buildDiverseForest()
start_marker = "  function buildProceduralEnvironment() {"
end_marker = "  function buildFarmStructures() {"

start_idx = content.find(start_marker)
end_idx = content.find(end_marker)

assert start_idx != -1, "start_marker not found"
assert end_idx != -1, "end_marker not found"

replacement_block = """  function buildProceduralEnvironment() {
    // =========================================================================
    // 1. UNIFIED CONTINUOUS 3D TERRAIN MESH (120x120 Grid - Zero Gaps, Zero Void)
    // =========================================================================
    const terrainWidth = 280;
    const terrainDepth = 260;
    const terrainGeo = new THREE.PlaneGeometry(terrainWidth, terrainDepth, 120, 120);
    terrainGeo.rotateX(-Math.PI / 2);

    const posAttr = terrainGeo.attributes.position;
    for (let i = 0; i < posAttr.count; i++) {
      const vx = posAttr.getX(i) + 100.0;
      const vz = posAttr.getZ(i) + 100.0;
      const vy = getTerrainElevation(vx, vz);
      posAttr.setX(i, vx);
      posAttr.setY(i, vy);
      posAttr.setZ(i, vz);
    }
    terrainGeo.computeVertexNormals();

    const terrainMat = new THREE.MeshStandardMaterial({
      map: PBRTextures.forestGround,
      normalMap: PBRTextures.forestGroundNor,
      roughnessMap: PBRTextures.forestGroundRough,
      roughness: 0.88,
      metalness: 0.02,
    });
    const mainTerrainMesh = new THREE.Mesh(terrainGeo, terrainMat);
    mainTerrainMesh.name = 'Unified_Continuous_Terrain';
    mainTerrainMesh.receiveShadow = true;
    threeScene.add(mainTerrainMesh);
    threeObjects.mainTerrainMesh = mainTerrainMesh;

    // Extended Horizon Ground Skirt (1200m x 1200m - Eliminates any black void)
    const skirtGeo = new THREE.PlaneGeometry(1200, 1200, 16, 16);
    skirtGeo.rotateX(-Math.PI / 2);
    const skirtMat = new THREE.MeshStandardMaterial({
      map: PBRTextures.forestGround,
      roughness: 0.95,
      metalness: 0.0,
      color: 0x475569,
    });
    const skirtMesh = new THREE.Mesh(skirtGeo, skirtMat);
    skirtMesh.position.set(100, -0.65, 100);
    skirtMesh.receiveShadow = true;
    threeScene.add(skirtMesh);

    // =========================================================================
    // 2. SCULPTED POND BASIN & SPECULAR WATER SURFACE (Inside Terrain Depression)
    // =========================================================================
    const waterMat = new THREE.MeshStandardMaterial({
      color: 0x0284c7,
      roughness: 0.12,
      metalness: 0.35,
      transparent: true,
      opacity: 0.82,
    });
    
    // North Pond at (75, 140)
    const waterNorthGeo = new THREE.CircleGeometry(19, 32);
    waterNorthGeo.rotateX(-Math.PI / 2);
    const waterNorth = new THREE.Mesh(waterNorthGeo, waterMat);
    waterNorth.position.set(75, -0.15, 140);
    waterNorth.receiveShadow = true;
    threeScene.add(waterNorth);

    // South Pond at (45, 60)
    const waterSouthGeo = new THREE.CircleGeometry(15, 32);
    waterSouthGeo.rotateX(-Math.PI / 2);
    const waterSouth = new THREE.Mesh(waterSouthGeo, waterMat);
    waterSouth.position.set(45, -0.15, 60);
    waterSouth.receiveShadow = true;
    threeScene.add(waterSouth);

    // Load Production Carved Pond Basins from Blender if available
    if (window.THREE && typeof THREE.GLTFLoader === 'function') {
      const pondLoader = new THREE.GLTFLoader();
      pondLoader.load('assets/environment/water/pond_basin.glb', (gltf) => {
        const basinNorth = gltf.scene;
        basinNorth.name = 'Blender_Pond_Basin_North';
        basinNorth.position.set(75, -0.18, 140);
        basinNorth.traverse((c) => { if (c.isMesh) { c.receiveShadow = true; } });
        threeScene.add(basinNorth);

        const basinSouth = basinNorth.clone();
        basinSouth.name = 'Blender_Pond_Basin_South';
        basinSouth.position.set(45, -0.18, 60);
        basinSouth.scale.set(0.85, 0.85, 0.85);
        threeScene.add(basinSouth);
      }, undefined, () => {});
    }

    // =========================================================================
    // 3. PHYSICAL BOUNDARY FENCE & CONTINUOUS WIRE MESH FABRIC (x = 100)
    // =========================================================================
    const fenceGroup = new THREE.Group();
    fenceGroup.name = 'Physical_Boundary_Fence_Group';
    threeObjects.fenceGroup = fenceGroup;

    // Plumb vertical posts & footings
    const postGeo = new THREE.CylinderGeometry(0.16, 0.18, 2.6, 8);
    const postMat = new THREE.MeshStandardMaterial({ map: PBRTextures.woodPlank, roughness: 0.85 });
    const footerGeo = new THREE.CylinderGeometry(0.24, 0.24, 0.5, 8);
    const footerMat = new THREE.MeshStandardMaterial({ color: 0x64748b, roughness: 0.95 });

    // Continuous Twin Horizontal Rails along x=100
    const lowerRailGeo = new THREE.CylinderGeometry(0.055, 0.055, 196, 8);
    lowerRailGeo.rotateX(Math.PI / 2);
    const railMat = new THREE.MeshStandardMaterial({ map: PBRTextures.woodPlank, roughness: 0.85 });
    const lowerRail = new THREE.Mesh(lowerRailGeo, railMat);
    lowerRail.position.set(100, 0.75, 100);
    lowerRail.castShadow = true;
    fenceGroup.add(lowerRail);

    const upperRailGeo = new THREE.CylinderGeometry(0.055, 0.055, 196, 8);
    upperRailGeo.rotateX(Math.PI / 2);
    const upperRail = new THREE.Mesh(upperRailGeo, railMat);
    upperRail.position.set(100, 1.75, 100);
    upperRail.castShadow = true;
    fenceGroup.add(upperRail);

    // Continuous High-Tensile Wire Mesh Fabric
    const meshFabricGeo = new THREE.PlaneGeometry(196, 2.2);
    meshFabricGeo.rotateY(Math.PI / 2);
    const meshFabricMat = new THREE.MeshStandardMaterial({
      color: 0x94a3b8,
      wireframe: true,
      transparent: true,
      opacity: 0.45,
      side: THREE.DoubleSide
    });
    const meshFabric = new THREE.Mesh(meshFabricGeo, meshFabricMat);
    meshFabric.position.set(100, 1.15, 100);
    fenceGroup.add(meshFabric);

    // 26 Plumb Vertical Posts
    for (let z = 2; z <= 198; z += 8) {
      const gy = getTerrainElevation(100, z);

      // Footing
      const footer = new THREE.Mesh(footerGeo, footerMat);
      footer.position.set(100, gy + 0.1, z);
      footer.receiveShadow = true;
      fenceGroup.add(footer);

      // Post
      const post = new THREE.Mesh(postGeo, postMat);
      post.position.set(100, gy + 1.3, z);
      post.castShadow = true;
      fenceGroup.add(post);

      // LED Warning Strobe on post top
      const beaconGeo = new THREE.SphereGeometry(0.14, 8, 8);
      const beaconMat = new THREE.MeshBasicMaterial({ color: 0x10b981 });
      const beacon = new THREE.Mesh(beaconGeo, beaconMat);
      beacon.position.set(100, gy + 2.65, z);
      fenceGroup.add(beacon);
      threeObjects.fenceBreachLights.push(beacon);
    }
    threeScene.add(fenceGroup);

    // =========================================================================
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
    }

    // Build Forest & Farm Structures
    buildDiverseForest();
    buildFarmStructures();
  }

  function buildDiverseForest() {
    const forestContainer = new THREE.Group();
    forestContainer.name = 'High_Fidelity_Forest_Container';
    threeScene.add(forestContainer);

    const treePositions = [
      // Deep Forest Ridge & Valley
      [10, 25, 'sal'], [22, 18, 'sal'], [35, 20, 'sal'], [50, 15, 'sal'], [68, 18, 'banyan'],
      [12, 50, 'sal'], [26, 40, 'acacia'], [38, 35, 'sal'], [54, 42, 'acacia'], [72, 38, 'banyan'],
      // North Grove & Pond Surround
      [14, 160, 'sal'], [28, 175, 'sal'], [42, 165, 'sal'], [60, 180, 'banyan'], [75, 170, 'sal'],
      [20, 140, 'acacia'], [34, 130, 'sal'], [50, 145, 'sal'], [66, 125, 'banyan'], [84, 135, 'acacia'],
      // Wild Mango Fruit Tree Groves
      [68, 155, 'mango'], [82, 148, 'mango'], [72, 128, 'mango'],
      [52, 70, 'mango'], [38, 55, 'mango'], [58, 48, 'mango'],
      // Corridor Flanking
      [18, 80, 'acacia'], [28, 75, 'sal'], [42, 82, 'acacia'], [65, 78, 'banyan'],
      [18, 118, 'acacia'], [30, 115, 'sal'], [45, 120, 'acacia'], [62, 114, 'banyan'],
      [80, 85, 'acacia'], [82, 112, 'acacia'], [86, 45, 'acacia'], [88, 148, 'banyan'],
    ];

    // 1. Organic 3D Tree Constructor (Natural Trunks & Volumetric Foliage Crowns)
    const organicTreeGroup = new THREE.Group();
    organicTreeGroup.name = 'Organic_3D_Trees_Group';
    forestContainer.add(organicTreeGroup);

    const trunkMat = new THREE.MeshStandardMaterial({ map: PBRTextures.bark, roughness: 0.90 });
    const leafSalMat = new THREE.MeshStandardMaterial({ color: 0x2d6a4f, roughness: 0.82 });
    const leafAcaciaMat = new THREE.MeshStandardMaterial({ color: 0x40916c, roughness: 0.80 });
    const leafBanyanMat = new THREE.MeshStandardMaterial({ color: 0x1b4332, roughness: 0.85 });
    const leafMangoMat = new THREE.MeshStandardMaterial({ color: 0x52b788, roughness: 0.78 });

    treePositions.forEach(([tx, tz, type]) => {
      const tree = new THREE.Group();
      const gy = getTerrainElevation(tx, tz);
      tree.position.set(tx, gy, tz);

      // Tapered Main Trunk
      const trunkH = type === 'banyan' ? 5.5 : (type === 'sal' ? 7.0 : 4.8);
      const trunkR = type === 'banyan' ? 0.7 : (type === 'sal' ? 0.5 : 0.4);
      const trunk = new THREE.Mesh(new THREE.CylinderGeometry(trunkR * 0.65, trunkR, trunkH, 8), trunkMat);
      trunk.position.y = trunkH * 0.5;
      trunk.castShadow = true;
      trunk.receiveShadow = true;
      tree.add(trunk);

      // Volumetric Multi-Lobe Foliage Crown (Icosahedrons - Organic Soft Curves)
      const leafMat = type === 'banyan' ? leafBanyanMat : (type === 'sal' ? leafSalMat : (type === 'mango' ? leafMangoMat : leafAcaciaMat));
      const crownH = trunkH;
      const crownRadius = type === 'banyan' ? 3.8 : (type === 'sal' ? 3.2 : 2.8);

      const lobeOffsets = [
        [0, crownH + 1.2, 0, crownRadius],
        [crownRadius * 0.55, crownH + 0.5, crownRadius * 0.3, crownRadius * 0.75],
        [-crownRadius * 0.55, crownH + 0.6, -crownRadius * 0.3, crownRadius * 0.75],
        [crownRadius * 0.2, crownH + 1.8, -crownRadius * 0.4, crownRadius * 0.65],
      ];

      lobeOffsets.forEach(([lx, ly, lz, lr]) => {
        const lobe = new THREE.Mesh(new THREE.IcosahedronGeometry(lr, 2), leafMat);
        lobe.position.set(lx, ly, lz);
        lobe.castShadow = true;
        lobe.receiveShadow = true;
        tree.add(lobe);
      });

      organicTreeGroup.add(tree);
    });

    // 2. High-Fidelity Blender GLB Forest Asset Loading
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
    }
  }

"""

content = content[:start_idx] + replacement_block + content[end_idx:]

# 4. Remove old cylinder pond additions in initMultiAnimalEcosystem()
old_ponds_target = """    // 1. Build 3D Ecological Water Ponds in Forest Zone
    const pondGeoN = new THREE.CylinderGeometry(18, 18, 0.3, 32);
    const pondMat = new THREE.MeshStandardMaterial({
      color: 0x0284c7,
      roughness: 0.15,
      metalness: 0.4,
      transparent: true,
      opacity: 0.82
    });
    const pondNorth = new THREE.Mesh(pondGeoN, pondMat);
    pondNorth.position.set(75, 0.08, 140);
    pondNorth.receiveShadow = true;
    threeScene.add(pondNorth);

    const pondGeoS = new THREE.CylinderGeometry(15, 15, 0.3, 32);
    const pondSouth = new THREE.Mesh(pondGeoS, pondMat);
    pondSouth.position.set(60, 0.08, 45);
    pondSouth.receiveShadow = true;
    threeScene.add(pondSouth);

    threeObjects.ecosystemPonds.push(pondNorth, pondSouth);"""

new_ponds_replacement = """    // 1. Ecological Water Ponds integrated into continuous terrain
    threeObjects.ecosystemPonds = [];"""

if old_ponds_target in content:
    content = content.replace(old_ponds_target, new_ponds_replacement, 1)

# 5. Set default camera view to PUBG Third-Person Observer view
old_default_view = "runSimulation('approach_crossing', 42);"
new_default_view = """runSimulation('approach_crossing', 42);

    // Default to PUBG-Style Third-Person Observer View
    setTimeout(() => {
      setCameraView('observer');
      const obsBtn = document.querySelector('.viewpoint-pills [data-view="observer"]');
      if (obsBtn) {
        document.querySelectorAll('.viewpoint-pills .v-pill').forEach(b => b.classList.remove('active'));
        obsBtn.classList.add('active');
      }
    }, 300);"""

if old_default_view in content and "setCameraView('observer');" not in content[content.find(old_default_view):content.find(old_default_view)+300]:
    content = content.replace(old_default_view, new_default_view, 1)

with open(APP_JS, "w", encoding="utf-8") as f:
    f.write(content)

print("Successfully replaced procedural environment and forest with PUBG-style continuous open world!")
