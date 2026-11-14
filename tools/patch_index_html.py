"""Patches index.html to add Mode F and Ecosystem Command Centre."""
from pathlib import Path

html_path = Path("src/prw_wild/web/static/index.html")
content = html_path.read_text(encoding="utf-8")

# 1. Add Mode F tab button
tab_target = 'MODE E: HARDWARE LAB\n        </button>'
tab_replacement = """MODE E: HARDWARE LAB
        </button>
        <button class="lab-mode-tab" data-mode="ecosystem" id="tabModeEcosystem" title="Multi-Animal Autonomous Ecosystem AI Command Centre (50+ Agents, Real Vision & Tracking)">
          <span class="tab-icon">🐅</span> MODE F: MULTI-ANIMAL AI
        </button>"""

if 'data-mode="ecosystem"' not in content:
    content = content.replace(tab_target, tab_replacement)
    print("Added Mode F tab")

# 2. Add Ecosystem Intelligence Panel in sidebar
sidebar_target = '<aside class="sidebar-section">\n        <!-- Gated Camera Viewport Simulator -->'
panel_html = """<aside class="sidebar-section">
        <!-- Multi-Animal Ecosystem Intelligence & Real Vision AI Panel -->
        <div class="side-panel ecosystem-panel" id="ecosystemPanel">
          <div class="panel-header">
            <div class="panel-title">
              <span class="panel-tag">WILDLIFE ECOSYSTEM INTELLIGENCE</span>
              <span class="pop-count-badge" id="hudPopCountBadge">60 SIMULATED</span>
            </div>
            <span class="vision-status-chip" id="hudVisionBackendChip">AI VISION: ACTIVE</span>
          </div>

          <!-- Species Distribution Grid -->
          <div class="species-roster-grid" id="speciesRosterGrid">
            <div class="species-chip elephant"><span class="sp-icon">🐘</span> Elephant <strong id="cnt_elephant">8</strong></div>
            <div class="species-chip chital"><span class="sp-icon">🦌</span> Chital <strong id="cnt_chital">18</strong></div>
            <div class="species-chip sambar"><span class="sp-icon">🦌</span> Sambar <strong id="cnt_sambar">8</strong></div>
            <div class="species-chip boar"><span class="sp-icon">🐗</span> Boar <strong id="cnt_boar">12</strong></div>
            <div class="species-chip gaur"><span class="sp-icon">🐂</span> Gaur <strong id="cnt_gaur">6</strong></div>
            <div class="species-chip macaque"><span class="sp-icon">🐒</span> Macaque <strong id="cnt_macaque">8</strong></div>
          </div>

          <!-- Real-Time AI Detection & Tracking Telemetry -->
          <div class="vision-ai-telemetry-box">
            <div class="vai-row">
              <span>AI Visual Detections:</span>
              <strong id="valAiDetections" class="text-cyan">0 DETECTED</strong>
            </div>
            <div class="vai-row">
              <span>Active SORT Tracks:</span>
              <strong id="valAiTracks" class="text-emerald">0 TRACKED</strong>
            </div>
            <div class="vai-row">
              <span>Confidence Calibration:</span>
              <strong class="text-amber">RAW (NOT CALIBRATED)</strong>
            </div>
            <div class="vai-row">
              <span>Perimeter Crossing Risk:</span>
              <strong id="valAiRiskScore" class="text-rose">0.00 (LOW)</strong>
            </div>
            <div class="vai-row">
              <span>Predicted Warning ETA:</span>
              <strong id="valAiEta" class="text-white">-- s</strong>
            </div>
          </div>

          <!-- Dynamic Operator Manual Injection Controls -->
          <div class="ecosystem-controls-section">
            <div class="ec-section-title">MANUAL OPERATOR INJECTION</div>
            <div class="ec-btn-row">
              <button class="ec-btn inject-approach" id="btnInjectApproach" title="Force animal to approach perimeter fence">🚨 APPROACH</button>
              <button class="ec-btn inject-turnaway" id="btnInjectTurnAway" title="Force animal to turn back into forest">↩ TURN AWAY</button>
              <button class="ec-btn inject-cross" id="btnInjectCross" title="Trigger realistic perimeter fence breach">⚡ CROSS BREACH</button>
            </div>
            <div class="ec-slider-row">
              <label for="popSizeSlider">POPULATION: <span id="lblPopSize">60</span></label>
              <input type="range" id="popSizeSlider" min="50" max="75" value="60" step="1">
              <button class="ec-btn-mini" id="btnApplyPopSize">RESET</button>
            </div>
          </div>

          <!-- Ecological Resource Monitors -->
          <div class="resource-monitor-section">
            <div class="ec-section-title">ECOLOGICAL RESOURCES</div>
            <div class="res-grid">
              <div class="res-card">
                <span class="res-label">💧 North Pond</span>
                <div class="res-bar"><div class="res-fill water" id="res_water_north" style="width: 100%;"></div></div>
              </div>
              <div class="res-card">
                <span class="res-label">💧 South Pond</span>
                <div class="res-bar"><div class="res-fill water" id="res_water_south" style="width: 100%;"></div></div>
              </div>
              <div class="res-card">
                <span class="res-label">🌿 Pasture</span>
                <div class="res-bar"><div class="res-fill grass" id="res_grass" style="width: 100%;"></div></div>
              </div>
              <div class="res-card">
                <span class="res-label">🌾 Farm Crops</span>
                <div class="res-bar"><div class="res-fill crops" id="res_crops" style="width: 100%;"></div></div>
              </div>
            </div>
          </div>
        </div>

        <!-- Gated Camera Viewport Simulator -->"""

if 'id="ecosystemPanel"' not in content:
    content = content.replace(sidebar_target, panel_html)
    print("Added Ecosystem Panel")

html_path.write_text(content, encoding="utf-8")
print("Done patching index.html")

