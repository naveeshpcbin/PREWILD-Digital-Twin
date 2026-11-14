import re

with open("src/prw_wild/web/static/app.js", "r", encoding="utf-8") as f:
    code = f.read().replace("\r\n", "\n")

# 1. Update SPECIES_VISUAL_CONFIGS
old_species_configs = """  const SPECIES_VISUAL_CONFIGS = {
    asian_elephant: { scale: 1.0, color: 0x8c8d8f, glb: 'assets/animals/asian_elephant_production.glb', yOffset: 0.0 },
    chital_deer: { scale: 1.1, color: 0xc88242, glb: 'assets/animals/chital_deer.glb', yOffset: 0.0 },
    sambar_deer: { scale: 1.25, color: 0x5a3e2b, glb: 'assets/animals/sambar_deer.glb', yOffset: 0.0 },
    wild_boar: { scale: 1.0, color: 0x383432, glb: 'assets/animals/wild_boar.glb', yOffset: 0.0 },
    gaur_bison: { scale: 1.2, color: 0x241d19, glb: 'assets/animals/gaur_bison.glb', yOffset: 0.0 },
    bonnet_macaque: { scale: 0.85, color: 0x8a7760, glb: 'assets/animals/bonnet_macaque.glb', yOffset: 0.0 },
  };"""

new_species_configs = """  const SPECIES_VISUAL_CONFIGS = {
    // 12 Distinct Biologically Rigged & Textured Wildlife Variants
    asian_elephant_bull: { scale: 1.0, color: 0x8c8d8f, glb: 'assets/animals/asian_elephant_bull.glb', yOffset: 0.0 },
    asian_elephant_cow: { scale: 0.95, color: 0x828385, glb: 'assets/animals/asian_elephant_cow.glb', yOffset: 0.0 },
    chital_stag: { scale: 1.15, color: 0xc88242, glb: 'assets/animals/chital_stag.glb', yOffset: 0.0 },
    chital_hind: { scale: 1.05, color: 0xc47e3e, glb: 'assets/animals/chital_hind.glb', yOffset: 0.0 },
    sambar_stag: { scale: 1.30, color: 0x5a3e2b, glb: 'assets/animals/sambar_stag.glb', yOffset: 0.0 },
    sambar_cow: { scale: 1.20, color: 0x543a28, glb: 'assets/animals/sambar_cow.glb', yOffset: 0.0 },
    wild_boar_razorback: { scale: 1.05, color: 0x383432, glb: 'assets/animals/wild_boar_razorback.glb', yOffset: 0.0 },
    wild_boar_sow: { scale: 0.95, color: 0x332f2e, glb: 'assets/animals/wild_boar_sow.glb', yOffset: 0.0 },
    gaur_bull: { scale: 1.25, color: 0x241d19, glb: 'assets/animals/gaur_bull.glb', yOffset: 0.0 },
    gaur_cow: { scale: 1.15, color: 0x28201b, glb: 'assets/animals/gaur_cow.glb', yOffset: 0.0 },
    bonnet_macaque_alpha: { scale: 0.90, color: 0x8a7760, glb: 'assets/animals/bonnet_macaque_alpha.glb', yOffset: 0.0 },
    bonnet_macaque_forager: { scale: 0.80, color: 0x82705a, glb: 'assets/animals/bonnet_macaque_forager.glb', yOffset: 0.0 },

    // Base Species Keys for Backward Compatibility
    asian_elephant: { scale: 1.0, color: 0x8c8d8f, glb: 'assets/animals/asian_elephant_production.glb', yOffset: 0.0 },
    chital_deer: { scale: 1.1, color: 0xc88242, glb: 'assets/animals/chital_deer.glb', yOffset: 0.0 },
    sambar_deer: { scale: 1.25, color: 0x5a3e2b, glb: 'assets/animals/sambar_deer.glb', yOffset: 0.0 },
    wild_boar: { scale: 1.0, color: 0x383432, glb: 'assets/animals/wild_boar.glb', yOffset: 0.0 },
    gaur_bison: { scale: 1.2, color: 0x241d19, glb: 'assets/animals/gaur_bison.glb', yOffset: 0.0 },
    bonnet_macaque: { scale: 0.85, color: 0x8a7760, glb: 'assets/animals/bonnet_macaque.glb', yOffset: 0.0 },
  };"""

assert old_species_configs in code, "old_species_configs not found"
code = code.replace(old_species_configs, new_species_configs, 1)

# 2. Update spawnAnimalPopulationMeshes to use model_variant
old_spawn = """      if (speciesGlbTemplates[agent.species]) {
        const tmpl = speciesGlbTemplates[agent.species];
        modelMesh = tmpl.scene.clone(true);
        if (tmpl.animations && tmpl.animations.length > 0) {
          mixer = new THREE.AnimationMixer(modelMesh);
          const clip = tmpl.animations.find(a => a.name === 'Walk') || tmpl.animations[0];
          walkAction = mixer.clipAction(clip);
          walkAction.play();
        }
      } else {
        modelMesh = buildProceduralAnimalFallback(agent.species);
      }"""

new_spawn = """      const vKey = agent.model_variant || agent.species;
      const tmpl = speciesGlbTemplates[vKey] || speciesGlbTemplates[agent.species];
      if (tmpl) {
        modelMesh = tmpl.scene.clone(true);
        if (tmpl.animations && tmpl.animations.length > 0) {
          mixer = new THREE.AnimationMixer(modelMesh);
          const clip = tmpl.animations.find(a => a.name === 'Walk') || tmpl.animations[0];
          walkAction = mixer.clipAction(clip);
          walkAction.play();
        }
      } else {
        modelMesh = buildProceduralAnimalFallback(vKey);
      }"""

assert old_spawn in code, "old_spawn not found"
code = code.replace(old_spawn, new_spawn, 1)

# 3. Update mesh dictionary tracking with variant
old_mesh_dict = """        species: agent.species,
        targetPos: new THREE.Vector3(agent.position.x, elevY, agent.position.y),"""

new_mesh_dict = """        species: agent.species,
        variant: vKey,
        targetPos: new THREE.Vector3(agent.position.x, elevY, agent.position.y),"""

assert old_mesh_dict in code, "old_mesh_dict not found"
code = code.replace(old_mesh_dict, new_mesh_dict, 1)

# 4. Update refreshAnimalMeshesWithGlb to support variant keys
old_refresh = """  function refreshAnimalMeshesWithGlb(speciesKey) {
    if (!speciesGlbTemplates[speciesKey]) return;
    const tmpl = speciesGlbTemplates[speciesKey];

    Object.entries(threeObjects.multiAnimalMeshes).forEach(([aid, item]) => {
      if (item.species === speciesKey) {
        // Replace mesh
        item.group.remove(item.modelMesh);
        const newMesh = tmpl.scene.clone(true);
        item.group.add(newMesh);
        item.modelMesh = newMesh;

        if (tmpl.animations && tmpl.animations.length > 0) {
          item.mixer = new THREE.AnimationMixer(newMesh);
          const clip = tmpl.animations.find(a => a.name === 'Walk') || tmpl.animations[0];
          item.walkAction = item.mixer.clipAction(clip);
          item.walkAction.play();
        }
      }
    });
  }"""

new_refresh = """  function refreshAnimalMeshesWithGlb(key) {
    if (!speciesGlbTemplates[key]) return;
    const tmpl = speciesGlbTemplates[key];

    Object.entries(threeObjects.multiAnimalMeshes).forEach(([aid, item]) => {
      if (item.variant === key || (!item.variant && item.species === key)) {
        // Replace mesh
        item.group.remove(item.modelMesh);
        const newMesh = tmpl.scene.clone(true);
        item.group.add(newMesh);
        item.modelMesh = newMesh;

        if (tmpl.animations && tmpl.animations.length > 0) {
          item.mixer = new THREE.AnimationMixer(newMesh);
          const clip = tmpl.animations.find(a => a.name === 'Walk') || tmpl.animations[0];
          item.walkAction = item.mixer.clipAction(clip);
          item.walkAction.play();
        }
      }
    });
  }"""

assert old_refresh in code, "old_refresh not found"
code = code.replace(old_refresh, new_refresh, 1)

# 5. Add Continuous Twin Horizontal Rails and Terrain Grounding to Fence
old_fence_posts = """    // Heavy Timber Posts with Wire Tension and Warning Strobe Beacons
    const postGeo = new THREE.CylinderGeometry(0.18, 0.22, 2.6, 8);
    const postMat = new THREE.MeshStandardMaterial({ map: PBRTextures.woodPlank, roughness: 0.85 });

    for (let z = 5; z <= 195; z += 10) {
      const post = new THREE.Mesh(postGeo, postMat);
      post.position.set(100, 1.3, z);
      post.castShadow = true;
      fenceGroup.add(post);

      // Warning Strobe Beacon on post top
      const beaconGeo = new THREE.SphereGeometry(0.16, 8, 8);
      const beaconMat = new THREE.MeshBasicMaterial({ color: 0x10b981 });
      const beacon = new THREE.Mesh(beaconGeo, beaconMat);
      beacon.position.set(100, 2.65, z);
      fenceGroup.add(beacon);
      threeObjects.fenceBreachLights.push(beacon);
    }
    threeScene.add(fenceGroup);"""

new_fence_posts = """    // Heavy Timber Posts with Concrete Footings, Plumb Verticality & Strobe Beacons
    const postGeo = new THREE.CylinderGeometry(0.18, 0.22, 2.6, 8);
    const postMat = new THREE.MeshStandardMaterial({ map: PBRTextures.woodPlank, roughness: 0.85 });
    const footerGeo = new THREE.CylinderGeometry(0.26, 0.26, 0.5, 8);
    const footerMat = new THREE.MeshStandardMaterial({ color: 0x64748b, roughness: 0.95 });

    // Continuous Twin Horizontal Timber Rails connecting posts along x=100
    const lowerRailGeo = new THREE.CylinderGeometry(0.06, 0.06, 194, 8);
    lowerRailGeo.rotateX(Math.PI / 2);
    const railMat = new THREE.MeshStandardMaterial({ map: PBRTextures.woodPlank, roughness: 0.85 });
    const lowerRail = new THREE.Mesh(lowerRailGeo, railMat);
    lowerRail.position.set(100, 0.75, 100);
    lowerRail.castShadow = true;
    fenceGroup.add(lowerRail);

    const upperRailGeo = new THREE.CylinderGeometry(0.06, 0.06, 194, 8);
    upperRailGeo.rotateX(Math.PI / 2);
    const upperRail = new THREE.Mesh(upperRailGeo, railMat);
    upperRail.position.set(100, 1.75, 100);
    upperRail.castShadow = true;
    fenceGroup.add(upperRail);

    for (let z = 5; z <= 195; z += 8) {
      const gy = getTerrainElevation(100, z);

      // Concrete footing embedded into terrain
      const footer = new THREE.Mesh(footerGeo, footerMat);
      footer.position.set(100, gy + 0.1, z);
      footer.receiveShadow = true;
      fenceGroup.add(footer);

      // Plumb vertical fence post
      const post = new THREE.Mesh(postGeo, postMat);
      post.position.set(100, gy + 1.3, z);
      post.castShadow = true;
      fenceGroup.add(post);

      // Warning Strobe Beacon on post top
      const beaconGeo = new THREE.SphereGeometry(0.16, 8, 8);
      const beaconMat = new THREE.MeshBasicMaterial({ color: 0x10b981 });
      const beacon = new THREE.Mesh(beaconGeo, beaconMat);
      beacon.position.set(100, gy + 2.65, z);
      fenceGroup.add(beacon);
      threeObjects.fenceBreachLights.push(beacon);
    }
    threeScene.add(fenceGroup);

    // Load Blender Reconstructed Modular Fence Section
    if (window.THREE && typeof THREE.GLTFLoader === 'function') {
      const fenceLoader = new THREE.GLTFLoader();
      fenceLoader.load('assets/environment/boundary/boundary_fence_sensor.glb', (gltf) => {
        const fenceSec = gltf.scene;
        fenceSec.name = 'Blender_Boundary_Fence_Sensor';
        fenceSec.position.set(100, getTerrainElevation(100, 100), 100);
        fenceSec.traverse((c) => { if (c.isMesh) { c.castShadow = true; c.receiveShadow = true; } });
        threeScene.add(fenceSec);
        console.log('[PRW-Wild] Loaded Blender Reconstructed Boundary Fence Sensor Asset');
      }, undefined, (e) => { console.warn('[PRW-Wild] Fence sensor note:', e); });
    }"""

assert old_fence_posts in code, "old_fence_posts not found"
code = code.replace(old_fence_posts, new_fence_posts, 1)

with open("src/prw_wild/web/static/app.js", "w", encoding="utf-8") as f:
    f.write(code)

print("Successfully updated app.js with 12 animal variants, continuous twin horizontal rails, and fence sensor asset.")
