"""
Patches index.html and style.css for:
- Neural bounding box overlay canvas over camera feed
- Smart Fencing Deterrent System controls
- Individual Animal Directory with species filters and interactive roster
"""

import os

INDEX_HTML = r"D:\Simulation For DT\prw-wild-digital-twin\src\prw_wild\web\static\index.html"
STYLE_CSS = r"D:\Simulation For DT\prw-wild-digital-twin\src\prw_wild\web\static\style.css"

# 1. Patch index.html
with open(INDEX_HTML, "r", encoding="utf-8") as f:
    html = f.read()

# 1.1 Add camPovBboxCanvas overlay right after camPovCanvas
target_canvas = '<canvas id="camPovCanvas" width="280" height="158" class="pov-render-canvas"></canvas>'
replacement_canvas = '<canvas id="camPovCanvas" width="280" height="158" class="pov-render-canvas"></canvas>\n                <canvas id="camPovBboxCanvas" width="280" height="158" class="pov-bbox-overlay-canvas"></canvas>'

assert target_canvas in html, "target_canvas not found in index.html"
html = html.replace(target_canvas, replacement_canvas, 1)

# 1.2 Add Smart Fence Deterrents and Animal Directory into ecosystemPanel
target_panel_end = """              <div class="res-card">
                <span class="res-label">🌾 Farm Crops</span>
                <div class="res-bar"><div class="res-fill crops" id="res_crops" style="width: 100%;"></div></div>
              </div>
            </div>
          </div>
        </div>"""

replacement_panel_end = """              <div class="res-card">
                <span class="res-label">🌾 Farm Crops</span>
                <div class="res-bar"><div class="res-fill crops" id="res_crops" style="width: 100%;"></div></div>
              </div>
            </div>
          </div>

          <!-- Smart Virtual Fencing Deterrent System -->
          <div class="deterrent-controls-section">
            <div class="ec-section-title">SMART FENCE DETERRENT SYSTEM</div>
            <div class="deterrent-btn-grid">
              <button class="det-btn beehive" onclick="triggerPerimeterDeterrent('beehive')" title="Simulate Acoustic Bee-Hive Sound (Proven Indian Elephant Deterrent)">
                🐝 BEE-HIVE SOUND
              </button>
              <button class="det-btn ultrasonic" onclick="triggerPerimeterDeterrent('ultrasonic')" title="Simulate High-Frequency Directional Ultrasonic Pulse">
                📡 ULTRASONIC
              </button>
              <button class="det-btn strobe" onclick="triggerPerimeterDeterrent('strobe')" title="Trigger Perimeter Strobe Warning Flasher">
                ⚡ STROBE PULSE
              </button>
            </div>
            <div class="deterrent-status-box" id="deterrentStatusText">Deterrent System: Ready (Autonomous Standby)</div>
          </div>

          <!-- Individual Animal Directory (60 Distinct Agents) -->
          <div class="animal-directory-section">
            <div class="ec-section-title">INDIVIDUAL ANIMAL DIRECTORY (60 AGENTS)</div>
            <div class="animal-filter-bar">
              <select id="selSpeciesFilter" class="animal-filter-select" onchange="renderIndividualAnimalDirectory()">
                <option value="all">ALL SPECIES (60 AGENTS)</option>
                <option value="asian_elephant">ASIAN ELEPHANTS (8)</option>
                <option value="chital_deer">CHITAL DEER (18)</option>
                <option value="sambar_deer">SAMBAR DEER (8)</option>
                <option value="wild_boar">INDIAN WILD BOAR (12)</option>
                <option value="gaur_bison">GAUR BISON (8)</option>
                <option value="bonnet_macaque">BONNET MACAQUE (8)</option>
              </select>
            </div>
            <div class="individual-animal-scrollbox" id="individualAnimalList">
              <!-- Rendered dynamically by app.js -->
            </div>
          </div>
        </div>"""

assert target_panel_end in html, "target_panel_end not found in index.html"
html = html.replace(target_panel_end, replacement_panel_end, 1)

with open(INDEX_HTML, "w", encoding="utf-8") as f:
    f.write(html)

print("index.html patched successfully!")

# 2. Patch style.css
with open(STYLE_CSS, "r", encoding="utf-8") as f:
    css = f.read()

extra_css = """
/* ==========================================================================
   Neural Network Bounding Box Overlay & Smart Fence Styles
   ========================================================================== */
.pov-feed-container {
  position: relative;
}

.pov-bbox-overlay-canvas {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  pointer-events: none;
  z-index: 12;
}

.deterrent-controls-section {
  margin-top: 10px;
  background: rgba(15, 23, 42, 0.6);
  border: 1px solid rgba(245, 158, 11, 0.3);
  border-radius: 6px;
  padding: 8px;
}

.deterrent-btn-grid {
  display: grid;
  grid-template-columns: 1fr 1fr 1fr;
  gap: 6px;
  margin-top: 6px;
}

.det-btn {
  background: rgba(30, 41, 59, 0.8);
  border: 1px solid rgba(245, 158, 11, 0.5);
  color: #f1f5f9;
  font-size: 9px;
  font-weight: 700;
  padding: 6px 4px;
  border-radius: 4px;
  cursor: pointer;
  transition: all 0.2s ease;
  text-align: center;
}

.det-btn:hover {
  background: rgba(245, 158, 11, 0.25);
  border-color: #f59e0b;
}

.deterrent-status-box {
  margin-top: 6px;
  font-size: 10px;
  font-family: monospace;
  color: #94a3b8;
  text-align: center;
}

.animal-directory-section {
  margin-top: 10px;
  background: rgba(15, 23, 42, 0.6);
  border: 1px solid rgba(56, 189, 248, 0.3);
  border-radius: 6px;
  padding: 8px;
}

.animal-filter-bar {
  margin-top: 6px;
}

.animal-filter-select {
  width: 100%;
  background: #0f172a;
  color: #38bdf8;
  border: 1px solid rgba(56, 189, 248, 0.4);
  font-size: 10px;
  font-family: monospace;
  font-weight: 700;
  padding: 4px 6px;
  border-radius: 4px;
}

.individual-animal-scrollbox {
  margin-top: 8px;
  max-height: 180px;
  overflow-y: auto;
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.animal-roster-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  background: rgba(30, 41, 59, 0.5);
  border: 1px solid rgba(255, 255, 255, 0.08);
  border-radius: 4px;
  padding: 5px 8px;
  cursor: pointer;
  transition: all 0.15s ease;
}

.animal-roster-row:hover {
  background: rgba(56, 189, 248, 0.15);
  border-color: rgba(56, 189, 248, 0.5);
}

.animal-row-main {
  display: flex;
  flex-direction: column;
  gap: 1px;
}

.animal-row-name {
  font-size: 11px;
  font-weight: 700;
  color: #f8fafc;
}

.animal-row-spec {
  font-size: 8px;
  font-family: monospace;
  color: #94a3b8;
}

.animal-row-task {
  font-size: 9px;
  color: #cbd5e1;
  max-width: 110px;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.animal-row-status {
  font-size: 8px;
}

.badge-green {
  background: rgba(16, 185, 129, 0.2);
  color: #10b981;
  border: 1px solid rgba(16, 185, 129, 0.4);
  padding: 1px 4px;
  border-radius: 3px;
  font-weight: 700;
}

.badge-amber {
  background: rgba(245, 158, 11, 0.2);
  color: #f59e0b;
  border: 1px solid rgba(245, 158, 11, 0.4);
  padding: 1px 4px;
  border-radius: 3px;
  font-weight: 700;
  animation: pulse-badge 1s infinite alternate;
}

.badge-rose {
  background: rgba(244, 63, 94, 0.25);
  color: #f43f5e;
  border: 1px solid rgba(244, 63, 94, 0.6);
  padding: 1px 4px;
  border-radius: 3px;
  font-weight: 800;
  animation: pulse-badge 0.5s infinite alternate;
}

.badge-cyan {
  background: rgba(6, 182, 212, 0.2);
  color: #06b6d4;
  border: 1px solid rgba(6, 182, 212, 0.4);
  padding: 1px 4px;
  border-radius: 3px;
  font-weight: 700;
}

@keyframes pulse-badge {
  0% { opacity: 0.7; }
  100% { opacity: 1.0; transform: scale(1.03); }
}
"""

css += extra_css

with open(STYLE_CSS, "w", encoding="utf-8") as f:
    f.write(css)

print("style.css patched successfully!")

