"""Patch index.html, style.css, and app.js with the PRW-Wild Physical Hardware Control Workbench."""
from pathlib import Path

# ==============================================================================
# 1. PATCH INDEX.HTML
# ==============================================================================
index_path = Path(r"D:\Simulation For DT\prw-wild-digital-twin\src\prw_wild\web\static\index.html")
index_content = index_path.read_text(encoding="utf-8")

# Add Hardware Control Bench button if not already present
btn_target = '<button class="hw-view-btn active" id="btnHwModeWorkbench" title="3D Multi-Board Physical Assembly with real 3D curved jumper cables">3D WIRING WORKBENCH</button>'
btn_replacement = """<button class="hw-view-btn active" id="btnHwModeWorkbench" title="3D Multi-Board Physical Assembly with real 3D curved jumper cables">3D WIRING WORKBENCH</button>
            <button class="hw-view-btn" id="btnHwModeControl" title="Physical hardware control workbench: toggle Layer 1, 2, 3 outputs, switch operating mode, and emergency all-off">HARDWARE CONTROL BENCH</button>"""
if "btnHwModeControl" not in index_content:
    assert btn_target in index_content, "btn_target not found in index.html"
    index_content = index_content.replace(btn_target, btn_replacement, 1)

# Add #tacticalHwQuickbar after detectionLayersOverlay if not already present
if "tacticalHwQuickbar" not in index_content:
    overlay_target = """            <!-- Floating Three-Layer Detection HUD Overlay -->
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
            </div>"""

    overlay_replacement = """            <!-- Floating Three-Layer Detection HUD Overlay -->
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

            <!-- Tactical Hardware Quick-Control HUD Overlay -->
            <div class="tactical-hw-quickbar" id="tacticalHwQuickbar">
              <div class="thw-mode-pill" id="thwModePill">MODE: SIM ONLY</div>
              <div class="thw-controls">
                <button class="thw-btn" id="quickL1Toggle" title="Toggle Layer 1 (CSI / ESP32 GPIO38)">L1: <span id="quickL1State">OFF</span></button>
                <button class="thw-btn" id="quickL2Toggle" title="Toggle Layer 2 (Sensor Network Relay)">L2: <span id="quickL2State">OFF</span></button>
                <button class="thw-btn" id="quickL3Toggle" title="Toggle Layer 3 (Camera CAM_01)">L3: <span id="quickL3State">OFF</span></button>
                <button class="thw-btn danger" id="quickAllOff" title="Trigger Emergency All-Off">🚨 ALL-OFF</button>
                <button class="thw-btn bench-link" id="quickOpenBench" title="Open Full Hardware Control Workbench">🛠️ BENCH</button>
              </div>
            </div>"""

    assert overlay_target in index_content, "overlay_target not found in index.html"
    index_content = index_content.replace(overlay_target, overlay_replacement, 1)

# Add #hardwareControlContainer into #hw-viewport-container if not already present
if "hardwareControlContainer" not in index_content:
    hw_viewport_target = """              <!-- Interactive Wiring Schematic View (Toggleable) -->
              <div id="hardwareWiringContainer" class="hw-wiring-viewport hidden">
                <canvas id="hardwareWiringCanvas" width="720" height="520"></canvas>
                <div class="wiring-legend">
                  <div class="wl-item"><span class="wl-color red"></span> 5V DC Supply (PIR VCC)</div>
                  <div class="wl-item"><span class="wl-color orange"></span> 3.3V DC Supply (Vibration / Mic)</div>
                  <div class="wl-item"><span class="wl-color black"></span> Common Ground (GND)</div>
                  <div class="wl-item"><span class="wl-color cyan"></span> Digital Signal (GPIO4 / GPIO5)</div>
                  <div class="wl-item"><span class="wl-color purple"></span> I2S Audio Bus (GPIO7 / 8 / 9)</div>
                </div>
              </div>"""

    hw_viewport_replacement = hw_viewport_target + """

              <!-- Hardware Physical Control Bench Viewport -->
              <div id="hardwareControlContainer" class="hw-control-viewport hidden">
                <div class="hw-control-panel-inner">
                  <!-- Operating Mode Selection Header -->
                  <div class="hw-mode-selection-box">
                    <div class="hw-box-title">
                      <span class="icon">⚙️</span> SYSTEM OPERATING MODE:
                      <span class="hw-active-mode-badge" id="hwActiveModeBadge">SIMULATION ONLY</span>
                    </div>
                    <div class="hw-mode-buttons">
                      <button class="btn-hw-mode active" id="btnModeSimOnly" data-mode="SIMULATION_ONLY">
                        <span class="mode-icon">🧪</span>
                        <div class="mode-info">
                          <strong>SIMULATION ONLY</strong>
                          <small>Safe SIL virtualization — real hardware outputs disarmed</small>
                        </div>
                      </button>
                      <button class="btn-hw-mode" id="btnModeHwTest" data-mode="HARDWARE_TEST">
                        <span class="mode-icon">🛠️</span>
                        <div class="mode-info">
                          <strong>HARDWARE TEST</strong>
                          <small>Manual bench test mode — toggle L1, L2, L3 independently</small>
                        </div>
                      </button>
                      <button class="btn-hw-mode" id="btnModeAuto" data-mode="AUTO_HARDWARE_CONTROL">
                        <span class="mode-icon">⚡</span>
                        <div class="mode-info">
                          <strong>AUTO HARDWARE CONTROL</strong>
                          <small>Virtual animal movements dynamically command physical outputs</small>
                        </div>
                      </button>
                    </div>
                  </div>

                  <!-- Three Fixed Layers Actuation Grid -->
                  <div class="hw-layers-control-grid">
                    <!-- Layer 1 Card -->
                    <div class="hw-layer-actuator-card l1-card" id="cardLayer1">
                      <div class="card-top">
                        <div class="layer-title-wrap">
                          <span class="l-badge l1">LAYER 1 (OUTER)</span>
                          <h4>Wi-Fi CSI / ESP32 Actuator</h4>
                        </div>
                        <span class="conn-pill simulated" id="l1ConnStatus">SIMULATED (NO USB)</span>
                      </div>
                      <p class="hw-card-desc">Target: <code>ESP32-S3-DevKitC-1 v1.1</code> (GPIO38 / WS2812 RGB). Triggers outer perimeter CSI presence alert.</p>
                      
                      <div class="hw-state-row">
                        <div class="hw-state-indicator" id="l1StateIndicator">
                          <span class="state-dot"></span>
                          <span class="state-text" id="l1StateText">STATE: OFF</span>
                        </div>
                        <div class="hw-latency-text" id="l1LatencyText">ACK: -- ms</div>
                      </div>

                      <div class="hw-button-row">
                        <button class="btn-actuate on l1" id="btnL1On">ACTIVATE (ON)</button>
                        <button class="btn-actuate off" id="btnL1Off">DEACTIVATE (OFF)</button>
                      </div>
                    </div>

                    <!-- Layer 2 Card -->
                    <div class="hw-layer-actuator-card l2-card" id="cardLayer2">
                      <div class="card-top">
                        <div class="layer-title-wrap">
                          <span class="l-badge l2">LAYER 2 (MIDDLE)</span>
                          <h4>Sensor Network Indicator</h4>
                        </div>
                        <span class="conn-pill simulated" id="l2ConnStatus">SIMULATED</span>
                      </div>
                      <p class="hw-card-desc">Target: <code>STATION_SENSOR_NET_01</code> Relay & Indication Bus. Actuates acoustic/PIR/vibration indicators.</p>
                      
                      <div class="hw-state-row">
                        <div class="hw-state-indicator" id="l2StateIndicator">
                          <span class="state-dot"></span>
                          <span class="state-text" id="l2StateText">STATE: OFF</span>
                        </div>
                        <div class="hw-latency-text" id="l2LatencyText">ACK: -- ms</div>
                      </div>

                      <div class="hw-button-row">
                        <button class="btn-actuate on l2" id="btnL2On">ACTIVATE (ON)</button>
                        <button class="btn-actuate off" id="btnL2Off">DEACTIVATE (OFF)</button>
                      </div>
                    </div>

                    <!-- Layer 3 Card -->
                    <div class="hw-layer-actuator-card l3-card" id="cardLayer3">
                      <div class="card-top">
                        <div class="layer-title-wrap">
                          <span class="l-badge l3">LAYER 3 (INNER)</span>
                          <h4>Physical Camera Surveillance</h4>
                        </div>
                        <span class="conn-pill simulated" id="l3ConnStatus">SIMULATED</span>
                      </div>
                      <p class="hw-card-desc">Target: <code>CAM_01 / ESP32-CAM OV2640</code> PTZ mast. Wakes optical camera and initiates visual AI confirmation capture.</p>
                      
                      <div class="hw-state-row">
                        <div class="hw-state-indicator" id="l3StateIndicator">
                          <span class="state-dot"></span>
                          <span class="state-text" id="l3StateText">STATE: OFF (STANDBY)</span>
                        </div>
                        <div class="hw-latency-text" id="l3LatencyText">ACK: -- ms</div>
                      </div>

                      <div class="hw-button-row">
                        <button class="btn-actuate on l3" id="btnL3On">WAKE & CAPTURE (ON)</button>
                        <button class="btn-actuate off" id="btnL3Off">STANDBY (OFF)</button>
                      </div>
                    </div>
                  </div>

                  <!-- Emergency Action & Master Bar -->
                  <div class="hw-master-action-bar">
                    <button class="btn-emergency-stop" id="btnHwEmergencyStop" title="Immediately halt all physical and simulated hardware outputs">
                      <span class="em-icon">🚨</span>
                      <span class="em-text">EMERGENCY ALL-OFF (HALT ALL OUTPUTS)</span>
                    </button>
                    <button class="btn-refresh-hw" id="btnRefreshHwStatus" title="Poll latest hardware state">
                      🔄 REFRESH TELEMETRY
                    </button>
                  </div>

                  <!-- Live Command Telemetry Terminal Log -->
                  <div class="hw-telemetry-box">
                    <div class="telemetry-hdr">
                      <span>LIVE HARDWARE COMMAND & ACK TELEMETRY LOG</span>
                      <span class="telemetry-count" id="telemetryCount">0 events logged</span>
                    </div>
                    <div class="telemetry-log" id="hwTelemetryLog">
                      <div class="log-line info">[SYSTEM INIT] Hardware control service initialized. Operating mode: SIMULATION ONLY.</div>
                    </div>
                  </div>
                </div>
              </div>"""

    assert hw_viewport_target in index_content, "hw_viewport_target not found in index.html"
    index_content = index_content.replace(hw_viewport_target, hw_viewport_replacement, 1)

index_path.write_text(index_content, encoding="utf-8")
print("index.html successfully updated!")

# ==============================================================================
# 2. PATCH STYLE.CSS
# ==============================================================================
css_path = Path(r"D:\Simulation For DT\prw-wild-digital-twin\src\prw_wild\web\static\style.css")
css_content = css_path.read_text(encoding="utf-8")

if "PRW-WILD PHYSICAL HARDWARE CONTROL BENCH" not in css_content:
    css_additions = """
/* ==========================================================================
   PRW-WILD PHYSICAL HARDWARE CONTROL BENCH & TACTICAL QUICKBAR
   ========================================================================== */

.tactical-hw-quickbar {
  position: absolute;
  top: 72px;
  right: 18px;
  z-index: 25;
  display: flex;
  align-items: center;
  gap: 8px;
  background: rgba(15, 23, 42, 0.90);
  backdrop-filter: blur(8px);
  border: 1px solid rgba(255, 255, 255, 0.12);
  border-radius: var(--radius-sm);
  padding: 5px 10px;
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.5);
  font-family: var(--font-mono);
}

.thw-mode-pill {
  font-size: 10px;
  font-weight: 700;
  padding: 3px 8px;
  border-radius: 4px;
  background: rgba(255, 255, 255, 0.08);
  color: var(--cyan-radar);
  border: 1px solid rgba(0, 240, 255, 0.25);
  letter-spacing: 0.5px;
}

.thw-controls {
  display: flex;
  gap: 6px;
}

.thw-btn {
  background: rgba(30, 41, 59, 0.8);
  border: 1px solid rgba(255, 255, 255, 0.15);
  color: var(--text-dim);
  font-family: var(--font-mono);
  font-size: 10px;
  padding: 3px 8px;
  border-radius: 4px;
  cursor: pointer;
  transition: all 0.2s ease;
}

.thw-btn:hover {
  background: rgba(51, 65, 85, 0.9);
  color: #fff;
  border-color: rgba(255, 255, 255, 0.3);
}

.thw-btn.active-l1 {
  background: rgba(0, 240, 255, 0.25);
  color: var(--cyan-radar);
  border-color: var(--cyan-radar);
  box-shadow: 0 0 10px var(--cyan-glow);
}

.thw-btn.active-l2 {
  background: rgba(245, 158, 11, 0.25);
  color: var(--amber-rf);
  border-color: var(--amber-rf);
  box-shadow: 0 0 10px var(--amber-glow);
}

.thw-btn.active-l3 {
  background: rgba(168, 85, 247, 0.25);
  color: var(--violet-camera);
  border-color: var(--violet-camera);
  box-shadow: 0 0 10px var(--violet-glow);
}

.thw-btn.danger {
  background: rgba(239, 68, 68, 0.2);
  color: #fca5a5;
  border-color: rgba(239, 68, 68, 0.4);
}

.thw-btn.danger:hover {
  background: #dc2626;
  color: #fff;
}

.thw-btn.bench-link {
  background: rgba(0, 240, 255, 0.15);
  color: var(--cyan-radar);
  border-color: rgba(0, 240, 255, 0.3);
}

/* Modal Hardware Control Bench Viewport */
.hw-control-viewport {
  width: 100%;
  height: 520px;
  background: radial-gradient(circle at 50% 30%, #0d1527 0%, #060913 100%);
  border-radius: var(--radius-sm);
  padding: 18px;
  box-sizing: border-box;
  overflow-y: auto;
}

.hw-control-panel-inner {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

/* Operating Mode Selector */
.hw-mode-selection-box {
  background: rgba(15, 23, 42, 0.7);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: var(--radius-sm);
  padding: 12px 16px;
}

.hw-box-title {
  display: flex;
  align-items: center;
  gap: 8px;
  font-family: var(--font-mono);
  font-size: 11.5px;
  color: var(--text-muted);
  margin-bottom: 10px;
}

.hw-active-mode-badge {
  font-weight: 700;
  color: var(--cyan-radar);
  background: rgba(0, 240, 255, 0.12);
  padding: 2px 8px;
  border-radius: 4px;
  border: 1px solid rgba(0, 240, 255, 0.3);
}

.hw-mode-buttons {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 10px;
}

.btn-hw-mode {
  display: flex;
  align-items: center;
  gap: 10px;
  background: rgba(30, 41, 59, 0.5);
  border: 1px solid rgba(255, 255, 255, 0.12);
  border-radius: var(--radius-sm);
  padding: 10px 12px;
  text-align: left;
  cursor: pointer;
  transition: all 0.2s ease;
  color: var(--text-dim);
}

.btn-hw-mode:hover {
  background: rgba(51, 65, 85, 0.6);
  border-color: rgba(255, 255, 255, 0.25);
  color: #fff;
}

.btn-hw-mode.active {
  background: rgba(0, 240, 255, 0.15);
  border-color: var(--cyan-radar);
  box-shadow: 0 0 14px rgba(0, 240, 255, 0.2);
  color: #fff;
}

.btn-hw-mode .mode-icon {
  font-size: 20px;
}

.btn-hw-mode .mode-info strong {
  display: block;
  font-family: var(--font-mono);
  font-size: 11px;
  letter-spacing: 0.5px;
}

.btn-hw-mode .mode-info small {
  display: block;
  font-size: 9.5px;
  color: var(--text-muted);
  line-height: 1.3;
}

/* Layer Actuator Grid */
.hw-layers-control-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 12px;
}

.hw-layer-actuator-card {
  background: rgba(15, 23, 42, 0.85);
  border: 1px solid rgba(255, 255, 255, 0.12);
  border-radius: var(--radius-sm);
  padding: 14px;
  display: flex;
  flex-direction: column;
  gap: 10px;
  transition: all 0.3s ease;
}

.hw-layer-actuator-card.l1-card.active-on {
  border-color: var(--cyan-radar);
  box-shadow: 0 0 16px rgba(0, 240, 255, 0.25);
}

.hw-layer-actuator-card.l2-card.active-on {
  border-color: var(--amber-rf);
  box-shadow: 0 0 16px rgba(245, 158, 11, 0.25);
}

.hw-layer-actuator-card.l3-card.active-on {
  border-color: var(--violet-camera);
  box-shadow: 0 0 16px rgba(168, 85, 247, 0.25);
}

.card-top {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  gap: 8px;
}

.layer-title-wrap h4 {
  margin: 4px 0 0;
  font-size: 12px;
  font-weight: 600;
  color: #fff;
}

.l-badge {
  display: inline-block;
  font-family: var(--font-mono);
  font-size: 9px;
  font-weight: 700;
  padding: 2px 6px;
  border-radius: 3px;
}

.l-badge.l1 { background: rgba(0, 240, 255, 0.2); color: var(--cyan-radar); }
.l-badge.l2 { background: rgba(245, 158, 11, 0.2); color: var(--amber-rf); }
.l-badge.l3 { background: rgba(168, 85, 247, 0.2); color: var(--violet-camera); }

.conn-pill {
  font-family: var(--font-mono);
  font-size: 9px;
  font-weight: 700;
  padding: 2px 6px;
  border-radius: 3px;
}

.conn-pill.simulated {
  background: rgba(148, 163, 184, 0.15);
  color: #94a3b8;
  border: 1px solid rgba(148, 163, 184, 0.3);
}

.conn-pill.connected {
  background: rgba(34, 197, 94, 0.2);
  color: #4ade80;
  border: 1px solid #22c55e;
}

.hw-card-desc {
  font-size: 10.5px;
  color: var(--text-dim);
  line-height: 1.4;
  margin: 0;
  flex: 1;
}

.hw-card-desc code {
  background: rgba(0, 0, 0, 0.3);
  padding: 1px 4px;
  border-radius: 3px;
  color: var(--cyan-radar);
  font-size: 10px;
}

.hw-state-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  background: rgba(0, 0, 0, 0.3);
  padding: 6px 10px;
  border-radius: 4px;
}

.hw-state-indicator {
  display: flex;
  align-items: center;
  gap: 6px;
  font-family: var(--font-mono);
  font-size: 10.5px;
  font-weight: 700;
  color: var(--text-muted);
}

.state-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background: #64748b;
  transition: all 0.3s ease;
}

.hw-state-indicator.state-on .state-dot {
  background: #22c55e;
  box-shadow: 0 0 8px #22c55e;
}

.hw-state-indicator.state-on.l1 .state-dot {
  background: var(--cyan-radar);
  box-shadow: 0 0 8px var(--cyan-radar);
}

.hw-state-indicator.state-on.l2 .state-dot {
  background: var(--amber-rf);
  box-shadow: 0 0 8px var(--amber-rf);
}

.hw-state-indicator.state-on.l3 .state-dot {
  background: var(--violet-camera);
  box-shadow: 0 0 8px var(--violet-camera);
}

.hw-latency-text {
  font-family: var(--font-mono);
  font-size: 10px;
  color: var(--text-dim);
}

.hw-button-row {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 8px;
}

.btn-actuate {
  font-family: var(--font-mono);
  font-size: 10px;
  font-weight: 700;
  padding: 6px 8px;
  border-radius: 4px;
  cursor: pointer;
  border: 1px solid transparent;
  transition: all 0.2s ease;
}

.btn-actuate.on {
  background: rgba(34, 197, 94, 0.2);
  color: #4ade80;
  border-color: rgba(34, 197, 94, 0.4);
}

.btn-actuate.on:hover {
  background: #16a34a;
  color: #fff;
}

.btn-actuate.on.l1:hover {
  background: #06b6d4;
  color: #fff;
}

.btn-actuate.on.l2:hover {
  background: #d97706;
  color: #fff;
}

.btn-actuate.on.l3:hover {
  background: #9333ea;
  color: #fff;
}

.btn-actuate.off {
  background: rgba(239, 68, 68, 0.15);
  color: #fca5a5;
  border-color: rgba(239, 68, 68, 0.3);
}

.btn-actuate.off:hover {
  background: #dc2626;
  color: #fff;
}

/* Master Emergency Action Bar */
.hw-master-action-bar {
  display: flex;
  gap: 12px;
}

.btn-emergency-stop {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 10px;
  background: linear-gradient(135deg, #b91c1c 0%, #7f1d1d 100%);
  border: 1px solid #ef4444;
  color: #fff;
  font-family: var(--font-mono);
  font-size: 12px;
  font-weight: 700;
  letter-spacing: 0.8px;
  padding: 10px 18px;
  border-radius: var(--radius-sm);
  cursor: pointer;
  box-shadow: 0 0 16px rgba(239, 68, 68, 0.4);
  transition: all 0.2s ease;
}

.btn-emergency-stop:hover {
  background: #dc2626;
  box-shadow: 0 0 24px rgba(239, 68, 68, 0.7);
  transform: scale(1.01);
}

.btn-refresh-hw {
  background: rgba(30, 41, 59, 0.8);
  border: 1px solid rgba(255, 255, 255, 0.15);
  color: var(--text-dim);
  font-family: var(--font-mono);
  font-size: 11px;
  padding: 10px 16px;
  border-radius: var(--radius-sm);
  cursor: pointer;
  transition: all 0.2s ease;
}

.btn-refresh-hw:hover {
  background: rgba(51, 65, 85, 0.9);
  color: #fff;
}

/* Telemetry Log Terminal */
.hw-telemetry-box {
  background: rgba(10, 14, 23, 0.95);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: var(--radius-sm);
  overflow: hidden;
}

.telemetry-hdr {
  display: flex;
  justify-content: space-between;
  align-items: center;
  background: rgba(15, 23, 42, 0.8);
  padding: 6px 12px;
  font-family: var(--font-mono);
  font-size: 10px;
  color: var(--text-muted);
  border-bottom: 1px solid rgba(255, 255, 255, 0.08);
}

.telemetry-log {
  max-height: 110px;
  overflow-y: auto;
  padding: 8px 12px;
  font-family: var(--font-mono);
  font-size: 10px;
  line-height: 1.5;
  display: flex;
  flex-direction: column-reverse;
}

.log-line {
  color: #94a3b8;
}

.log-line.cmd-l1 { color: var(--cyan-radar); }
.log-line.cmd-l2 { color: var(--amber-rf); }
.log-line.cmd-l3 { color: var(--violet-camera); }
.log-line.emergency { color: #f87171; font-weight: 700; }
"""
    css_content += css_additions
    css_path.write_text(css_content, encoding="utf-8")
    print("style.css successfully updated!")
else:
    print("style.css already contains hardware control styles.")
