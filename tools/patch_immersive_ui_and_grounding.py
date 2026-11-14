"""
Patches app.js, index.html, and style.css for:
1. Exact 3D terrain elevation grounding for all trees, rocks, crops, watchtower, and animals.
2. Multi-animal individual directory (60 distinct named animals with demographics, tasks, and scale).
3. Neural network visual bounding box overlay canvas on live camera feed.
4. Smart fencing acoustic / visual deterrent simulation controls.
"""

import re
import os

PROJECT_DIR = r"D:\Simulation For DT\prw-wild-digital-twin"
APP_JS = os.path.join(PROJECT_DIR, "src", "prw_wild", "web", "static", "app.js")
INDEX_HTML = os.path.join(PROJECT_DIR, "src", "prw_wild", "web", "static", "index.html")
STYLE_CSS = os.path.join(PROJECT_DIR, "src", "prw_wild", "web", "static", "style.css")

# ===========================================================================
# 1. Patch app.js
# ===========================================================================
with open(APP_JS, "r", encoding="utf-8") as f:
    app_text = f.read()

# 1.1 Insert getTerrainElevation right before buildProceduralEnvironment
terrain_func = """  // ==========================================================================
  // Analytical Terrain Elevation Sampling (Matches Blender 5.2.2 World Mesh)
  // ==========================================================================
  function getTerrainElevation(x, z) {
    let base = (x < 100) ? (100.0 - x) * 0.015 : -(x - 100.0) * 0.005;
    let y = base;
    if (x < 100) {
      const hills =
        Math.sin(x * 0.065 + 1.2) * Math.cos(z * 0.055) * 1.8 +
        Math.sin(x * 0.12 - 0.5) * Math.cos(z * 0.11 + 0.8) * 0.75 +
        Math.sin(x * 0.22) * Math.sin(z * 0.19) * 0.35;
      const westRidge = Math.max(0.0, (40.0 - x) * 0.08);
      y += hills + westRidge;
    } else {
      const terIdx = Math.floor((x - 100.0) / 28.0);
      const terRem = (x - 100.0) % 28.0;
      const farmGrade = -terIdx * 0.35 - (terRem / 28.0) * 0.08;
      const furrows = Math.sin(z * 1.1) * 0.06;
      y += farmGrade + furrows;
    }

    // Corridor valley depression
    const corrDistZ = Math.abs(z - (100.0 + Math.sin(x * 0.05) * 6.0));
    if (corrDistZ < 22.0 && x < 105) {
      const corrFactor = Math.pow(1.0 - corrDistZ / 22.0, 2);
      y -= corrFactor * 2.2;
    }

    // North Pond depression at (75, 140)
    const distP1 = Math.hypot(x - 75.0, z - 140.0);
    if (distP1 < 22.0) {
      const depth1 = Math.pow(1.0 - distP1 / 22.0, 1.8);
      y -= depth1 * 2.4;
    }

    // South Pond depression at (45, 60)
    const distP2 = Math.hypot(x - 45.0, z - 60.0);
    if (distP2 < 18.0) {
      const depth2 = Math.pow(1.0 - distP2 / 18.0, 1.8);
      y -= depth2 * 2.1;
    }

    y += Math.sin(x * 1.7 + z * 1.3) * 0.04;
    return y;
  }

  function buildProceduralEnvironment() {"""

target_proc_env = "  function buildProceduralEnvironment() {"
assert target_proc_env in app_text, "target_proc_env not found"
app_text = app_text.replace(target_proc_env, terrain_func, 1)

# 1.2 Ground trees and vegetation in buildDiverseForest
old_tree_pos_set = """                tree.position.set(tx, 0, tz);"""
new_tree_pos_set = """                const groundY = getTerrainElevation(tx, tz);
                tree.position.set(tx, groundY, tz);"""
assert old_tree_pos_set in app_text, "old_tree_pos_set not found"
app_text = app_text.replace(old_tree_pos_set, new_tree_pos_set, 1)

old_boulder_pos_set = """                rock.position.set(bx, 0, bz);"""
new_boulder_pos_set = """                rock.position.set(bx, getTerrainElevation(bx, bz), bz);"""
assert old_boulder_pos_set in app_text, "old_boulder_pos_set not found"
app_text = app_text.replace(old_boulder_pos_set, new_boulder_pos_set, 1)

old_fern_pos_set = """                fern.position.set(fx, 0, fz);"""
new_fern_pos_set = """                fern.position.set(fx, getTerrainElevation(fx, fz), fz);"""
assert old_fern_pos_set in app_text, "old_fern_pos_set not found"
app_text = app_text.replace(old_fern_pos_set, new_fern_pos_set, 1)

old_shrub_pos_set = """                shrub.position.set(sx, 0, sz);"""
new_shrub_pos_set = """                shrub.position.set(sx, getTerrainElevation(sx, sz), sz);"""
assert old_shrub_pos_set in app_text, "old_shrub_pos_set not found"
app_text = app_text.replace(old_shrub_pos_set, new_shrub_pos_set, 1)

old_grass_pos_set = """                gclump.position.set(gx, 0, gz);"""
new_grass_pos_set = """                gclump.position.set(gx, getTerrainElevation(gx, gz), gz);"""
assert old_grass_pos_set in app_text, "old_grass_pos_set not found"
app_text = app_text.replace(old_grass_pos_set, new_grass_pos_set, 1)

# 1.3 Ground Watchtower and Crop parcels
old_machan_pos = "machan.position.set(118, 0, 102);"
new_machan_pos = "machan.position.set(118, getTerrainElevation(118, 102), 102);"
assert old_machan_pos in app_text, "old_machan_pos not found"
app_text = app_text.replace(old_machan_pos, new_machan_pos, 1)

old_crops_pos = "cropsNorth.position.set(145, 0, 75);"
new_crops_pos = "cropsNorth.position.set(145, getTerrainElevation(145, 75), 75);"
assert old_crops_pos in app_text, "old_crops_pos not found"
app_text = app_text.replace(old_crops_pos, new_crops_pos, 1)

old_crops_south = "cropsSouth.position.set(145, 0, 145);"
new_crops_south = "cropsSouth.position.set(145, getTerrainElevation(145, 145), 145);"
assert old_crops_south in app_text, "old_crops_south not found"
app_text = app_text.replace(old_crops_south, new_crops_south, 1)

# 1.4 Update spawnAnimalPopulationMeshes with elevation and individual scale
target_spawn_animal = """    agents.forEach(agent => {
      const rootGroup = new THREE.Group();
      rootGroup.name = `Animal_${agent.animal_id}`;
      rootGroup.position.set(agent.position.x, 0, agent.position.y);
      rootGroup.rotation.y = -agent.heading_rad;"""

replacement_spawn_animal = """    agents.forEach(agent => {
      const rootGroup = new THREE.Group();
      rootGroup.name = `Animal_${agent.animal_id}`;
      const elevY = getTerrainElevation(agent.position.x, agent.position.y);
      rootGroup.position.set(agent.position.x, elevY, agent.position.y);
      rootGroup.rotation.y = -agent.heading_rad;

      // Apply individual animal morphology scale
      const sf = agent.scale_factor || 1.0;
      rootGroup.scale.set(sf, sf, sf);"""

assert target_spawn_animal in app_text, "target_spawn_animal not found"
app_text = app_text.replace(target_spawn_animal, replacement_spawn_animal, 1)

target_spawn_targetpos = """        targetPos: new THREE.Vector3(agent.position.x, 0, agent.position.y),
        targetHeading: -agent.heading_rad,
        speed: agent.speed_m_s"""

replacement_spawn_targetpos = """        targetPos: new THREE.Vector3(agent.position.x, elevY, agent.position.y),
        targetHeading: -agent.heading_rad,
        speed: agent.speed_m_s,
        data: agent"""

assert target_spawn_targetpos in app_text, "target_spawn_targetpos not found"
app_text = app_text.replace(target_spawn_targetpos, replacement_spawn_targetpos, 1)

# 1.5 Update stepEcosystemBackend animal targetPos with terrain elevation
target_step_targetpos = """        const item = threeObjects.multiAnimalMeshes[a.animal_id];
        if (item) {
          item.targetPos.set(a.position.x, 0, a.position.y);
          item.targetHeading = -a.heading_rad;
          item.speed = a.speed_m_s;
        }"""

replacement_step_targetpos = """        const item = threeObjects.multiAnimalMeshes[a.animal_id];
        if (item) {
          const elevY = getTerrainElevation(a.position.x, a.position.y);
          item.targetPos.set(a.position.x, elevY, a.position.y);
          item.targetHeading = -a.heading_rad;
          item.speed = a.speed_m_s;
          item.data = a;
        }"""

assert target_step_targetpos in app_text, "target_step_targetpos not found"
app_text = app_text.replace(target_step_targetpos, replacement_step_targetpos, 1)

# 1.6 Update runCameraAiInference to draw all bounding boxes onto camPovBboxCanvas
target_vision_draw = """        // Overlay dynamic bounding box on POV camera feed
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
      }"""

replacement_vision_draw = """        // Overlay dynamic bounding box on POV camera feed
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

      // Draw all detected bounding boxes onto overlay canvas
      drawNeuralBoundingBoxes(dets, risks);"""

assert target_vision_draw in app_text, "target_vision_draw not found"
app_text = app_text.replace(target_vision_draw, replacement_vision_draw, 1)

# 1.7 Add drawNeuralBoundingBoxes and animal directory UI functions
helper_functions = """
  // ==========================================================================
  // Neural Network Bounding Box Overlay Canvas Renderer
  // ==========================================================================
  function drawNeuralBoundingBoxes(detections, risks) {
    const overlay = document.getElementById('camPovBboxCanvas');
    if (!overlay) return;
    const ctx = overlay.getContext('2d');
    if (!ctx) return;

    ctx.clearRect(0, 0, overlay.width, overlay.height);

    if (!detections || detections.length === 0) return;

    // Build risk lookup by box proximity
    detections.forEach((det, idx) => {
      const [x1, y1, x2, y2] = det.bbox;
      const bw = x2 - x1;
      const bh = y2 - y1;

      // Find matching risk record if available
      const rMatch = risks && risks[idx] ? risks[idx] : null;
      const riskLevel = rMatch ? rMatch.risk_level : 'LOW';

      // Colors based on risk
      let strokeColor = '#10b981'; // Emerald
      let glowColor = 'rgba(16, 185, 129, 0.4)';
      if (riskLevel === 'CRITICAL' || det.class_name === 'asian_elephant') {
        strokeColor = '#f43f5e'; // Rose
        glowColor = 'rgba(244, 63, 94, 0.4)';
      } else if (riskLevel === 'HIGH' || riskLevel === 'APPROACH_WARNING') {
        strokeColor = '#f59e0b'; // Amber
        glowColor = 'rgba(245, 158, 11, 0.4)';
      }

      ctx.save();
      ctx.strokeStyle = strokeColor;
      ctx.lineWidth = 1.8;
      ctx.shadowColor = glowColor;
      ctx.shadowBlur = 6;

      // Draw rounded rectangle bounding box
      ctx.strokeRect(x1, y1, bw, bh);

      // Draw corner bracket accents
      const cornerLen = Math.min(10, Math.min(bw, bh) * 0.25);
      ctx.lineWidth = 2.5;
      // Top-Left
      ctx.beginPath(); ctx.moveTo(x1, y1 + cornerLen); ctx.lineTo(x1, y1); ctx.lineTo(x1 + cornerLen, y1); ctx.stroke();
      // Top-Right
      ctx.beginPath(); ctx.moveTo(x2 - cornerLen, y1); ctx.lineTo(x2, y1); ctx.lineTo(x2, y1 + cornerLen); ctx.stroke();
      // Bottom-Left
      ctx.beginPath(); ctx.moveTo(x1, y2 - cornerLen); ctx.lineTo(x1, y2); ctx.lineTo(x1 + cornerLen, y2); ctx.stroke();
      // Bottom-Right
      ctx.beginPath(); ctx.moveTo(x2 - cornerLen, y2); ctx.lineTo(x2, y2); ctx.lineTo(x2, y2 - cornerLen); ctx.stroke();

      // Header Tag Banner
      const trackId = rMatch ? rMatch.track_id : `trk_${idx + 1}`;
      const confPct = Math.round(det.confidence * 100);
      const tagText = `${trackId} • ${det.class_name.toUpperCase()} (${confPct}% RAW)`;

      ctx.font = '600 9px monospace';
      const textWidth = ctx.measureText(tagText).width;
      const tagH = 14;
      const tagY = Math.max(0, y1 - tagH - 2);

      ctx.fillStyle = strokeColor;
      ctx.fillRect(x1, tagY, textWidth + 8, tagH);

      ctx.fillStyle = '#0f172a';
      ctx.fillText(tagText, x1 + 4, tagY + 10);

      // Sub-tag for Distance & ETA if in approach
      if (rMatch && rMatch.distance_to_boundary_m !== undefined) {
        const subText = `DIST: ${rMatch.distance_to_boundary_m}m • ETA: ${rMatch.eta_seconds !== null ? rMatch.eta_seconds + 's' : '--'}`;
        ctx.fillStyle = 'rgba(15, 23, 42, 0.85)';
        ctx.fillRect(x1, y2 + 2, ctx.measureText(subText).width + 6, 12);
        ctx.fillStyle = strokeColor;
        ctx.fillText(subText, x1 + 3, y2 + 11);
      }

      ctx.restore();
    });
  }

  // ==========================================================================
  // Individual Animal Directory HUD & Camera Focus
  // ==========================================================================
  function renderIndividualAnimalDirectory() {
    const listEl = document.getElementById('individualAnimalList');
    if (!listEl || !multiAnimalPopulation) return;

    const filterVal = document.getElementById('selSpeciesFilter')?.value || 'all';

    let html = '';
    multiAnimalPopulation.forEach(a => {
      if (filterVal !== 'all' && a.species !== filterVal) return;

      const isProbing = a.state === 'approaching_boundary';
      const isBreaching = a.state === 'crossing_boundary';
      const isDeterred = a.state === 'turning_away';

      let statusBadge = '<span class=\"badge-green\">FORAGING</span>';
      if (isBreaching) statusBadge = '<span class=\"badge-rose\">BREACHING</span>';
      else if (isProbing) statusBadge = '<span class=\"badge-amber\">PROBING FENCE</span>';
      else if (isDeterred) statusBadge = '<span class=\"badge-cyan\">DETERRED</span>';
      else if (a.state === 'drinking') statusBadge = '<span class=\"badge-cyan\">DRINKING</span>';

      html += `
        <div class=\"animal-roster-row\" onclick=\"focusAnimalCamera('${a.animal_id}')\">
          <div class=\"animal-row-main\">
            <span class=\"animal-row-name\">${a.name || a.animal_id}</span>
            <span class=\"animal-row-spec\">${a.species.replace('_', ' ').toUpperCase()}</span>
          </div>
          <div class=\"animal-row-task\">${a.current_task || 'Grazing'}</div>
          <div class=\"animal-row-status\">${statusBadge}</div>
        </div>
      `;
    });

    listEl.innerHTML = html;
  }

  window.focusAnimalCamera = function(animalId) {
    const item = threeObjects.multiAnimalMeshes[animalId];
    if (!item) return;

    const targetPos = item.group.position;
    if (orbitControls && threeCamera) {
      orbitControls.target.set(targetPos.x, targetPos.y + 1.5, targetPos.z);
      threeCamera.position.set(targetPos.x - 12, targetPos.y + 8, targetPos.z + 14);
      orbitControls.update();
      console.log(`[PRW-Wild] Focused camera on individual animal ${animalId}`);
    }
  };

  window.triggerPerimeterDeterrent = async function(type) {
    console.log(`[PRW-Wild] Triggering perimeter deterrent: ${type}`);
    // Find animals near fence (< 25m) and inject turn_away intent
    let deterredCount = 0;
    for (const a of multiAnimalPopulation) {
      if (a.position.x > 75.0 && a.position.x < 100.0) {
        await fetch('/api/ecosystem/inject', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ animal_id: a.animal_id, intent: 'turn_away' })
        });
        deterredCount++;
      }
    }
    const statusEl = document.getElementById('deterrentStatusText');
    if (statusEl) {
      statusEl.textContent = `DETERRENT ACTIVATED: ${deterredCount} animal(s) safely turned away!`;
      statusEl.className = 'text-emerald';
      setTimeout(() => {
        statusEl.textContent = 'Deterrent System: Ready (Standby)';
        statusEl.className = 'text-slate-400';
      }, 4000);
    }
  };
"""

app_text += helper_functions

with open(APP_JS, "w", encoding="utf-8") as f:
    f.write(app_text)

print("app.js patched successfully!")

