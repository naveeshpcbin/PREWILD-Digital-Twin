import os

# 1. Patch app.js with 3D ground envelopes and occupancy logic
app_js_path = r"D:\Simulation For DT\prw-wild-digital-twin\src\prw_wild\web\static\app.js"
with open(app_js_path, "r", encoding="utf-8") as f:
    app_text = f.read()

# Add ground envelope creation inside buildProceduralEnvironment right after fenceGroup
old_fence_add = """    threeScene.add(fenceGroup);

    // ========================================================================="""

new_fence_add = """    threeScene.add(fenceGroup);

    // =========================================================================
    // 3B. THREE FIXED DETECTION LAYERS (GROUND VISUALIZATION ENVELOPES)
    // Fixed Ordering: Outer = Layer 1 (CSI), Middle = Layer 2 (Sensors), Inner = Layer 3 (Camera)
    // =========================================================================
    const layer1Geo = new THREE.PlaneGeometry(25, 196, 12, 32);
    layer1Geo.rotateX(-Math.PI / 2);
    const l1Pos = layer1Geo.attributes.position;
    for (let i = 0; i < l1Pos.count; i++) {
      const vx = l1Pos.getX(i) + 57.5;
      const vz = l1Pos.getZ(i) + 100.0;
      l1Pos.setX(i, vx);
      l1Pos.setY(i, getTerrainElevation(vx, vz) + 0.05);
      l1Pos.setZ(i, vz);
    }
    layer1Geo.computeVertexNormals();
    const layer1Mat = new THREE.MeshBasicMaterial({
      color: 0x00f0ff,
      transparent: true,
      opacity: 0.08,
      side: THREE.DoubleSide
    });
    const layer1Mesh = new THREE.Mesh(layer1Geo, layer1Mat);
    layer1Mesh.name = 'Layer1_CSI_Ground_Envelope';
    threeScene.add(layer1Mesh);
    threeObjects.layer1Mesh = layer1Mesh;

    const layer2Geo = new THREE.PlaneGeometry(15, 196, 8, 32);
    layer2Geo.rotateX(-Math.PI / 2);
    const l2Pos = layer2Geo.attributes.position;
    for (let i = 0; i < l2Pos.count; i++) {
      const vx = l2Pos.getX(i) + 77.5;
      const vz = l2Pos.getZ(i) + 100.0;
      l2Pos.setX(i, vx);
      l2Pos.setY(i, getTerrainElevation(vx, vz) + 0.06);
      l2Pos.setZ(i, vz);
    }
    layer2Geo.computeVertexNormals();
    const layer2Mat = new THREE.MeshBasicMaterial({
      color: 0xf59e0b,
      transparent: true,
      opacity: 0.09,
      side: THREE.DoubleSide
    });
    const layer2Mesh = new THREE.Mesh(layer2Geo, layer2Mat);
    layer2Mesh.name = 'Layer2_Sensors_Ground_Envelope';
    threeScene.add(layer2Mesh);
    threeObjects.layer2Mesh = layer2Mesh;

    const layer3Geo = new THREE.PlaneGeometry(15, 196, 8, 32);
    layer3Geo.rotateX(-Math.PI / 2);
    const l3Pos = layer3Geo.attributes.position;
    for (let i = 0; i < l3Pos.count; i++) {
      const vx = l3Pos.getX(i) + 92.5;
      const vz = l3Pos.getZ(i) + 100.0;
      l3Pos.setX(i, vx);
      l3Pos.setY(i, getTerrainElevation(vx, vz) + 0.07);
      l3Pos.setZ(i, vz);
    }
    layer3Geo.computeVertexNormals();
    const layer3Mat = new THREE.MeshBasicMaterial({
      color: 0xa855f7,
      transparent: true,
      opacity: 0.12,
      side: THREE.DoubleSide
    });
    const layer3Mesh = new THREE.Mesh(layer3Geo, layer3Mat);
    layer3Mesh.name = 'Layer3_Camera_Ground_Envelope';
    threeScene.add(layer3Mesh);
    threeObjects.layer3Mesh = layer3Mesh;

    // ========================================================================="""

assert old_fence_add in app_text, "old_fence_add not found"
app_text = app_text.replace(old_fence_add, new_fence_add, 1)

# Add layer occupancy computation to stepEcosystemBackend
old_render_dir = """      renderIndividualAnimalDirectory();"""

new_render_dir = """      renderIndividualAnimalDirectory();

      // Update Three-Layer Detection Occupancy (Fixed Order: L1 CSI -> L2 Sensors -> L3 Camera)
      let countL1 = 0;
      let countL2 = 0;
      let countL3 = 0;

      multiAnimalPopulation.forEach(a => {
        const x = a.position.x;
        if (x >= 45.0 && x < 70.0) countL1++;
        else if (x >= 70.0 && x < 85.0) countL2++;
        else if (x >= 85.0 && x < 100.0) countL3++;
      });

      // Update 3D Ground Envelopes & Shaders
      if (threeObjects.layer1Mesh) {
        threeObjects.layer1Mesh.material.opacity = countL1 > 0 ? 0.22 : 0.06;
      }
      if (threeObjects.layer2Mesh) {
        threeObjects.layer2Mesh.material.opacity = countL2 > 0 ? 0.26 : 0.08;
      }
      if (threeObjects.layer3Mesh) {
        threeObjects.layer3Mesh.material.opacity = countL3 > 0 ? 0.32 : 0.10;
      }

      // Update HUD Status Badges
      const b1 = document.getElementById('hudLayer1Badge');
      const s1 = document.getElementById('hudLayer1Status');
      if (b1 && s1) {
        if (countL1 > 0) {
          b1.classList.add('active');
          s1.textContent = `ACTIVE (${countL1})`;
        } else {
          b1.classList.remove('active');
          s1.textContent = 'IDLE (0)';
        }
      }

      const b2 = document.getElementById('hudLayer2Badge');
      const s2 = document.getElementById('hudLayer2Status');
      if (b2 && s2) {
        if (countL2 > 0) {
          b2.classList.add('active');
          s2.textContent = `ACTIVE (${countL2})`;
        } else {
          b2.classList.remove('active');
          s2.textContent = 'IDLE (0)';
        }
      }

      const b3 = document.getElementById('hudLayer3Badge');
      const s3 = document.getElementById('hudLayer3Status');
      if (b3 && s3) {
        if (countL3 > 0) {
          b3.classList.add('active');
          s3.textContent = `TARGET LOCKED (${countL3})`;
        } else {
          b3.classList.remove('active');
          s3.textContent = 'STANDBY (0)';
        }
      }"""

assert old_render_dir in app_text, "old_render_dir not found"
app_text = app_text.replace(old_render_dir, new_render_dir, 1)

with open(app_js_path, "w", encoding="utf-8") as f:
    f.write(app_text)
print("SUCCESS: Patched app.js with Three-Layer detection envelopes and occupancy logic")

# 2. Patch index.html with HUD overlay
html_path = r"D:\Simulation For DT\prw-wild-digital-twin\src\prw_wild\web\static\index.html"
with open(html_path, "r", encoding="utf-8") as f:
    html_text = f.read()

target_overlay = """            <!-- Floating HUD Overlays -->"""
replacement_overlay = """            <!-- Floating Three-Layer Detection HUD Overlay -->
            <div class="detection-layers-overlay" id="detectionLayersOverlay">
              <div class="detection-layer-badge l1" id="hudLayer1Badge">
                <span class="dl-num">L1</span>
                <span class="dl-name">Wi-Fi CSI / ESP32 (Outer)</span>
                <span class="dl-status" id="hudLayer1Status">IDLE (0)</span>
              </div>
              <div class="detection-layer-badge l2" id="hudLayer2Badge">
                <span class="dl-num">L2</span>
                <span class="dl-name">Sensor Network (Middle)</span>
                <span class="dl-status" id="hudLayer2Status">IDLE (0)</span>
              </div>
              <div class="detection-layer-badge l3" id="hudLayer3Badge">
                <span class="dl-num">L3</span>
                <span class="dl-name">Camera Surveillance (Inner)</span>
                <span class="dl-status" id="hudLayer3Status">STANDBY (0)</span>
              </div>
            </div>

            <!-- Floating HUD Overlays -->"""

assert target_overlay in html_text, "target_overlay not found in index.html"
html_text = html_text.replace(target_overlay, replacement_overlay, 1)

with open(html_path, "w", encoding="utf-8") as f:
    f.write(html_text)
print("SUCCESS: Patched index.html with Detection Layers HUD")

# 3. Patch style.css
css_path = r"D:\Simulation For DT\prw-wild-digital-twin\src\prw_wild\web\static\style.css"
with open(css_path, "r", encoding="utf-8") as f:
    css_text = f.read()

css_addition = """
/* Detection Layers HUD Overlay (Fixed Three-Layer Architecture) */
.detection-layers-overlay {
  position: absolute;
  top: 18px;
  right: 18px;
  display: flex;
  flex-direction: column;
  gap: 8px;
  z-index: 25;
  pointer-events: none;
}
.detection-layer-badge {
  display: flex;
  align-items: center;
  gap: 10px;
  background: rgba(15, 23, 42, 0.88);
  backdrop-filter: blur(8px);
  border: 1px solid var(--border-subtle);
  border-radius: var(--radius-sm);
  padding: 6px 12px;
  font-family: var(--font-mono);
  font-size: 11px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.4);
  transition: all 0.3s ease;
}
.detection-layer-badge .dl-num {
  font-weight: 700;
  padding: 2px 6px;
  border-radius: 4px;
}
.detection-layer-badge.l1 .dl-num { background: rgba(0, 240, 255, 0.18); color: var(--cyan-radar); }
.detection-layer-badge.l2 .dl-num { background: rgba(245, 158, 11, 0.18); color: var(--amber-rf); }
.detection-layer-badge.l3 .dl-num { background: rgba(168, 85, 247, 0.18); color: var(--violet-camera); }
.detection-layer-badge .dl-name { color: var(--text-muted); font-size: 10.5px; }
.detection-layer-badge .dl-status { margin-left: auto; font-weight: 600; color: var(--text-dim); }
.detection-layer-badge.active.l1 { border-color: var(--cyan-radar); box-shadow: 0 0 14px var(--cyan-glow); }
.detection-layer-badge.active.l1 .dl-status { color: var(--cyan-radar); }
.detection-layer-badge.active.l2 { border-color: var(--amber-rf); box-shadow: 0 0 14px var(--amber-glow); }
.detection-layer-badge.active.l2 .dl-status { color: var(--amber-rf); }
.detection-layer-badge.active.l3 { border-color: var(--violet-camera); box-shadow: 0 0 14px var(--violet-glow); }
.detection-layer-badge.active.l3 .dl-status { color: var(--violet-camera); }
"""

css_text += css_addition

with open(css_path, "w", encoding="utf-8") as f:
    f.write(css_text)
print("SUCCESS: Patched style.css with Detection Layers styling")

