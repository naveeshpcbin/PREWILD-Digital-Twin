"""
Production Visual Overhaul Script
Applies:
1. Eradication of primitive cylinder/cone/sphere fallback trees
2. Forward heading calibration for elephant and all 16 species (Math.atan2(vx, vy))
3. Ground elevation contact (y = getTerrainElevation(x, z))
4. Dynamic walk animation timescale synchronized to speed
5. Fix transmission property warning on MeshStandardMaterial
"""
import re

app_js_path = r"D:\Simulation For DT\prw-wild-digital-twin\src\prw_wild\web\static\app.js"

with open(app_js_path, "r", encoding="utf-8") as f:
    content = f.read()

# 1. Eradicate organicTreeGroup in buildDiverseForest
old_tree_block = """    // 1. Organic 3D Tree Constructor (Natural Trunks & Volumetric Foliage Crowns)
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
    });"""

new_tree_block = """    // 1. Production High-Fidelity Forest (Zero Primitive Fallbacks)
    // Primitive cylinder/icosahedron lollipop trees eradicated.
    // 100% of forest instances are rendered from verified Blender GLB production assets."""

# Also remove old organicTreeGroup removal block
old_remove_organic = """            // Hide primitive placeholder trees once real GLB trees are attached
            if (organicTreeGroup && organicTreeGroup.parent) {
              forestContainer.remove(organicTreeGroup);
            }"""
new_remove_organic = """            // Real Blender GLB production tree placed at verified coordinate"""

# 2. Fix transmission warning on MeshStandardMaterial
old_pir1 = """    const pirDome = new THREE.Mesh(new THREE.SphereGeometry(1.05, 18, 14, 0, Math.PI * 2, 0, Math.PI / 2), new THREE.MeshStandardMaterial({ color: 0xf8fafc, roughness: 0.15, transmission: 0.3 }));"""
new_pir1 = """    const pirDome = new THREE.Mesh(new THREE.SphereGeometry(1.05, 18, 14, 0, Math.PI * 2, 0, Math.PI / 2), new THREE.MeshPhysicalMaterial({ color: 0xf8fafc, roughness: 0.15, transmission: 0.3, transparent: true }));"""

old_pir2 = """    const dome = new THREE.Mesh(new THREE.SphereGeometry(1.05, 18, 14, 0, Math.PI * 2, 0, Math.PI / 2), new THREE.MeshStandardMaterial({ color: 0xf8fafc, roughness: 0.15, transmission: 0.3 }));"""
new_pir2 = """    const dome = new THREE.Mesh(new THREE.SphereGeometry(1.05, 18, 14, 0, Math.PI * 2, 0, Math.PI / 2), new THREE.MeshPhysicalMaterial({ color: 0xf8fafc, roughness: 0.15, transmission: 0.3, transparent: true }));"""

# 3. Orient elephant in loadElephantModel
old_el_orient = """          // Create dedicated child visual-model group for fixed axis & orientation correction
          const visualGroup = new THREE.Group();
          visualGroup.name = 'Elephant_Visual_Child_Root';
          // Align model forward (+X trunk) with simulation heading, scaled to magnificent 1.25 life size
          visualGroup.rotation.y = 0;
          visualGroup.scale.set(1.25, 1.25, 1.25);
          visualGroup.add(prodModel);
          threeObjects.elephantVisualGroup = visualGroup;"""

new_el_orient = """          // Create dedicated child visual-model group for fixed axis & orientation correction
          const visualGroup = new THREE.Group();
          visualGroup.name = 'Elephant_Visual_Child_Root';
          // Align elephant trunk (+X in local GLB) to standard glTF forward (+Z)
          prodModel.rotation.y = -Math.PI / 2;
          visualGroup.rotation.y = 0;
          visualGroup.scale.set(1.25, 1.25, 1.25);
          visualGroup.add(prodModel);
          threeObjects.elephantVisualGroup = visualGroup;"""

# 4. Orient elephant and ground contact and mixer speed in syncThreeScene
old_el_sync = """    // 1. Elephant Position & Smooth Heading Direction (Shortest angular path)
    const animal = getGroundTruthAtTime(t);
    if (animal && threeObjects.elephantGroup) {
      threeObjects.elephantGroup.position.set(animal.x, threeObjects.elephantGroup.position.y, animal.y);

      const speed = Math.hypot(animal.vx, animal.vy);
      if (speed > 0.05) {
        const targetHeading = -Math.atan2(animal.vy, animal.vx);
        let diff = targetHeading - elephantLastValidHeading;
        while (diff < -Math.PI) diff += Math.PI * 2;
        while (diff > Math.PI) diff -= Math.PI * 2;
        const lerpFactor = isPlaying ? 0.35 : 1.0;
        elephantLastValidHeading += diff * lerpFactor;
        threeObjects.elephantGroup.rotation.y = elephantLastValidHeading;
      } else {
        threeObjects.elephantGroup.rotation.y = elephantLastValidHeading;
      }
    }"""

new_el_sync = """    // 1. Elephant Position, Ground Elevation & True Forward Heading
    const animal = getGroundTruthAtTime(t);
    if (animal && threeObjects.elephantGroup) {
      const terrY = getTerrainElevation(animal.x, animal.y);
      threeObjects.elephantGroup.position.set(animal.x, terrY, animal.y);

      const speed = Math.hypot(animal.vx, animal.vy);
      if (speed > 0.05) {
        // True forward heading: Math.atan2(vx, vz) where vz is animal.vy in 2D simulation
        const targetHeading = Math.atan2(animal.vx, animal.vy);
        let diff = targetHeading - elephantLastValidHeading;
        while (diff < -Math.PI) diff += Math.PI * 2;
        while (diff > Math.PI) diff -= Math.PI * 2;
        const lerpFactor = isPlaying ? 0.35 : 1.0;
        elephantLastValidHeading += diff * lerpFactor;
        threeObjects.elephantGroup.rotation.y = elephantLastValidHeading;
      } else {
        threeObjects.elephantGroup.rotation.y = elephantLastValidHeading;
      }

      // Synchronize walk animation mixer playback speed with ground speed
      if (threeObjects.elephantMixer && threeObjects.elephantWalkAction) {
        if (speed > 0.05) {
          threeObjects.elephantWalkAction.paused = false;
          threeObjects.elephantWalkAction.setEffectiveTimeScale(Math.min(2.5, Math.max(0.4, speed / 1.5)));
        } else {
          threeObjects.elephantWalkAction.paused = true;
        }
      }
    }"""

# 5. Orient multi-animal species templates
old_sp_load = """      Object.entries(SPECIES_VISUAL_CONFIGS).forEach(([spKey, cfg]) => {
        loader.load(cfg.glb, (gltf) => {
          speciesGlbTemplates[spKey] = {
            scene: gltf.scene,
            animations: gltf.animations || []
          };"""

new_sp_load = """      Object.entries(SPECIES_VISUAL_CONFIGS).forEach(([spKey, cfg]) => {
        loader.load(cfg.glb, (gltf) => {
          const modelScene = gltf.scene;
          if (spKey.includes('elephant')) {
            modelScene.rotation.y = -Math.PI / 2;
          }
          speciesGlbTemplates[spKey] = {
            scene: modelScene,
            animations: gltf.animations || []
          };"""

# 6. Multi-animal spawn heading
old_sp_spawn = """      const elevY = getTerrainElevation(agent.position.x, agent.position.y);
      rootGroup.position.set(agent.position.x, elevY, agent.position.y);
      rootGroup.rotation.y = -agent.heading_rad;"""

new_sp_spawn = """      const elevY = getTerrainElevation(agent.position.x, agent.position.y);
      rootGroup.position.set(agent.position.x, elevY, agent.position.y);
      rootGroup.rotation.y = Math.atan2(agent.velocity.x, agent.velocity.y);"""

# 7. Multi-animal step heading
old_sp_step = """          const elevY = getTerrainElevation(a.position.x, a.position.y);
          item.targetPos.set(a.position.x, elevY, a.position.y);
          item.targetHeading = -a.heading_rad;
          item.speed = a.speed_m_s;
          item.data = a;"""

new_sp_step = """          const elevY = getTerrainElevation(a.position.x, a.position.y);
          item.targetPos.set(a.position.x, elevY, a.position.y);
          item.targetHeading = Math.atan2(a.velocity.x, a.velocity.y);
          item.speed = a.speed_m_s;
          item.data = a;"""

# 8. Multi-animal locomotion update
old_sp_loco = """    Object.values(threeObjects.multiAnimalMeshes).forEach(item => {
      // Smooth position interpolation
      item.group.position.lerp(item.targetPos, 0.15);

      // Smooth heading rotation
      let diff = item.targetHeading - item.group.rotation.y;
      while (diff < -Math.PI) diff += Math.PI * 2;
      while (diff > Math.PI) diff -= Math.PI * 2;
      item.group.rotation.y += diff * 0.15;

      // Animation mixer update
      if (item.mixer) {
        if (item.speed > 0.1 && item.walkAction) {
          item.walkAction.paused = false;
          item.walkAction.setEffectiveTimeScale(Math.min(2.0, Math.max(0.6, item.speed * 0.8)));
        } else if (item.walkAction) {
          item.walkAction.paused = true;
        }
        item.mixer.update(delta);
      }
    });"""

new_sp_loco = """    Object.values(threeObjects.multiAnimalMeshes).forEach(item => {
      // Smooth position interpolation & terrain ground clamping
      item.group.position.lerp(item.targetPos, 0.15);
      item.group.position.y = getTerrainElevation(item.group.position.x, item.group.position.z);

      // Smooth heading rotation
      if (item.speed > 0.05) {
        let diff = item.targetHeading - item.group.rotation.y;
        while (diff < -Math.PI) diff += Math.PI * 2;
        while (diff > Math.PI) diff -= Math.PI * 2;
        item.group.rotation.y += diff * 0.15;
      }

      // Animation mixer update synchronized to velocity
      if (item.mixer) {
        if (item.speed > 0.1 && item.walkAction) {
          item.walkAction.paused = false;
          item.walkAction.setEffectiveTimeScale(Math.min(2.2, Math.max(0.4, item.speed / 1.2)));
        } else if (item.walkAction) {
          item.walkAction.paused = true;
        }
        item.mixer.update(delta);
      }
    });"""

# Helper to replace normalized newlines
def do_replace(txt, old, new, desc):
    # try direct
    if old in txt:
        print(f"[OK] Found and replaced: {desc}")
        return txt.replace(old, new)
    # try crlf
    old_crlf = old.replace('\n', '\r\n')
    new_crlf = new.replace('\n', '\r\n')
    if old_crlf in txt:
        print(f"[OK] Found and replaced (CRLF): {desc}")
        return txt.replace(old_crlf, new_crlf)
    print(f"[FAIL] Could NOT find: {desc}")
    return txt

content = do_replace(content, old_tree_block, new_tree_block, "1. Eradicate organicTreeGroup")
content = do_replace(content, old_remove_organic, new_remove_organic, "1b. Remove old organicTreeGroup removal")
content = do_replace(content, old_pir1, new_pir1, "2a. Fix pirDome transmission")
content = do_replace(content, old_pir2, new_pir2, "2b. Fix dome transmission")
content = do_replace(content, old_el_orient, new_el_orient, "3. Orient elephant in loadElephantModel")
content = do_replace(content, old_el_sync, new_el_sync, "4. Orient elephant & ground contact in syncThreeScene")
content = do_replace(content, old_sp_load, new_sp_load, "5. Orient elephant species templates")
content = do_replace(content, old_sp_spawn, new_sp_spawn, "6. Multi-animal spawn heading")
content = do_replace(content, old_sp_step, new_sp_step, "7. Multi-animal step heading")
content = do_replace(content, old_sp_loco, new_sp_loco, "8. Multi-animal locomotion update")

with open(app_js_path, "w", encoding="utf-8") as f:
    f.write(content)

print("Update complete!")

