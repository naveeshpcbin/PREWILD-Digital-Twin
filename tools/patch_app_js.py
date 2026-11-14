"""Patch app.js to integrate 50+ Multi-Animal Ecosystem, 6 Species GLBs, and Live AI Vision Pipeline."""
import re
from pathlib import Path

app_path = Path("src/prw_wild/web/static/app.js")
code = app_path.read_text(encoding="utf-8")

# 1. Add multiAnimal fields to threeObjects definition
target_three_objs = "    cameraPovCamera: null,\n  };"
repl_three_objs = """    cameraPovCamera: null,
    multiAnimalPopulationGroup: null,
    multiAnimalMeshes: {},
    ecosystemPonds: [],
  };

  // Multi-Animal Ecosystem & Vision State
  let multiAnimalPopulation = [];
  let speciesGlbTemplates = {};
  let lastVisionInferenceTime = 0;
  let isVisionInferenceBusy = false;
  let ecosystemStepTimer = 0;"""

if "multiAnimalPopulationGroup: null" not in code:
    code = code.replace(target_three_objs, repl_three_objs)
    print("Added multiAnimal fields to threeObjects")

# 2. Add Multi-Animal Engine and Live Vision Functions before init()
target_init = "  // ==========================================================================\n  // Initialization\n  // =========================================================================="

ecosystem_code = """  // ==========================================================================
  // Multi-Animal Ecosystem 3D Population & Real AI Vision Engine
  // ==========================================================================

  const SPECIES_VISUAL_CONFIGS = {
    asian_elephant: { scale: 1.0, color: 0x8c8d8f, glb: 'assets/animals/asian_elephant_production.glb', yOffset: 0.0 },
    chital_deer: { scale: 1.1, color: 0xc88242, glb: 'assets/animals/chital_deer.glb', yOffset: 0.0 },
    sambar_deer: { scale: 1.25, color: 0x5a3e2b, glb: 'assets/animals/sambar_deer.glb', yOffset: 0.0 },
    wild_boar: { scale: 1.0, color: 0x383432, glb: 'assets/animals/wild_boar.glb', yOffset: 0.0 },
    gaur_bison: { scale: 1.2, color: 0x241d19, glb: 'assets/animals/gaur_bison.glb', yOffset: 0.0 },
    bonnet_macaque: { scale: 0.85, color: 0x8a7760, glb: 'assets/animals/bonnet_macaque.glb', yOffset: 0.0 },
  };

  function buildProceduralAnimalFallback(species) {
    const group = new THREE.Group();
    const cfg = SPECIES_VISUAL_CONFIGS[species] || SPECIES_VISUAL_CONFIGS.chital_deer;
    const mat = new THREE.MeshStandardMaterial({ color: cfg.color, roughness: 0.8 });

    // Body
    const bodyGeo = new THREE.BoxGeometry(0.8, 0.7, 1.4);
    const body = new THREE.Mesh(bodyGeo, mat);
    body.position.y = 0.8;
    body.castShadow = true;
    group.add(body);

    // Head
    const headGeo = new THREE.BoxGeometry(0.4, 0.45, 0.6);
    const head = new THREE.Mesh(headGeo, mat);
    head.position.set(0, 1.2, 0.8);
    head.castShadow = true;
    group.add(head);

    // 4 Legs
    const legGeo = new THREE.CylinderGeometry(0.08, 0.08, 0.7, 6);
    const legPositions = [
      [0.3, 0.35, 0.4], [-0.3, 0.35, 0.4],
      [0.3, 0.35, -0.4], [-0.3, 0.35, -0.4]
    ];
    legPositions.forEach(([lx, ly, lz]) => {
      const leg = new THREE.Mesh(legGeo, mat);
      leg.position.set(lx, ly, lz);
      leg.castShadow = true;
      group.add(leg);
    });

    group.scale.set(cfg.scale, cfg.scale, cfg.scale);
    return group;
  }

  function initMultiAnimalEcosystem() {
    if (!threeScene) return;

    const popGroup = new THREE.Group();
    popGroup.name = 'MultiAnimal_Population_Group';
    threeScene.add(popGroup);
    threeObjects.multiAnimalPopulationGroup = popGroup;

    // 1. Build 3D Ecological Water Ponds in Forest Zone
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

    threeObjects.ecosystemPonds.push(pondNorth, pondSouth);

    // 2. Preload Species 3D GLB Models
    if (window.THREE && typeof THREE.GLTFLoader === 'function') {
      const loader = new THREE.GLTFLoader();
      Object.entries(SPECIES_VISUAL_CONFIGS).forEach(([spKey, cfg]) => {
        loader.load(cfg.glb, (gltf) => {
          speciesGlbTemplates[spKey] = {
            scene: gltf.scene,
            animations: gltf.animations || []
          };
          console.log(`[PRW-Wild] Loaded GLB for ${spKey}`);
          // Refresh animal meshes with production GLB model
          refreshAnimalMeshesWithGlb(spKey);
        }, undefined, (err) => {
          console.warn(`[PRW-Wild] GLB fallback for ${spKey}:`, err);
        });
      });
    }

    // 3. Fetch Initial Multi-Animal Population from Backend
    fetchInitialEcosystemPopulation();

    // 4. Wire UI Event Listeners
    wireEcosystemUIEvents();
  }

  async function fetchInitialEcosystemPopulation() {
    try {
      const res = await fetch('/api/ecosystem/population');
      if (!res.ok) return;
      const data = await res.json();
      multiAnimalPopulation = data.population || [];

      // Update HUD count
      const badge = document.getElementById('hudPopCountBadge');
      if (badge) badge.textContent = `${multiAnimalPopulation.length} SIMULATED`;

      // Update Species Counts
      const counts = {};
      multiAnimalPopulation.forEach(a => counts[a.species] = (counts[a.species] || 0) + 1);
      document.getElementById('cnt_elephant') && (document.getElementById('cnt_elephant').textContent = counts.asian_elephant || 0);
      document.getElementById('cnt_chital') && (document.getElementById('cnt_chital').textContent = counts.chital_deer || 0);
      document.getElementById('cnt_sambar') && (document.getElementById('cnt_sambar').textContent = counts.sambar_deer || 0);
      document.getElementById('cnt_boar') && (document.getElementById('cnt_boar').textContent = counts.wild_boar || 0);
      document.getElementById('cnt_gaur') && (document.getElementById('cnt_gaur').textContent = counts.gaur_bison || 0);
      document.getElementById('cnt_macaque') && (document.getElementById('cnt_macaque').textContent = counts.bonnet_macaque || 0);

      // Spawn 3D Meshes for all agents
      spawnAnimalPopulationMeshes(multiAnimalPopulation);
    } catch (e) {
      console.warn('[PRW-Wild] Error fetching ecosystem population:', e);
    }
  }

  function spawnAnimalPopulationMeshes(agents) {
    if (!threeObjects.multiAnimalPopulationGroup) return;

    // Clear existing
    while (threeObjects.multiAnimalPopulationGroup.children.length > 0) {
      threeObjects.multiAnimalPopulationGroup.remove(threeObjects.multiAnimalPopulationGroup.children[0]);
    }
    threeObjects.multiAnimalMeshes = {};

    agents.forEach(agent => {
      const rootGroup = new THREE.Group();
      rootGroup.name = `Animal_${agent.animal_id}`;
      rootGroup.position.set(agent.position.x, 0, agent.position.y);
      rootGroup.rotation.y = -agent.heading_rad;

      let modelMesh = null;
      let mixer = null;
      let walkAction = null;

      if (speciesGlbTemplates[agent.species]) {
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
      }

      rootGroup.add(modelMesh);
      threeObjects.multiAnimalPopulationGroup.add(rootGroup);

      threeObjects.multiAnimalMeshes[agent.animal_id] = {
        group: rootGroup,
        modelMesh: modelMesh,
        mixer: mixer,
        walkAction: walkAction,
        species: agent.species,
        targetPos: new THREE.Vector3(agent.position.x, 0, agent.position.y),
        targetHeading: -agent.heading_rad,
        speed: agent.speed_m_s
      };
    });
  }

  function refreshAnimalMeshesWithGlb(speciesKey) {
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
  }

  function updateMultiAnimalLocomotion(delta) {
    // 1. Advance animations and smooth interpolation
    Object.values(threeObjects.multiAnimalMeshes).forEach(item => {
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
    });

    // 2. Periodic backend simulation step (every ~500ms)
    ecosystemStepTimer += delta;
    if (ecosystemStepTimer >= 0.5) {
      ecosystemStepTimer = 0;
      stepEcosystemBackend();
    }
  }

  async function stepEcosystemBackend() {
    try {
      const res = await fetch('/api/ecosystem/step', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ dt: 0.5 })
      });
      if (!res.ok) return;
      const data = await res.json();
      multiAnimalPopulation = data.agents || [];

      // Update positions
      multiAnimalPopulation.forEach(a => {
        const item = threeObjects.multiAnimalMeshes[a.animal_id];
        if (item) {
          item.targetPos.set(a.position.x, 0, a.position.y);
          item.targetHeading = -a.heading_rad;
          item.speed = a.speed_m_s;
        }
      });

      // Update resource bars
      if (data.resources) {
        data.resources.forEach(r => {
          const pct = Math.max(0, Math.min(100, (r.current_amount / r.max_capacity) * 100));
          if (r.patch_id === 'water_pond_north') {
            const bar = document.getElementById('res_water_north');
            if (bar) bar.style.width = `${pct}%`;
          } else if (r.patch_id === 'water_pond_south') {
            const bar = document.getElementById('res_water_south');
            if (bar) bar.style.width = `${pct}%`;
          } else if (r.patch_id === 'grass_glade_west' || r.patch_id === 'grass_corridor_approach') {
            const bar = document.getElementById('res_grass');
            if (bar) bar.style.width = `${pct}%`;
          } else if (r.patch_id.startsWith('farm_')) {
            const bar = document.getElementById('res_crops');
            if (bar) bar.style.width = `${pct}%`;
          }
        });
      }
    } catch (e) {
      // Backend stepping error handler
    }
  }

  async function runCameraAiInference() {
    if (isVisionInferenceBusy || !camPovRenderer) return;
    const povCanvas = document.getElementById('camPovCanvas');
    if (!povCanvas) return;

    isVisionInferenceBusy = true;
    try {
      const dataUrl = povCanvas.toDataURL('image/jpeg', 0.8);
      const res = await fetch('/api/vision/detect', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ image: dataUrl })
      });
      if (!res.ok) {
        isVisionInferenceBusy = false;
        return;
      }

      const visionData = await res.json();
      const dets = visionData.detections || [];
      const trks = visionData.tracks || [];
      const risks = visionData.risk_assessments || [];

      // Update Vision HUD
      const valDets = document.getElementById('valAiDetections');
      if (valDets) valDets.textContent = `${dets.length} DETECTED`;

      const valTrks = document.getElementById('valAiTracks');
      if (valTrks) valTrks.textContent = `${trks.length} TRACKED`;

      // Update Risk Assessment HUD
      if (risks.length > 0) {
        // Find highest risk track
        let maxRisk = risks[0];
        risks.forEach(r => {
          if (r.crossing_risk_score > maxRisk.crossing_risk_score) maxRisk = r;
        });

        const valRisk = document.getElementById('valAiRiskScore');
        if (valRisk) {
          valRisk.textContent = `${maxRisk.crossing_risk_score} (${maxRisk.risk_level})`;
          valRisk.className = maxRisk.risk_level === 'CRITICAL' ? 'text-rose' : (maxRisk.risk_level === 'HIGH' ? 'text-amber' : 'text-emerald');
        }

        const valEta = document.getElementById('valAiEta');
        if (valEta) {
          valEta.textContent = maxRisk.eta_seconds !== null ? `${maxRisk.eta_seconds} s` : '-- s';
        }

        // Overlay dynamic bounding box on POV camera feed
        const bboxEl = document.getElementById('povTargetBbox');
        const bboxLbl = document.getElementById('povBboxLabel');
        if (bboxEl && bboxLbl && maxRisk) {
          bboxEl.classList.remove('hidden');
          bboxLbl.textContent = `${maxRisk.class_name.toUpperCase()} [ID:${maxRisk.track_id}] ${maxRisk.detection_confidence} (RAW)`;
        }
      } else {
        const valRisk = document.getElementById('valAiRiskScore');
        if (valRisk) valRisk.textContent = '0.00 (LOW)';
        const valEta = document.getElementById('valAiEta');
        if (valEta) valEta.textContent = '-- s';
        const bboxEl = document.getElementById('povTargetBbox');
        if (bboxEl) bboxEl.classList.add('hidden');
      }
    } catch (e) {
      console.warn('[PRW-Wild] Live AI vision inference error:', e);
    } finally {
      isVisionInferenceBusy = false;
    }
  }

  function wireEcosystemUIEvents() {
    // 1. Manual Approach Button
    document.getElementById('btnInjectApproach')?.addEventListener('click', async () => {
      // Find animal closest to boundary in forest
      const candidate = multiAnimalPopulation.find(a => a.position.x < 170) || multiAnimalPopulation[0];
      if (candidate) {
        await fetch('/api/ecosystem/inject', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ animal_id: candidate.animal_id, intent: 'approach' })
        });
        console.log(`[PRW-Wild] Injected APPROACH intent on ${candidate.animal_id}`);
      }
    });

    // 2. Manual Turn Away Button
    document.getElementById('btnInjectTurnAway')?.addEventListener('click', async () => {
      const candidate = multiAnimalPopulation.find(a => a.position.x > 120 && a.position.x < 180) || multiAnimalPopulation[0];
      if (candidate) {
        await fetch('/api/ecosystem/inject', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ animal_id: candidate.animal_id, intent: 'turn_away' })
        });
        console.log(`[PRW-Wild] Injected TURN AWAY intent on ${candidate.animal_id}`);
      }
    });

    // 3. Manual Cross Breach Button
    document.getElementById('btnInjectCross')?.addEventListener('click', async () => {
      const candidate = multiAnimalPopulation.find(a => a.position.x > 100) || multiAnimalPopulation[0];
      if (candidate) {
        await fetch('/api/ecosystem/inject', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ animal_id: candidate.animal_id, intent: 'cross' })
        });
        console.log(`[PRW-Wild] Injected CROSS intent on ${candidate.animal_id}`);
      }
    });

    // 4. Population Size Slider
    const popSlider = document.getElementById('popSizeSlider');
    const popLabel = document.getElementById('lblPopSize');
    if (popSlider && popLabel) {
      popSlider.addEventListener('input', () => {
        popLabel.textContent = popSlider.value;
      });
    }

    // 5. Apply Reset Population
    document.getElementById('btnApplyPopSize')?.addEventListener('click', async () => {
      const val = parseInt(document.getElementById('popSizeSlider')?.value || 60);
      const res = await fetch('/api/ecosystem/reset', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ population_size: val, seed: Math.floor(Math.random() * 90000) })
      });
      if (res.ok) {
        await fetchInitialEcosystemPopulation();
      }
    });

    // 6. Mode F Tab Switcher
    document.getElementById('tabModeEcosystem')?.addEventListener('click', () => {
      setLabMode('ecosystem');
      // Position camera for glorious ecosystem overview
      if (threeControls && threeCamera) {
        threeCamera.position.set(130, 45, 110);
        threeControls.target.set(100, 2, 100);
        threeControls.update();
      }
      // Ensure Camera POV window is visible for live AI vision monitor
      const povWin = document.getElementById('camPovFloatingWindow');
      if (povWin) povWin.classList.remove('hidden');
    });
  }

"""

if "initMultiAnimalEcosystem" not in code:
    code = code.replace(target_init, ecosystem_code + "\n" + target_init)
    print("Added Multi-Animal Ecosystem and Vision engine functions")

# 3. Hook initMultiAnimalEcosystem() into init()
target_init_call = "    initHardwareLab();"
repl_init_call = """    initHardwareLab();
    initMultiAnimalEcosystem();"""

if "initMultiAnimalEcosystem();" not in code:
    code = code.replace(target_init_call, repl_init_call)
    print("Hooked initMultiAnimalEcosystem into init()")

# 4. Hook updateMultiAnimalLocomotion and runCameraAiInference into animateThree()
target_animate_three = "    // Render 3D Scene"
repl_animate_three = """    // Multi-Animal Population Locomotion & Gait Update
    if (threeObjects.multiAnimalPopulationGroup && threeClock) {
      const ecoDelta = Math.min(threeClock.getDelta(), 0.1);
      updateMultiAnimalLocomotion(ecoDelta);
    }

    // Live AI Vision Inference from Rendered Camera POV
    const nowMs = typeof performance !== 'undefined' ? performance.now() : Date.now();
    if (nowMs - lastVisionInferenceTime > 400) {
      lastVisionInferenceTime = nowMs;
      runCameraAiInference();
    }

    // Render 3D Scene"""

if "updateMultiAnimalLocomotion" not in code:
    code = code.replace(target_animate_three, repl_animate_three)
    print("Hooked updateMultiAnimalLocomotion and runCameraAiInference into animateThree()")

app_path.write_text(code, encoding="utf-8")
print("Done patching app.js")

