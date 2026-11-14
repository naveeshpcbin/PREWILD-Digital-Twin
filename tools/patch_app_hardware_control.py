"""Patch app.js with PRW-Wild Hardware Control Workbench, mode switching, manual overrides, and 3D visual layer actuation."""
from pathlib import Path

app_path = Path(r"D:\Simulation For DT\prw-wild-digital-twin\src\prw_wild\web\static\app.js")
content = app_path.read_text(encoding="utf-8")

# 1. Update setSelectedHardwareDevice mode switching
submode_old = """    // 2. Synchronize Mode Buttons
    document.getElementById('btnHwModeWorkbench')?.classList.toggle('active', hwCurrentSubMode === 'workbench');
    document.getElementById('btnHwMode3D')?.classList.toggle('active', hwCurrentSubMode === '3d');
    document.getElementById('btnHwModeWiring')?.classList.toggle('active', hwCurrentSubMode === 'wiring');

    // 3. Container & Filter Group Visibility
    const isWiring = (hwCurrentSubMode === 'wiring');
    document.getElementById('hardwareLab3DContainer')?.classList.toggle('hidden', isWiring);
    document.getElementById('hardwareWiringContainer')?.classList.toggle('hidden', !isWiring);

    const isWorkbench = (hwCurrentSubMode === 'workbench');
    document.getElementById('hwWireFilterGroup')?.classList.toggle('hidden', !isWorkbench);
    document.getElementById('btnToggleWires')?.classList.toggle('hidden', !isWorkbench);

    if (wiringAnimId) cancelAnimationFrame(wiringAnimId);

    // If 2D wiring schematic mode, render 2D canvas and exit
    if (isWiring) {
      renderHardwareWiring();
      return;
    }"""

submode_new = """    // 2. Synchronize Mode Buttons
    document.getElementById('btnHwModeWorkbench')?.classList.toggle('active', hwCurrentSubMode === 'workbench');
    document.getElementById('btnHwModeControl')?.classList.toggle('active', hwCurrentSubMode === 'control');
    document.getElementById('btnHwMode3D')?.classList.toggle('active', hwCurrentSubMode === '3d');
    document.getElementById('btnHwModeWiring')?.classList.toggle('active', hwCurrentSubMode === 'wiring');

    // 3. Container & Filter Group Visibility
    const isWiring = (hwCurrentSubMode === 'wiring');
    const isControl = (hwCurrentSubMode === 'control');
    document.getElementById('hardwareLab3DContainer')?.classList.toggle('hidden', isWiring || isControl);
    document.getElementById('hardwareWiringContainer')?.classList.toggle('hidden', !isWiring);
    document.getElementById('hardwareControlContainer')?.classList.toggle('hidden', !isControl);

    const isWorkbench = (hwCurrentSubMode === 'workbench');
    document.getElementById('hwWireFilterGroup')?.classList.toggle('hidden', !isWorkbench);
    document.getElementById('btnToggleWires')?.classList.toggle('hidden', !isWorkbench);

    if (wiringAnimId) cancelAnimationFrame(wiringAnimId);

    if (isControl) {
      fetchHardwareStatusAndUpdateUI();
      return;
    }

    // If 2D wiring schematic mode, render 2D canvas and exit
    if (isWiring) {
      renderHardwareWiring();
      return;
    }"""

assert submode_old in content, "submode_old not found in app.js"
content = content.replace(submode_old, submode_new, 1)

# 2. Add btnHwModeControl click listener
click_target = """    // Sub-mode switchers
    document.getElementById('btnHwModeWorkbench')?.addEventListener('click', () => {
      setSelectedHardwareDevice('workbench', { mode: 'workbench' });
    });"""

click_replacement = """    // Sub-mode switchers
    document.getElementById('btnHwModeWorkbench')?.addEventListener('click', () => {
      setSelectedHardwareDevice('workbench', { mode: 'workbench' });
    });

    document.getElementById('btnHwModeControl')?.addEventListener('click', () => {
      setSelectedHardwareDevice('workbench', { mode: 'control' });
    });"""

assert click_target in content, "click_target not found in app.js"
content = content.replace(click_target, click_replacement, 1)

# 3. Add Hardware Control Functions and UI Event Listeners
hw_functions = """
  // ==========================================================================
  // PRW-Wild Physical Hardware Control Workbench Implementation
  // ==========================================================================
  let cachedHardwareStatus = null;
  let hwTelemetryEventsCount = 0;

  function appendHardwareTelemetryLog(message, type = 'info') {
    const logBox = document.getElementById('hwTelemetryLog');
    if (!logBox) return;
    const line = document.createElement('div');
    line.className = `log-line ${type}`;
    const ts = new Date().toLocaleTimeString();
    line.textContent = `[${ts}] ${message}`;
    logBox.insertBefore(line, logBox.firstChild);
    hwTelemetryEventsCount++;
    const countEl = document.getElementById('telemetryCount');
    if (countEl) countEl.textContent = `${hwTelemetryEventsCount} events logged`;
    while (logBox.children.length > 50) {
      logBox.removeChild(logBox.lastChild);
    }
  }

  async function fetchHardwareStatusAndUpdateUI() {
    try {
      const res = await fetch('/api/hardware/status');
      if (!res.ok) return;
      const status = await res.json();
      cachedHardwareStatus = status;
      applyHardwareStatus(status);
    } catch (err) {
      console.warn('[PRW-Wild Hardware] Error fetching hardware status:', err);
    }
  }

  function applyHardwareStatus(status, counts = null) {
    if (!status) return;
    cachedHardwareStatus = status;

    // 1. Operating Mode Badges & Buttons
    const mode = status.operating_mode || 'SIMULATION_ONLY';
    const modeBadge = document.getElementById('hwActiveModeBadge');
    if (modeBadge) modeBadge.textContent = mode.replace(/_/g, ' ');

    const thwPill = document.getElementById('thwModePill');
    if (thwPill) thwPill.textContent = 'MODE: ' + (mode === 'SIMULATION_ONLY' ? 'SIM ONLY' : (mode === 'HARDWARE_TEST' ? 'BENCH TEST' : 'AUTO CONTROL'));

    document.getElementById('btnModeSimOnly')?.classList.toggle('active', mode === 'SIMULATION_ONLY');
    document.getElementById('btnModeHwTest')?.classList.toggle('active', mode === 'HARDWARE_TEST');
    document.getElementById('btnModeAuto')?.classList.toggle('active', mode === 'AUTO_HARDWARE_CONTROL');

    const l1 = status.layers?.layer_1 || {};
    const l2 = status.layers?.layer_2 || {};
    const l3 = status.layers?.layer_3 || {};

    const l1On = (l1.state === 'ON');
    const l2On = (l2.state === 'ON');
    const l3On = (l3.state === 'ON');

    // 2. Main Viewport Floating Three-Layer Detection Badges
    const b1 = document.getElementById('hudLayer1Badge');
    const b2 = document.getElementById('hudLayer2Badge');
    const b3 = document.getElementById('hudLayer3Badge');
    if (b1) b1.classList.toggle('active', l1On);
    if (b2) b2.classList.toggle('active', l2On);
    if (b3) b3.classList.toggle('active', l3On);

    const s1 = document.getElementById('hudLayer1Status');
    const s2 = document.getElementById('hudLayer2Status');
    const s3 = document.getElementById('hudLayer3Status');
    if (s1) s1.textContent = (l1On ? 'ACTIVE' : 'IDLE') + (counts ? ` (${counts[1] || 0})` : '');
    if (s2) s2.textContent = (l2On ? 'ACTIVE' : 'IDLE') + (counts ? ` (${counts[2] || 0})` : '');
    if (s3) s3.textContent = (l3On ? 'STREAMING' : 'STANDBY') + (counts ? ` (${counts[3] || 0})` : '');

    // 3. Tactical Quick-Bar Buttons
    const q1 = document.getElementById('quickL1Toggle');
    const q2 = document.getElementById('quickL2Toggle');
    const q3 = document.getElementById('quickL3Toggle');
    const q1s = document.getElementById('quickL1State');
    const q2s = document.getElementById('quickL2State');
    const q3s = document.getElementById('quickL3State');

    if (q1) q1.classList.toggle('active-l1', l1On);
    if (q1s) q1s.textContent = l1.state || 'OFF';
    if (q2) q2.classList.toggle('active-l2', l2On);
    if (q2s) q2s.textContent = l2.state || 'OFF';
    if (q3) q3.classList.toggle('active-l3', l3On);
    if (q3s) q3s.textContent = l3.state || 'OFF';

    // 4. Modal Control Cards
    const c1 = document.getElementById('cardLayer1');
    const c2 = document.getElementById('cardLayer2');
    const c3 = document.getElementById('cardLayer3');
    if (c1) c1.classList.toggle('active-on', l1On);
    if (c2) c2.classList.toggle('active-on', l2On);
    if (c3) c3.classList.toggle('active-on', l3On);

    const ind1 = document.getElementById('l1StateIndicator');
    const ind2 = document.getElementById('l2StateIndicator');
    const ind3 = document.getElementById('l3StateIndicator');
    if (ind1) {
      ind1.classList.toggle('state-on', l1On);
      ind1.classList.toggle('l1', l1On);
      const txt = document.getElementById('l1StateText');
      if (txt) txt.textContent = `STATE: ${l1.state || 'OFF'}`;
    }
    if (ind2) {
      ind2.classList.toggle('state-on', l2On);
      ind2.classList.toggle('l2', l2On);
      const txt = document.getElementById('l2StateText');
      if (txt) txt.textContent = `STATE: ${l2.state || 'OFF'}`;
    }
    if (ind3) {
      ind3.classList.toggle('state-on', l3On);
      ind3.classList.toggle('l3', l3On);
      const txt = document.getElementById('l3StateText');
      if (txt) txt.textContent = `STATE: ${l3On ? 'ON (STREAMING)' : 'OFF (STANDBY)'}`;
    }

    // Connection truth pills
    const pill1 = document.getElementById('l1ConnStatus');
    if (pill1) {
      pill1.textContent = l1.physical_connected ? `PHYSICAL: ${l1.port_or_endpoint}` : 'SIMULATED (NO USB)';
      pill1.className = `conn-pill ${l1.physical_connected ? 'connected' : 'simulated'}`;
    }
    const pill2 = document.getElementById('l2ConnStatus');
    if (pill2) {
      pill2.textContent = l2.physical_connected ? 'PHYSICAL: CONNECTED' : 'SIMULATED';
      pill2.className = `conn-pill ${l2.physical_connected ? 'connected' : 'simulated'}`;
    }
    const pill3 = document.getElementById('l3ConnStatus');
    if (pill3) {
      pill3.textContent = l3.physical_connected ? `PHYSICAL: ${l3.port_or_endpoint}` : 'SIMULATED';
      pill3.className = `conn-pill ${l3.physical_connected ? 'connected' : 'simulated'}`;
    }

    // 5. Dynamic 3D Scene Actuation Feedback (Ground Envelopes)
    if (threeObjects.layer1Mesh && threeObjects.layer1Mesh.material) {
      threeObjects.layer1Mesh.material.opacity = l1On ? 0.32 : 0.08;
    }
    if (threeObjects.layer2Mesh && threeObjects.layer2Mesh.material) {
      threeObjects.layer2Mesh.material.opacity = l2On ? 0.35 : 0.09;
    }
    if (threeObjects.layer3Mesh && threeObjects.layer3Mesh.material) {
      threeObjects.layer3Mesh.material.opacity = l3On ? 0.42 : 0.12;
    }

    // Actuate 3D router packet LED
    if (threeObjects.routerLeds && threeObjects.routerLeds.length > 0) {
      const ledColor = l1On ? 0x00f0ff : 0x00ff88;
      threeObjects.routerLeds.forEach(led => {
        if (led.material) led.material.color.setHex(ledColor);
      });
    }

    // Actuate 3D Camera mast LED
    if (threeObjects.cameraMastGroup) {
      const camLed = threeObjects.cameraMastGroup.getObjectByName('CAM_POWER_LED');
      if (camLed && camLed.material) {
        camLed.material.color.setHex(l3On ? 0xa855f7 : 0x334155);
      }
    }
  }

  async function sendHardwareCommand(layer, action) {
    const t0 = performance.now();
    try {
      const res = await fetch('/api/hardware/command', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ layer: layer, action: action })
      });
      const data = await res.json();
      const dt = (performance.now() - t0).toFixed(1);
      
      const latEl = document.getElementById(`l${layer}LatencyText`);
      if (latEl) latEl.textContent = `ACK: ${dt} ms`;

      const typeClass = layer === 1 ? 'cmd-l1' : (layer === 2 ? 'cmd-l2' : 'cmd-l3');
      appendHardwareTelemetryLog(
        `LAYER ${layer} -> ${action} | ACK: ${data.acknowledged ? 'OK' : 'FAIL'} (${dt}ms) | Exec: ${data.physical_executed ? 'PHYSICAL' : 'SIMULATED'} | ${data.status_message}`,
        typeClass
      );
      await fetchHardwareStatusAndUpdateUI();
    } catch (e) {
      appendHardwareTelemetryLog(`LAYER ${layer} -> ${action} ERROR: ${e}`, 'emergency');
    }
  }

  async function setHardwareOperatingMode(mode) {
    try {
      const res = await fetch('/api/hardware/mode', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ mode: mode })
      });
      const data = await res.json();
      appendHardwareTelemetryLog(`OPERATING MODE CHANGED -> ${mode} | Status: ${data.success ? 'SUCCESS' : 'REJECTED'}`);
      await fetchHardwareStatusAndUpdateUI();
    } catch (e) {
      appendHardwareTelemetryLog(`MODE CHANGE ERROR: ${e}`, 'emergency');
    }
  }

  async function sendEmergencyAllOff() {
    try {
      const res = await fetch('/api/hardware/emergency_stop', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({})
      });
      const data = await res.json();
      appendHardwareTelemetryLog(`🚨 EMERGENCY ALL-OFF TRIGGERED! All layers commanded OFF immediately.`, 'emergency');
      await fetchHardwareStatusAndUpdateUI();
    } catch (e) {
      appendHardwareTelemetryLog(`EMERGENCY STOP ERROR: ${e}`, 'emergency');
    }
  }

  function initHardwareControlWorkbenchHandlers() {
    // Mode Selection Buttons
    document.getElementById('btnModeSimOnly')?.addEventListener('click', () => setHardwareOperatingMode('SIMULATION_ONLY'));
    document.getElementById('btnModeHwTest')?.addEventListener('click', () => setHardwareOperatingMode('HARDWARE_TEST'));
    document.getElementById('btnModeAuto')?.addEventListener('click', () => setHardwareOperatingMode('AUTO_HARDWARE_CONTROL'));

    // Manual Layer Actuator Buttons
    document.getElementById('btnL1On')?.addEventListener('click', () => sendHardwareCommand(1, 'ON'));
    document.getElementById('btnL1Off')?.addEventListener('click', () => sendHardwareCommand(1, 'OFF'));
    document.getElementById('btnL2On')?.addEventListener('click', () => sendHardwareCommand(2, 'ON'));
    document.getElementById('btnL2Off')?.addEventListener('click', () => sendHardwareCommand(2, 'OFF'));
    document.getElementById('btnL3On')?.addEventListener('click', () => sendHardwareCommand(3, 'ON'));
    document.getElementById('btnL3Off')?.addEventListener('click', () => sendHardwareCommand(3, 'OFF'));

    // Emergency Stops
    document.getElementById('btnHwEmergencyStop')?.addEventListener('click', () => sendEmergencyAllOff());
    document.getElementById('quickAllOff')?.addEventListener('click', () => sendEmergencyAllOff());

    // Refresh button
    document.getElementById('btnRefreshHwStatus')?.addEventListener('click', () => fetchHardwareStatusAndUpdateUI());

    // Tactical Quick-Bar Toggles
    document.getElementById('quickL1Toggle')?.addEventListener('click', () => {
      const currentState = cachedHardwareStatus?.layers?.layer_1?.state || 'OFF';
      sendHardwareCommand(1, currentState === 'ON' ? 'OFF' : 'ON');
    });
    document.getElementById('quickL2Toggle')?.addEventListener('click', () => {
      const currentState = cachedHardwareStatus?.layers?.layer_2?.state || 'OFF';
      sendHardwareCommand(2, currentState === 'ON' ? 'OFF' : 'ON');
    });
    document.getElementById('quickL3Toggle')?.addEventListener('click', () => {
      const currentState = cachedHardwareStatus?.layers?.layer_3?.state || 'OFF';
      sendHardwareCommand(3, currentState === 'ON' ? 'OFF' : 'ON');
    });

    // Quick Bench Link
    document.getElementById('quickOpenBench')?.addEventListener('click', () => {
      openHardwareLab('workbench', { mode: 'control' });
    });
  }
"""

# Insert functions before initHardwareLab
init_hw_target = "  function initHardwareLab() {"
assert init_hw_target in content, "init_hw_target not found in app.js"
content = content.replace(init_hw_target, hw_functions + "\n" + init_hw_target, 1)

# In initHardwareLab, call initHardwareControlWorkbenchHandlers
init_handlers_call = """    // Exploded View Button"""
init_handlers_replacement = """    initHardwareControlWorkbenchHandlers();
    fetchHardwareStatusAndUpdateUI();

    // Exploded View Button"""
assert init_handlers_call in content, "init_handlers_call target not found in app.js"
content = content.replace(init_handlers_call, init_handlers_replacement, 1)

# In tickMultiAnimalEcosystem, call applyHardwareStatus
ecosystem_target = """      multiAnimalPopulation = data.agents || [];"""
ecosystem_replacement = """      multiAnimalPopulation = data.agents || [];
      if (data.hardware_status) {
        applyHardwareStatus(data.hardware_status, data.layer_counts);
      }"""
assert ecosystem_target in content, "ecosystem_target not found in app.js"
content = content.replace(ecosystem_target, ecosystem_replacement, 1)

app_path.write_text(content, encoding="utf-8")
print("app.js successfully patched with Hardware Control Workbench!")

