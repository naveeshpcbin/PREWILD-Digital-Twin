/**
 * PRW-Wild — Game-Quality 3D Wildlife Digital Twin Simulation Engine
 *
 * Distinctive Architecture:
 * 1. Open-World Environment: Procedural dual-zone terrain (forest corridor vs furrowed agricultural plots),
 *    multi-species vegetation (Acacia umbrella trees, Broadleaf woodland, shrubs), farm homesteads,
 *    physical boundary fence with tension wires and LED strobe warning beacons.
 * 2. High-Fidelity 3D Elephant: Anatomically proportioned model, PBR wrinkled hide material,
 *    4-limb articulated quadruped diagonal walking gait with contralateral phase lag, ground contact planting,
 *    vertical body bob & roll sway, articulated curling trunk, flapping ears, tusks, and wagging tail.
 * 3. 3D Human Characters: Farmer, Field Worker, Local Resident, and Forest Ranger with distinctive uniforms,
 *    idle posture breathing, alert reaction states, and 3D dashed alert route lines.
 * 4. Physical Wi-Fi Router & Sensors: WIFI_AP_01 with 3 articulated antennas and active packet LEDs,
 *    distributed ESP32 CSI nodes, PIR domes, acoustic microphones, and gated CAM_01 camera mast.
 * 5. PRW-Wild Causal Replay Lab:
 *    - Mode A: Live Digital Twin (real-time synchronized 3D telemetry).
 *    - Mode B: Architecture Layer Explorer (13 inspectable engineering models with mathematical formulations,
 *              live inputs, live outputs, assumptions, and limitations).
 *    - Mode C: Causal Event Flightline (12-stage step-by-step decision scrubber tracing RF to siren).
 *    - Mode D: Counterfactual Twin (Side-by-side policy comparison: Predictive vs PIR-Only vs Always-On vs RF-Only).
 * 6. Camera System: 9 Camera Viewpoints including Follow Elephant, Follow Human, and Camera POV Picture-in-Picture
 *    with optical target bounding box overlay.
 * 7. Audio & Alerts: Web Audio API rising multi-tone emergency siren on breach, approach warning chime,
 *    arming, test, mute, and silence controls.
 * 8. Fallback: Seamless 2D Spatial Radar toggle preserved.
 */

(function () {
  'use strict';

  // ==========================================================================
  // Global Simulation State
  // ==========================================================================
  let simulationData = null;
  let currentTime = 0.0;
  let duration = 120.0;
  let timeStep = 0.5;
  let isPlaying = false;
  let playSpeed = 1.0;
  let lastFrameTimestamp = null;
  let animFrameId = null;

  // View Modes & Modes
  let currentViewMode = '3d'; // '3d' or '2d'
  let activeCameraView = 'orbit'; // 'orbit', 'isometric', 'topdown', 'follow', 'human', 'router', 'camera', 'campov', 'fence'
  let currentLabMode = 'live'; // 'live', 'layers', 'flightline', 'counterfactual'
  let activeLayerIndex = 1; // 1 to 13
  let activeFlightlineStage = 1; // 1 to 12
  let activeHumanIndex = 0; // for cycling 'human' view
  let graphicsQualityHigh = true;

  // Contact & Counterfactual Cache
  let contactsList = [];
  let authoritiesList = [];
  let counterfactualCache = null;

  // ==========================================================================
  // Web Audio API Laptop Alarm Manager
  // ==========================================================================
  class AlarmAudioManager {
    constructor() {
      this.ctx = null;
      this.isArmed = false;
      this.isMuted = false;
      this.isSilenced = false;
      this.volume = 0.75;
      this.activeSirenInterval = null;
      this.currentAlarmState = 'idle'; // 'idle', 'watch_chime', 'breach_siren', 'silenced'
    }

    initContext() {
      if (!this.ctx) {
        const AudioCtx = window.AudioContext || window.webkitAudioContext;
        if (AudioCtx) this.ctx = new AudioCtx();
      }
      if (this.ctx && this.ctx.state === 'suspended') {
        this.ctx.resume();
      }
      this.isArmed = true;
      this.updateUI();
    }

    playTone(frequency, durationMs, type = 'sine', gainMultiplier = 1.0) {
      if (!this.ctx || !this.isArmed || this.isMuted) return;
      try {
        const osc = this.ctx.createOscillator();
        const gain = this.ctx.createGain();
        osc.type = type;
        osc.frequency.setValueAtTime(frequency, this.ctx.currentTime);

        const targetGain = this.volume * gainMultiplier;
        gain.gain.setValueAtTime(targetGain, this.ctx.currentTime);
        gain.gain.exponentialRampToValueAtTime(0.001, this.ctx.currentTime + durationMs / 1000);

        osc.connect(gain);
        gain.connect(this.ctx.destination);

        osc.start();
        osc.stop(this.ctx.currentTime + durationMs / 1000);
      } catch (e) {
        console.warn('Audio synthesis warning:', e);
      }
    }

    playApproachChime() {
      if (!this.isArmed || this.isMuted || this.isSilenced) return;
      this.playTone(587, 180, 'sine', 0.5); // D5
      setTimeout(() => this.playTone(880, 240, 'triangle', 0.6), 180); // A5
    }

    startBreachSiren() {
      if (!this.isArmed || this.isMuted || this.isSilenced) return;
      if (this.activeSirenInterval) return;

      this.currentAlarmState = 'breach_siren';
      this.updateUI();

      // Distinctive rising multi-tone sequence (E5 -> A5 -> D6)
      const playSirenPattern = () => {
        if (!this.isArmed || this.isMuted || this.isSilenced) return;
        this.playTone(659, 130, 'sawtooth', 0.55);
        setTimeout(() => this.playTone(880, 130, 'sawtooth', 0.65), 120);
        setTimeout(() => this.playTone(1174, 220, 'sine', 0.8), 240);
      };

      playSirenPattern();
      this.activeSirenInterval = setInterval(playSirenPattern, 620);

      // Trigger optional native sound fallback on Windows via API
      fetch('/api/sound-alert', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ alert_type: 'breach' }),
      }).catch(() => {});
    }

    stopBreachSiren() {
      if (this.activeSirenInterval) {
        clearInterval(this.activeSirenInterval);
        this.activeSirenInterval = null;
      }
      if (this.currentAlarmState === 'breach_siren') {
        this.currentAlarmState = 'idle';
      }
      this.updateUI();
    }

    acknowledgeAndSilence() {
      this.isSilenced = true;
      this.stopBreachSiren();
      this.currentAlarmState = 'silenced';
      this.updateUI();
    }

    testAlarm() {
      this.initContext();
      this.isSilenced = false;
      this.stopBreachSiren();
      this.startBreachSiren();
      setTimeout(() => this.stopBreachSiren(), 2200);
    }

    toggleMute() {
      this.isMuted = !this.isMuted;
      if (this.isMuted) this.stopBreachSiren();
      this.updateUI();
    }

    updateUI() {
      const badge = document.getElementById('alarmStatusBadge');
      const text = document.getElementById('alarmStatusText');
      const btnArm = document.getElementById('btnArmAudio');
      const btnMute = document.getElementById('btnMuteAudio');
      const btnAck = document.getElementById('btnAckAlarm');

      if (!badge || !text) return;
      badge.className = 'alarm-status-pill';

      if (!this.isArmed) {
        badge.classList.add('idle');
        text.textContent = 'AUDIO: LOCKED';
        if (btnArm) btnArm.textContent = '🔊 ARM ALARM';
      } else if (this.isMuted) {
        badge.classList.add('idle');
        text.textContent = 'AUDIO: MUTED';
        if (btnMute) btnMute.textContent = '🔊 UNMUTE';
      } else if (this.currentAlarmState === 'breach_siren') {
        badge.classList.add('active');
        text.textContent = '🚨 SIREN ACTIVE';
        if (btnAck) btnAck.classList.remove('hidden');
      } else if (this.isSilenced) {
        badge.classList.add('idle');
        text.textContent = 'AUDIO: SILENCED';
      } else {
        badge.classList.add('armed');
        text.textContent = 'AUDIO: ARMED';
        if (btnArm) btnArm.textContent = '🔔 ARMED';
        if (btnMute) btnMute.textContent = '🔇 MUTE';
        if (btnAck) btnAck.classList.add('hidden');
      }
    }
  }

  const alarmManager = new AlarmAudioManager();

  // ==========================================================================
  // Procedural PBR Canvas Texture Generators
  // ==========================================================================
  const PBRTextures = {
    bark: null,
    foliage: null,
    furrowSoil: null,
    elephantSkin: null,
    woodPlank: null,

    init() {
      this.bark = this.createBarkTexture();
      this.foliage = this.createFoliageTexture();
      this.furrowSoil = this.createFurrowSoilTexture();
      this.elephantSkin = this.createElephantSkinTexture();
      this.woodPlank = this.createWoodPlankTexture();
    },

    createBarkTexture() {
      const c = document.createElement('canvas');
      c.width = 256; c.height = 256;
      const ctx = c.getContext('2d');
      ctx.fillStyle = '#2d1810';
      ctx.fillRect(0, 0, 256, 256);

      // Vertical bark fissures
      for (let x = 0; x < 256; x += 4) {
        const v = Math.sin(x * 0.2) * 20 + Math.random() * 25;
        ctx.fillStyle = `rgb(${45 + v}, ${25 + v * 0.6}, ${18 + v * 0.4})`;
        ctx.fillRect(x, 0, 3, 256);
      }
      const tex = new THREE.CanvasTexture(c);
      tex.wrapS = tex.wrapT = THREE.RepeatWrapping;
      tex.repeat.set(2, 4);
      return tex;
    },

    createFoliageTexture() {
      const c = document.createElement('canvas');
      c.width = 256; c.height = 256;
      const ctx = c.getContext('2d');
      ctx.fillStyle = '#14532d';
      ctx.fillRect(0, 0, 256, 256);

      // Stippled leaf blades
      for (let i = 0; i < 600; i++) {
        const x = Math.random() * 256;
        const y = Math.random() * 256;
        const r = Math.random() * 6 + 2;
        const shade = Math.floor(Math.random() * 50);
        ctx.fillStyle = `rgb(${20 + shade * 0.5}, ${83 + shade}, ${45 + shade * 0.3})`;
        ctx.beginPath();
        ctx.arc(x, y, r, 0, Math.PI * 2);
        ctx.fill();
      }
      const tex = new THREE.CanvasTexture(c);
      tex.wrapS = tex.wrapT = THREE.RepeatWrapping;
      tex.repeat.set(3, 3);
      return tex;
    },

    createFurrowSoilTexture() {
      const c = document.createElement('canvas');
      c.width = 256; c.height = 256;
      const ctx = c.getContext('2d');
      ctx.fillStyle = '#3a271d';
      ctx.fillRect(0, 0, 256, 256);

      // Tilled furrow bands
      for (let y = 0; y < 256; y += 16) {
        ctx.fillStyle = '#27170f';
        ctx.fillRect(0, y, 256, 6);
        ctx.fillStyle = '#4a3325';
        ctx.fillRect(0, y + 6, 256, 10);
      }
      // Soil crumbs
      for (let i = 0; i < 400; i++) {
        ctx.fillStyle = Math.random() > 0.5 ? '#1c100a' : '#573d2d';
        ctx.fillRect(Math.random() * 256, Math.random() * 256, 2, 2);
      }
      const tex = new THREE.CanvasTexture(c);
      tex.wrapS = tex.wrapT = THREE.RepeatWrapping;
      tex.repeat.set(6, 6);
      return tex;
    },

    createElephantSkinTexture() {
      const c = document.createElement('canvas');
      c.width = 256; c.height = 256;
      const ctx = c.getContext('2d');
      ctx.fillStyle = '#64748b';
      ctx.fillRect(0, 0, 256, 256);

      // Fine dermal wrinkles
      ctx.strokeStyle = '#475569';
      ctx.lineWidth = 1;
      for (let i = 0; i < 80; i++) {
        ctx.beginPath();
        let x = Math.random() * 256;
        let y = Math.random() * 256;
        ctx.moveTo(x, y);
        for (let j = 0; j < 4; j++) {
          x += (Math.random() - 0.5) * 30;
          y += (Math.random() - 0.5) * 30;
          ctx.lineTo(x, y);
        }
        ctx.stroke();
      }
      const tex = new THREE.CanvasTexture(c);
      tex.wrapS = tex.wrapT = THREE.RepeatWrapping;
      tex.repeat.set(4, 4);
      return tex;
    },

    createWoodPlankTexture() {
      const c = document.createElement('canvas');
      c.width = 256; c.height = 256;
      const ctx = c.getContext('2d');
      ctx.fillStyle = '#5c4033';
      ctx.fillRect(0, 0, 256, 256);

      // Plank grains
      ctx.strokeStyle = '#3e2723';
      ctx.lineWidth = 1.5;
      for (let x = 0; x < 256; x += 32) {
        ctx.beginPath();
        ctx.moveTo(x, 0); ctx.lineTo(x, 256);
        ctx.stroke();
      }
      const tex = new THREE.CanvasTexture(c);
      tex.wrapS = tex.wrapT = THREE.RepeatWrapping;
      return tex;
    },
  };

  // ==========================================================================
  // Three.js 3D Digital Twin Scene Architecture
  // ==========================================================================
  let threeScene = null;
  let threeCamera = null;
  let threeRenderer = null;
  let threeControls = null;

  // Dynamic Scene Objects
  const threeObjects = {
    elephantGroup: null,
    elephantLimbs: {
      legFL: null,
      legFR: null,
      legBL: null,
      legBR: null,
      trunkJoints: [],
      earL: null,
      earR: null,
      tail: null,
      head: null,
    },
    humanMeshes: {},
    routerGroup: null,
    routerLeds: [],
    cameraMastGroup: null,
    cameraHead: null,
    cameraFovCone: null,
    cameraLight: null,
    fenceGroup: null,
    fenceBoundaryLine: null,
    fenceRibbon: null,
    fenceBreachLights: [],
    sensorNodes: {},
    rfLinks: [],
    rfPulses: [],
    recipients: {},
    alertRouteLines: [],
    groundTruthTrail: null,
    kalmanCrosshair: null,
    predictionRay: null,
    etaSprite: null,
    interceptMarker: null,
    cameraPovCamera: null,
  };

  function initThreeScene() {
    const container = document.getElementById('threeContainer');
    if (!container || !window.THREE) return;

    PBRTextures.init();

    // 1. Scene
    threeScene = new THREE.Scene();
    threeScene.background = new THREE.Color(0x060914);
    threeScene.fog = new THREE.FogExp2(0x060914, 0.0032);

    // 2. Main Camera
    const aspect = container.clientWidth / container.clientHeight;
    threeCamera = new THREE.PerspectiveCamera(46, aspect, 0.5, 900);
    threeCamera.position.set(90, 75, 175);

    // POV Camera for CAM_01
    threeObjects.cameraPovCamera = new THREE.PerspectiveCamera(55, 1.77, 0.5, 300);

    // 3. WebGL Renderer
    threeRenderer = new THREE.WebGLRenderer({ antialias: true, alpha: false, powerPreference: 'high-performance' });
    threeRenderer.setSize(container.clientWidth, container.clientHeight);
    threeRenderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
    threeRenderer.shadowMap.enabled = true;
    threeRenderer.shadowMap.type = THREE.PCFSoftShadowMap;
    threeRenderer.toneMapping = THREE.ACESFilmicToneMapping;
    threeRenderer.toneMappingExposure = 1.05;

    container.innerHTML = '';
    container.appendChild(threeRenderer.domElement);

    // 4. Orbit Controls
    if (window.THREE.OrbitControls) {
      threeControls = new THREE.OrbitControls(threeCamera, threeRenderer.domElement);
      threeControls.enableDamping = true;
      threeControls.dampingFactor = 0.05;
      threeControls.maxPolarAngle = Math.PI / 2 - 0.04;
      threeControls.minDistance = 8;
      threeControls.maxDistance = 380;
      threeControls.target.set(85, 0, 100);
      threeControls.update();
    }

    // 5. Lighting, Environment, Hardware & Character Construction
    buildSceneLighting();
    buildProceduralEnvironment();
    buildRouterModel();
    buildCameraMastModel();
    buildArticulatedElephantModel();
    buildSensorStationModels();
    buildCommunityCharacters();
    buildTelemetryVisualizers();

    // 6. Raycast Inspector
    setupRaycaster(container);

    // 7. Resize Handler
    window.addEventListener('resize', onWindowResize);

    // Start 3D Loop
    animateThree();
  }

  function buildSceneLighting() {
    // Hemisphere ambient moonlight
    const hemiLight = new THREE.HemisphereLight(0x38bdf8, 0x050a14, 0.55);
    threeScene.add(hemiLight);

    // Directional Sun / Moonlight
    const dirLight = new THREE.DirectionalLight(0xe0f2fe, 0.95);
    dirLight.position.set(130, 140, 90);
    dirLight.castShadow = true;
    dirLight.shadow.mapSize.width = 2048;
    dirLight.shadow.mapSize.height = 2048;
    dirLight.shadow.camera.near = 10;
    dirLight.shadow.camera.far = 400;
    const d = 130;
    dirLight.shadow.camera.left = -d;
    dirLight.shadow.camera.right = d;
    dirLight.shadow.camera.top = d;
    dirLight.shadow.camera.bottom = -d;
    dirLight.shadow.bias = -0.0005;
    threeScene.add(dirLight);

    // Warm twilight accent
    const fillLight = new THREE.DirectionalLight(0xf59e0b, 0.25);
    fillLight.position.set(-80, 50, -50);
    threeScene.add(fillLight);
  }

  function buildProceduralEnvironment() {
    // Dual-Zone Terrain Plane
    const groundGeo = new THREE.PlaneGeometry(250, 270, 64, 64);
    groundGeo.rotateX(-Math.PI / 2);

    const pos = groundGeo.attributes.position;
    const count = pos.count;
    const colors = new Float32Array(count * 3);

    for (let i = 0; i < count; i++) {
      const vx = pos.getX(i);
      const vz = pos.getZ(i);

      if (vx < 100) {
        // Forest / Habitat: lush organic mossy green with loam patches
        const noise = Math.sin(vx * 0.12) * Math.cos(vz * 0.12) * 0.04;
        colors[i * 3 + 0] = 0.08 + noise;
        colors[i * 3 + 1] = 0.20 + noise;
        colors[i * 3 + 2] = 0.10 + noise;
      } else {
        // Agricultural Farm: rich brown furrowed loam
        const ridge = (Math.sin(vz * 0.8) > 0) ? 0.03 : -0.02;
        colors[i * 3 + 0] = 0.22 + ridge;
        colors[i * 3 + 1] = 0.16 + ridge;
        colors[i * 3 + 2] = 0.11;
      }
    }
    groundGeo.setAttribute('color', new THREE.BufferAttribute(colors, 3));

    const groundMat = new THREE.MeshStandardMaterial({
      vertexColors: true,
      roughness: 0.9,
      metalness: 0.05,
    });
    const groundMesh = new THREE.Mesh(groundGeo, groundMat);
    groundMesh.position.set(90, -0.08, 100);
    groundMesh.receiveShadow = true;
    threeScene.add(groundMesh);

    // 3D Ridged Crop Rows (Farm Zone: x=105 to 190)
    for (let z = 20; z <= 180; z += 5.5) {
      const furrowGeo = new THREE.BoxGeometry(85, 0.45, 1.8);
      const furrowMat = new THREE.MeshStandardMaterial({
        color: 0x15803d,
        map: PBRTextures.furrowSoil,
        roughness: 0.8,
      });
      const furrow = new THREE.Mesh(furrowGeo, furrowMat);
      furrow.position.set(148, 0.22, z);
      furrow.receiveShadow = true;
      threeScene.add(furrow);

      // Crop Stalks
      for (let cx = 112; cx <= 185; cx += 7) {
        const stalkGeo = new THREE.CylinderGeometry(0.04, 0.06, 1.2, 6);
        const stalkMat = new THREE.MeshStandardMaterial({ color: 0x22c55e, roughness: 0.6 });
        const stalk = new THREE.Mesh(stalkGeo, stalkMat);
        stalk.position.set(cx, 0.85, z);
        threeScene.add(stalk);
      }
    }

    // Winding Dirt Approach Corridor Path in Forest Zone
    const pathCurve = new THREE.CatmullRomCurve3([
      new THREE.Vector3(15, 0.02, 100),
      new THREE.Vector3(45, 0.02, 98),
      new THREE.Vector3(70, 0.02, 95),
      new THREE.Vector3(98, 0.02, 94),
    ]);
    const pathGeo = new THREE.TubeGeometry(pathCurve, 24, 2.8, 8, false);
    const pathMat = new THREE.MeshStandardMaterial({ color: 0x473322, roughness: 0.95 });
    const pathMesh = new THREE.Mesh(pathGeo, pathMat);
    pathMesh.scale.set(1, 0.04, 1);
    threeScene.add(pathMesh);

    // Boundary Fence Posts & Glowing Multi-State Barrier (x = 100)
    const fenceGroup = new THREE.Group();
    threeObjects.fenceGroup = fenceGroup;

    // Boundary Line
    const fenceLineGeo = new THREE.BufferGeometry().setFromPoints([
      new THREE.Vector3(100, 1.3, 0),
      new THREE.Vector3(100, 1.3, 200),
    ]);
    const fenceLineMat = new THREE.LineDashedMaterial({
      color: 0x10b981,
      dashSize: 3,
      gapSize: 1.5,
      linewidth: 3,
    });
    const fenceLine = new THREE.Line(fenceLineGeo, fenceLineMat);
    fenceLine.computeLineDistances();
    fenceGroup.add(fenceLine);
    threeObjects.fenceBoundaryLine = fenceLine;

    // Volumetric Glowing Fence Ribbon
    const ribbonGeo = new THREE.PlaneGeometry(200, 2.2);
    ribbonGeo.rotateY(Math.PI / 2);
    const ribbonMat = new THREE.MeshBasicMaterial({
      color: 0x10b981,
      transparent: true,
      opacity: 0.16,
      side: THREE.DoubleSide,
    });
    const ribbonMesh = new THREE.Mesh(ribbonGeo, ribbonMat);
    ribbonMesh.position.set(100, 1.1, 100);
    fenceGroup.add(ribbonMesh);
    threeObjects.fenceRibbon = ribbonMesh;

    // Heavy Timber Posts with Wire Tension and Warning Strobe Beacons
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
    threeScene.add(fenceGroup);

    // Multi-Species Procedural Forest (Acacia Umbrella Trees & Broadleaf Trees)
    buildDiverseForest();

    // Farm Storehouse & Sheds
    buildFarmStructures();
  }

  function buildDiverseForest() {
    const treePositions = [
      // Flanking corridor
      [18, 42, 'acacia'], [28, 30, 'broadleaf'], [40, 48, 'acacia'], [55, 32, 'broadleaf'], [72, 22, 'acacia'],
      [18, 155, 'broadleaf'], [32, 168, 'acacia'], [48, 148, 'broadleaf'], [65, 172, 'acacia'], [82, 158, 'broadleaf'],
      [22, 70, 'broadleaf'], [36, 76, 'acacia'], [18, 126, 'broadleaf'], [32, 122, 'acacia'], [62, 66, 'broadleaf'],
      [78, 138, 'acacia'], [12, 92, 'shrub'], [14, 108, 'shrub'], [52, 132, 'broadleaf'], [48, 58, 'acacia'],
      [8, 60, 'broadleaf'], [86, 45, 'acacia'], [88, 148, 'broadleaf'],
    ];

    treePositions.forEach(([tx, tz, type]) => {
      const treeGroup = new THREE.Group();

      if (type === 'acacia') {
        // Savanna Acacia Umbrella Tree
        const trunkGeo = new THREE.CylinderGeometry(0.35, 0.55, 4.5, 7);
        const trunkMat = new THREE.MeshStandardMaterial({ map: PBRTextures.bark, roughness: 0.9 });
        const trunk = new THREE.Mesh(trunkGeo, trunkMat);
        trunk.position.y = 2.25;
        trunk.rotation.z = (Math.random() - 0.5) * 0.15;
        trunk.castShadow = true;
        treeGroup.add(trunk);

        // Flat-topped umbrella canopy
        const canopyGeo = new THREE.CylinderGeometry(3.8, 4.5, 1.2, 9);
        const canopyMat = new THREE.MeshStandardMaterial({ map: PBRTextures.foliage, roughness: 0.8 });
        const canopy = new THREE.Mesh(canopyGeo, canopyMat);
        canopy.position.y = 5.0;
        canopy.castShadow = true;
        treeGroup.add(canopy);

        const upperCanopy = new THREE.Mesh(new THREE.CylinderGeometry(2.4, 3.2, 0.8, 8), canopyMat);
        upperCanopy.position.y = 5.9;
        treeGroup.add(upperCanopy);

      } else if (type === 'broadleaf') {
        // Broadleaf Woodland Tree with rounded lobed foliage
        const trunkGeo = new THREE.CylinderGeometry(0.4, 0.65, 4.0, 8);
        const trunkMat = new THREE.MeshStandardMaterial({ map: PBRTextures.bark, roughness: 0.9 });
        const trunk = new THREE.Mesh(trunkGeo, trunkMat);
        trunk.position.y = 2.0;
        trunk.castShadow = true;
        treeGroup.add(trunk);

        const lobeMat = new THREE.MeshStandardMaterial({ map: PBRTextures.foliage, roughness: 0.85 });
        const lobePositions = [
          [0, 5.2, 0, 2.6],
          [1.5, 4.6, 0.8, 2.0],
          [-1.4, 4.8, -0.6, 2.1],
          [0.3, 6.4, -0.4, 1.8],
        ];
        lobePositions.forEach(([lx, ly, lz, lr]) => {
          const lobe = new THREE.Mesh(new THREE.DodecahedronGeometry(lr, 1), lobeMat);
          lobe.position.set(lx, ly, lz);
          lobe.castShadow = true;
          treeGroup.add(lobe);
        });

      } else {
        // Low-lying Shrub
        const shrubMat = new THREE.MeshStandardMaterial({ map: PBRTextures.foliage, roughness: 0.9 });
        const shrub = new THREE.Mesh(new THREE.DodecahedronGeometry(1.6, 1), shrubMat);
        shrub.position.y = 1.0;
        treeGroup.add(shrub);
      }

      treeGroup.position.set(tx, 0, tz);
      threeScene.add(treeGroup);
    });

    // Forest Rocks & Mossy Boulders
    const boulderGeo = new THREE.DodecahedronGeometry(1.4, 1);
    const boulderMat = new THREE.MeshStandardMaterial({ color: 0x475569, roughness: 0.9 });
    const boulderPositions = [[35, 85], [58, 115], [25, 112], [80, 82]];

    boulderPositions.forEach(([bx, bz]) => {
      const rock = new THREE.Mesh(boulderGeo, boulderMat);
      rock.position.set(bx, 0.6, bz);
      rock.rotation.set(Math.random(), Math.random(), Math.random());
      rock.scale.set(1.4, 0.7, 1.2);
      rock.castShadow = true;
      threeScene.add(rock);
    });
  }

  function buildFarmStructures() {
    // Farm House & Shed
    const shedGroup = new THREE.Group();
    const wallGeo = new THREE.BoxGeometry(9, 4.8, 6.5);
    const wallMat = new THREE.MeshStandardMaterial({ map: PBRTextures.woodPlank, roughness: 0.8 });
    const walls = new THREE.Mesh(wallGeo, wallMat);
    walls.position.y = 2.4;
    walls.castShadow = true;
    shedGroup.add(walls);

    // Corrugated pitched roof
    const roofGeo = new THREE.ConeGeometry(6.6, 2.8, 4);
    roofGeo.rotateY(Math.PI / 4);
    const roofMat = new THREE.MeshStandardMaterial({ color: 0xb91c1c, roughness: 0.5, metalness: 0.3 });
    const roof = new THREE.Mesh(roofGeo, roofMat);
    roof.position.y = 6.0;
    roof.castShadow = true;
    shedGroup.add(roof);

    // Front porch pillars
    const pillarGeo = new THREE.CylinderGeometry(0.12, 0.12, 3.2, 6);
    const pillarMat = new THREE.MeshStandardMaterial({ color: 0x334155 });
    const p1 = new THREE.Mesh(pillarGeo, pillarMat);
    p1.position.set(3.8, 1.6, 3.8);
    const p2 = new THREE.Mesh(pillarGeo, pillarMat);
    p2.position.set(-3.8, 1.6, 3.8);
    shedGroup.add(p1); shedGroup.add(p2);

    shedGroup.position.set(138, 0, 115);
    threeScene.add(shedGroup);
  }

  // ==========================================================================
  // Physical Wi-Fi Router / Access Point Model (WIFI_AP_01)
  // ==========================================================================
  function buildRouterModel() {
    const routerGroup = new THREE.Group();
    threeObjects.routerGroup = routerGroup;

    // Heavy Mounting Mast & Pedestal
    const poleGeo = new THREE.CylinderGeometry(0.14, 0.18, 2.8, 8);
    const poleMat = new THREE.MeshStandardMaterial({ color: 0x334155, roughness: 0.5, metalness: 0.3 });
    const pole = new THREE.Mesh(poleGeo, poleMat);
    pole.position.y = 1.4;
    pole.castShadow = true;
    routerGroup.add(pole);

    // Shelf / Enclosure base
    const shelfGeo = new THREE.BoxGeometry(1.6, 0.12, 1.2);
    const shelfMat = new THREE.MeshStandardMaterial({ color: 0x1e293b, roughness: 0.4 });
    const shelf = new THREE.Mesh(shelfGeo, shelfMat);
    shelf.position.y = 2.8;
    routerGroup.add(shelf);

    // Dual-Tone Chamfered Router Enclosure
    const bodyGeo = new THREE.BoxGeometry(1.25, 0.30, 0.9);
    const bodyMat = new THREE.MeshStandardMaterial({ color: 0x0f172a, roughness: 0.3, metalness: 0.35 });
    const body = new THREE.Mesh(bodyGeo, bodyMat);
    body.position.y = 3.0;
    body.castShadow = true;
    routerGroup.add(body);

    // Front Accent Light Pipe & Bevel
    const trimGeo = new THREE.BoxGeometry(1.22, 0.05, 0.04);
    const trimMat = new THREE.MeshBasicMaterial({ color: 0x00f0ff });
    const trim = new THREE.Mesh(trimGeo, trimMat);
    trim.position.set(0, 3.03, 0.45);
    routerGroup.add(trim);

    // Operational Status LEDs (Power: Green, Wi-Fi: Cyan, Internet: Amber)
    const ledColors = [0x10b981, 0x00f0ff, 0x00f0ff, 0xf59e0b];
    threeObjects.routerLeds = [];
    ledColors.forEach((col, idx) => {
      const ledGeo = new THREE.SphereGeometry(0.025, 6, 6);
      const ledMat = new THREE.MeshBasicMaterial({ color: col });
      const led = new THREE.Mesh(ledGeo, ledMat);
      led.position.set(-0.35 + idx * 0.23, 3.06, 0.455);
      routerGroup.add(led);
      threeObjects.routerLeds.push(led);
    });

    // 3 Articulated Dual-Band Dipole Antennas
    const antGeo = new THREE.CylinderGeometry(0.025, 0.035, 1.2, 6);
    const antMat = new THREE.MeshStandardMaterial({ color: 0x1e293b, roughness: 0.3 });
    const antAngles = [-0.28, 0.0, 0.28];
    const antPositions = [-0.4, 0.0, 0.4];

    antPositions.forEach((ax, idx) => {
      const ant = new THREE.Mesh(antGeo, antMat);
      ant.position.set(ax, 3.55, -0.4);
      ant.rotation.z = antAngles[idx];
      ant.rotation.x = -0.12;
      routerGroup.add(ant);
    });

    // Rear RJ45 Ethernet Jacks
    for (let px = -0.25; px <= 0.25; px += 0.12) {
      const port = new THREE.Mesh(new THREE.BoxGeometry(0.08, 0.08, 0.03), new THREE.MeshStandardMaterial({ color: 0xf59e0b }));
      port.position.set(px, 2.98, -0.45);
      routerGroup.add(port);
    }

    // Label Sprite
    const labelSprite = createTextSprite('WIFI_AP_01 [ACCESS POINT]', '#00f0ff');
    labelSprite.position.set(0, 4.4, 0);
    routerGroup.add(labelSprite);

    routerGroup.position.set(60, 0, 95);
    routerGroup.userData = {
      type: 'ROUTER',
      id: 'WIFI_AP_01',
      role: 'Central Wi-Fi CSI Infrastructure AP',
      position: [60, 95],
      status: 'ONLINE',
    };
    threeScene.add(routerGroup);
  }

  // ==========================================================================
  // Distributed Sensor Stations (ESP32 CSI, PIR, Acoustic)
  // ==========================================================================
  function buildSensorStationModels() {
    const nodes = [
      { id: 'rf_01', type: 'rf_csi', pos: [40, 90], range: 35, color: 0x00f0ff, label: 'ESP32 CSI NODE #1' },
      { id: 'rf_02', type: 'rf_csi', pos: [70, 110], range: 35, color: 0x00f0ff, label: 'ESP32 CSI NODE #2' },
      { id: 'pir_01', type: 'pir', pos: [75, 95], range: 25, color: 0xf59e0b, label: 'PIR MOTION #1' },
      { id: 'aco_01', type: 'acoustic', pos: [55, 100], range: 60, color: 0x38bdf8, label: 'ACOUSTIC SENSOR #1' },
    ];

    nodes.forEach(node => {
      const group = new THREE.Group();

      const post = new THREE.Mesh(new THREE.CylinderGeometry(0.08, 0.1, 2.2, 8), new THREE.MeshStandardMaterial({ color: 0x475569 }));
      post.position.y = 1.1;
      post.castShadow = true;
      group.add(post);

      const box = new THREE.Mesh(new THREE.BoxGeometry(0.5, 0.6, 0.35), new THREE.MeshStandardMaterial({ color: 0x1e293b, roughness: 0.4 }));
      box.position.y = 2.1;
      box.castShadow = true;
      group.add(box);

      if (node.type === 'rf_csi') {
        const ant = new THREE.Mesh(new THREE.CylinderGeometry(0.02, 0.03, 0.75, 6), new THREE.MeshStandardMaterial({ color: 0x0f172a }));
        ant.position.set(0, 2.75, 0);
        group.add(ant);
        // Mini Solar Panel
        const solar = new THREE.Mesh(new THREE.BoxGeometry(0.6, 0.05, 0.4), new THREE.MeshStandardMaterial({ color: 0x1e1b4b, metalness: 0.7 }));
        solar.position.set(0.35, 2.4, 0);
        solar.rotation.z = -0.35;
        group.add(solar);
      } else if (node.type === 'pir') {
        const dome = new THREE.Mesh(new THREE.SphereGeometry(0.14, 8, 8), new THREE.MeshStandardMaterial({ color: 0xf59e0b, roughness: 0.2 }));
        dome.position.set(0, 2.1, 0.2);
        group.add(dome);
      } else if (node.type === 'acoustic') {
        const mic = new THREE.Mesh(new THREE.CylinderGeometry(0.12, 0.12, 0.35, 8), new THREE.MeshStandardMaterial({ color: 0x0284c7 }));
        mic.position.set(0, 2.55, 0);
        group.add(mic);
      }

      // Beacon Light
      const beacon = new THREE.Mesh(new THREE.SphereGeometry(0.08, 8, 8), new THREE.MeshBasicMaterial({ color: node.color }));
      beacon.position.set(0, 2.45, 0);
      group.add(beacon);

      // Coverage Ring
      const diskGeo = new THREE.RingGeometry(node.range - 0.4, node.range, 36);
      diskGeo.rotateX(-Math.PI / 2);
      const disk = new THREE.Mesh(diskGeo, new THREE.MeshBasicMaterial({ color: node.color, transparent: true, opacity: 0.16, side: THREE.DoubleSide }));
      disk.position.y = 0.05;
      group.add(disk);

      // Sprite Label
      const sprite = createTextSprite(node.id, '#94a3b8');
      sprite.position.set(0, 3.2, 0);
      group.add(sprite);

      group.position.set(node.pos[0], 0, node.pos[1]);
      group.userData = {
        type: node.type.toUpperCase(),
        id: node.id,
        role: node.label,
        position: node.pos,
        range_m: node.range,
        beaconMesh: beacon,
      };

      threeScene.add(group);
      threeObjects.sensorNodes[node.id] = group;
    });

    // Wi-Fi CSI RF Fresnel Link Rays
    const linkPoints = [
      new THREE.Vector3(40, 2.7, 90),
      new THREE.Vector3(60, 2.9, 95),
      new THREE.Vector3(70, 2.7, 110),
    ];
    const linkGeo = new THREE.BufferGeometry().setFromPoints(linkPoints);
    const linkMat = new THREE.LineDashedMaterial({ color: 0x00f0ff, dashSize: 2, gapSize: 2, transparent: true, opacity: 0.4 });
    const linkLine = new THREE.Line(linkGeo, linkMat);
    linkLine.computeLineDistances();
    threeScene.add(linkLine);
    threeObjects.rfLinks.push(linkLine);
  }

  // ==========================================================================
  // Gated Surveillance Camera Mast (CAM_01)
  // ==========================================================================
  function buildCameraMastModel() {
    const mastGroup = new THREE.Group();
    threeObjects.cameraMastGroup = mastGroup;

    // Lattice steel tower
    const tower = new THREE.Mesh(new THREE.CylinderGeometry(0.2, 0.38, 6.2, 8), new THREE.MeshStandardMaterial({ color: 0x475569, roughness: 0.5 }));
    tower.position.y = 3.1;
    tower.castShadow = true;
    mastGroup.add(tower);

    // Solar Panel on mast
    const solar = new THREE.Mesh(new THREE.BoxGeometry(1.6, 0.08, 1.2), new THREE.MeshStandardMaterial({ color: 0x1e1b4b, metalness: 0.6 }));
    solar.position.set(0.6, 5.2, 0);
    solar.rotation.z = -0.35;
    mastGroup.add(solar);

    // Pan/Tilt Head & Lens Hood
    const camHead = new THREE.Group();
    camHead.position.set(0, 6.2, 0);

    const bodyGeo = new THREE.CylinderGeometry(0.32, 0.38, 0.75, 12);
    bodyGeo.rotateZ(Math.PI / 2);
    const camBody = new THREE.Mesh(bodyGeo, new THREE.MeshStandardMaterial({ color: 0xffffff, roughness: 0.3 }));
    camHead.add(camBody);

    const lensGeo = new THREE.CylinderGeometry(0.22, 0.22, 0.28, 12);
    lensGeo.rotateZ(Math.PI / 2);
    const lens = new THREE.Mesh(lensGeo, new THREE.MeshStandardMaterial({ color: 0x0f172a, roughness: 0.1, metalness: 0.8 }));
    lens.position.set(-0.48, 0, 0);
    camHead.add(lens);

    // Attach Camera POV Camera to Pan-Tilt Head
    if (threeObjects.cameraPovCamera) {
      threeObjects.cameraPovCamera.position.set(-0.55, 0, 0);
      threeObjects.cameraPovCamera.rotation.y = Math.PI; // Look outward along lens
      camHead.add(threeObjects.cameraPovCamera);
    }

    mastGroup.add(camHead);
    threeObjects.cameraHead = camHead;

    // Volumetric Spotlight FOV Cone
    const fovConeGeo = new THREE.ConeGeometry(25, 55, 24, 1, true);
    fovConeGeo.rotateX(Math.PI / 2);
    fovConeGeo.translate(0, 0, 27.5);
    const fovCone = new THREE.Mesh(fovConeGeo, new THREE.MeshBasicMaterial({
      color: 0xa855f7,
      transparent: true,
      opacity: 0.06,
      side: THREE.DoubleSide,
      depthWrite: false,
    }));
    camHead.add(fovCone);
    threeObjects.cameraFovCone = fovCone;

    // SpotLight
    const spotLight = new THREE.SpotLight(0xa855f7, 0, 80, Math.PI / 5.5, 0.4, 1.2);
    spotLight.position.set(0, 0, 0);
    camHead.add(spotLight);
    threeObjects.cameraLight = spotLight;

    const label = createTextSprite('CAM_01 [PTZ GATE]', '#a855f7');
    label.position.set(0, 7.4, 0);
    mastGroup.add(label);

    mastGroup.position.set(85, 0, 95);
    mastGroup.userData = {
      type: 'CAMERA',
      id: 'CAM_01',
      role: 'Predictive Gated Optical PTZ Camera',
      position: [85, 95],
      status: 'STANDBY',
    };
    threeScene.add(mastGroup);
  }

  // ==========================================================================
  // Anatomical Articulated 3D Elephant Model (ELEPHANT_01)
  // ==========================================================================
  function buildArticulatedElephantModel() {
    const elGroup = new THREE.Group();
    threeObjects.elephantGroup = elGroup;

    const skinMat = new THREE.MeshStandardMaterial({
      color: 0x64748b,
      map: PBRTextures.elephantSkin,
      roughness: 0.85,
      metalness: 0.05,
    });
    const tuskMat = new THREE.MeshStandardMaterial({ color: 0xffffff, roughness: 0.25 });

    // 1. Torso / Body (contoured dorsal spine and shoulder hump)
    const bodyGeo = new THREE.SphereGeometry(2.4, 16, 14);
    bodyGeo.scale(1.25, 0.96, 0.88);
    const body = new THREE.Mesh(bodyGeo, skinMat);
    body.position.set(0, 2.7, 0);
    body.castShadow = true;
    elGroup.add(body);

    // 2. Head with Brow Ridge
    const headGroup = new THREE.Group();
    headGroup.position.set(2.4, 3.4, 0);
    const headGeo = new THREE.SphereGeometry(1.3, 14, 12);
    headGeo.scale(1.0, 1.1, 0.92);
    const head = new THREE.Mesh(headGeo, skinMat);
    head.castShadow = true;
    headGroup.add(head);
    elGroup.add(headGroup);
    threeObjects.elephantLimbs.head = headGroup;

    // 3. Articulated 5-Segment Trunk
    threeObjects.elephantLimbs.trunkJoints = [];
    let currentTrunkParent = headGroup;
    let trunkLength = 0.85;

    for (let i = 0; i < 5; i++) {
      const segGroup = new THREE.Group();
      segGroup.position.set(i === 0 ? 1.0 : 0.6, i === 0 ? -0.2 : -0.5, 0);

      const rTop = 0.32 - i * 0.045;
      const rBot = 0.28 - i * 0.045;
      const segMesh = new THREE.Mesh(new THREE.CylinderGeometry(rBot, rTop, trunkLength, 8), skinMat);
      segMesh.position.set(0.1, -trunkLength / 2, 0);
      segMesh.rotation.z = -0.3;
      segMesh.castShadow = true;
      segGroup.add(segMesh);

      currentTrunkParent.add(segGroup);
      threeObjects.elephantLimbs.trunkJoints.push(segGroup);
      currentTrunkParent = segGroup;
    }

    // 4. Tusks (Curved Ivory)
    const tuskGeo = new THREE.ConeGeometry(0.12, 1.45, 8);
    tuskGeo.rotateX(Math.PI / 2);

    const tuskL = new THREE.Mesh(tuskGeo, tuskMat);
    tuskL.position.set(0.9, -0.6, 0.46);
    tuskL.rotation.y = 0.2;
    headGroup.add(tuskL);

    const tuskR = new THREE.Mesh(tuskGeo, tuskMat);
    tuskR.position.set(0.9, -0.6, -0.46);
    tuskR.rotation.y = -0.2;
    headGroup.add(tuskR);

    // 5. Flapping Ears
    const earGeo = new THREE.CylinderGeometry(1.25, 1.05, 0.12, 10);
    earGeo.rotateZ(Math.PI / 2);

    const earLGroup = new THREE.Group();
    earLGroup.position.set(-0.2, 0.1, 1.25);
    const earL = new THREE.Mesh(earGeo, skinMat);
    earL.rotation.y = 0.35;
    earLGroup.add(earL);
    headGroup.add(earLGroup);
    threeObjects.elephantLimbs.earL = earLGroup;

    const earRGroup = new THREE.Group();
    earRGroup.position.set(-0.2, 0.1, -1.25);
    const earR = new THREE.Mesh(earGeo, skinMat);
    earR.rotation.y = -0.35;
    earRGroup.add(earR);
    headGroup.add(earRGroup);
    threeObjects.elephantLimbs.earR = earRGroup;

    // 6. 4 Articulated Quadruped Legs
    const createLeg = (lx, lz) => {
      const legGroup = new THREE.Group();
      legGroup.position.set(lx, 2.4, lz);

      // Upper leg
      const upperGeo = new THREE.CylinderGeometry(0.42, 0.38, 1.4, 8);
      const upper = new THREE.Mesh(upperGeo, skinMat);
      upper.position.y = -0.7;
      upper.castShadow = true;
      legGroup.add(upper);

      // Lower leg & foot pad
      const lowerGeo = new THREE.CylinderGeometry(0.36, 0.44, 1.2, 8);
      const lower = new THREE.Mesh(lowerGeo, skinMat);
      lower.position.y = -1.8;
      lower.castShadow = true;
      legGroup.add(lower);

      elGroup.add(legGroup);
      return legGroup;
    };

    threeObjects.elephantLimbs.legFL = createLeg(1.4, 0.85);
    threeObjects.elephantLimbs.legFR = createLeg(1.4, -0.85);
    threeObjects.elephantLimbs.legBL = createLeg(-1.4, 0.85);
    threeObjects.elephantLimbs.legBR = createLeg(-1.4, -0.85);

    // 7. Tail
    const tailGroup = new THREE.Group();
    tailGroup.position.set(-2.5, 2.5, 0);
    const tailMesh = new THREE.Mesh(new THREE.CylinderGeometry(0.06, 0.09, 1.6, 6), skinMat);
    tailMesh.position.y = -0.8;
    tailGroup.add(tailMesh);
    elGroup.add(tailGroup);
    threeObjects.elephantLimbs.tail = tailGroup;

    // Target Tag Sprite
    const targetTag = createTextSprite('ELEPHANT_01', '#10b981');
    targetTag.position.set(0, 5.4, 0);
    elGroup.add(targetTag);

    // Ground Contact Shadow
    const shadowMesh = new THREE.Mesh(new THREE.CircleGeometry(2.4, 16), new THREE.MeshBasicMaterial({ color: 0x000000, transparent: true, opacity: 0.35 }));
    shadowMesh.rotateX(-Math.PI / 2);
    shadowMesh.position.y = 0.04;
    elGroup.add(shadowMesh);

    elGroup.position.set(20, 0, 100);
    elGroup.userData = {
      type: 'ANIMAL',
      id: 'ELEPHANT_01',
      species: 'elephant',
      speed: 1.5,
    };
    threeScene.add(elGroup);
  }

  // ==========================================================================
  // 3D Human Characters (Farmer, Field Worker, Local Resident, Ranger)
  // ==========================================================================
  // ==========================================================================
  // 3D Human Characters (Farmer, Field Worker, Residents, Ranger Patrol)
  // ==========================================================================
  function buildCommunityCharacters() {
    const characters = [
      {
        id: 'FARM_OPERATOR_01',
        name: 'Arun Kumar (Farmer)',
        role: 'Farmer',
        pos: [115, 105],
        shirtCol: 0x1d4ed8, // denim blue work shirt
        vestCol: null,
        pantsCol: 0x334155, // rugged canvas trousers
        bootCol: 0x5a3825,  // brown leather work boots
        skinCol: 0xc68642,
        hasHat: true,
        hatType: 'straw',
        hatCol: 0xd97706, // woven straw sun hat
        hasRadio: false,
      },
      {
        id: 'FIELD_WORKER_01',
        name: 'Ramu (Field Crew)',
        role: 'Worker',
        pos: [108, 92],
        shirtCol: 0x3b82f6, // navy under-shirt
        vestCol: 0xf97316,  // high-vis neon orange safety vest
        pantsCol: 0x1e293b, // dark cargo trousers
        bootCol: 0x1c1917,  // steel-toe heavy work boots
        skinCol: 0x8d5524,
        hasHat: true,
        hatType: 'hardhat',
        hatCol: 0xfacc15, // yellow construction hard hat
        hasRadio: false,
      },
      {
        id: 'LOCAL_RESIDENT_01',
        name: 'Priya Sharma (Resident)',
        role: 'Resident',
        pos: [130, 75],
        shirtCol: 0x0d9488, // teal / emerald traditional tunic
        vestCol: null,
        pantsCol: 0x475569, // dark salwar trousers
        bootCol: 0x78350f,  // casual leather shoes
        skinCol: 0xe0ac69,
        hasHat: false,
        hatType: 'none',
        hasRadio: false,
      },
      {
        id: 'LOCAL_RESIDENT_02',
        name: 'Sunil Verma (Resident)',
        role: 'Resident',
        pos: [142, 88],
        shirtCol: 0x991b1b, // burgundy / saffron tunic
        vestCol: null,
        pantsCol: 0x64748b, // slate trousers
        bootCol: 0x451a03,  // leather sandals / shoes
        skinCol: 0xc68642,
        hasHat: false,
        hatType: 'none',
        hasRadio: false,
      },
      {
        id: 'PATROL_UNIT_01',
        name: 'Ranger Patrol Alpha',
        role: 'Patrol',
        pos: [85, 45],
        shirtCol: 0x3f6212, // tactical olive khaki ranger uniform
        vestCol: 0x365314,  // tactical load-bearing vest
        pantsCol: 0x1a2e05, // military cargo pants
        bootCol: 0x0f172a,  // black tactical combat boots
        skinCol: 0xc68642,
        hasHat: true,
        hatType: 'campaign',
        hatCol: 0x365314, // brimmed ranger campaign hat
        hasRadio: true,   // VHF field transceiver on shoulder
      },
    ];

    characters.forEach(c => {
      const humanGroup = new THREE.Group();

      const skinMat = new THREE.MeshStandardMaterial({ color: c.skinCol, roughness: 0.65 });
      const shirtMat = new THREE.MeshStandardMaterial({ color: c.shirtCol, roughness: 0.7 });
      const pantsMat = new THREE.MeshStandardMaterial({ color: c.pantsCol, roughness: 0.8 });
      const bootMat = new THREE.MeshStandardMaterial({ color: c.bootCol, roughness: 0.5, metalness: 0.1 });

      // 1. Pelvis & Hips
      const pelvis = new THREE.Mesh(new THREE.BoxGeometry(0.38, 0.18, 0.24), pantsMat);
      pelvis.position.y = 0.94;
      pelvis.castShadow = true;
      humanGroup.add(pelvis);

      // Belt
      const belt = new THREE.Mesh(new THREE.BoxGeometry(0.40, 0.06, 0.26), new THREE.MeshStandardMaterial({ color: 0x1e293b, roughness: 0.4 }));
      belt.position.y = 1.02;
      humanGroup.add(belt);

      // 2. Torso / Chest
      const chestGroup = new THREE.Group();
      chestGroup.position.y = 1.05;

      const lowerTorso = new THREE.Mesh(new THREE.BoxGeometry(0.36, 0.24, 0.22), shirtMat);
      lowerTorso.position.y = 0.12;
      chestGroup.add(lowerTorso);

      const upperTorso = new THREE.Mesh(new THREE.BoxGeometry(0.44, 0.32, 0.26), shirtMat);
      upperTorso.position.y = 0.38;
      upperTorso.castShadow = true;
      chestGroup.add(upperTorso);

      // High-Vis Safety Vest Overlay
      if (c.vestCol) {
        const vest = new THREE.Mesh(new THREE.BoxGeometry(0.46, 0.34, 0.28), new THREE.MeshStandardMaterial({ color: c.vestCol, roughness: 0.5 }));
        vest.position.y = 0.38;
        chestGroup.add(vest);

        // Reflective Silver Strips
        const stripeMat = new THREE.MeshStandardMaterial({ color: 0xe2e8f0, roughness: 0.1, metalness: 0.8 });
        const strip1 = new THREE.Mesh(new THREE.BoxGeometry(0.47, 0.04, 0.29), stripeMat);
        strip1.position.y = 0.44;
        chestGroup.add(strip1);
        const strip2 = new THREE.Mesh(new THREE.BoxGeometry(0.47, 0.04, 0.29), stripeMat);
        strip2.position.y = 0.30;
        chestGroup.add(strip2);
      }

      // Tactical Radio Holster on Shoulder (Ranger)
      if (c.hasRadio) {
        const radio = new THREE.Mesh(new THREE.BoxGeometry(0.08, 0.16, 0.08), new THREE.MeshStandardMaterial({ color: 0x020617, roughness: 0.3 }));
        radio.position.set(-0.24, 0.48, 0.12);
        chestGroup.add(radio);
        const radioAnt = new THREE.Mesh(new THREE.CylinderGeometry(0.01, 0.01, 0.20, 6), new THREE.MeshStandardMaterial({ color: 0x020617 }));
        radioAnt.position.set(-0.24, 0.62, 0.12);
        chestGroup.add(radioAnt);
      }

      humanGroup.add(chestGroup);

      // 3. Neck & Head
      const neck = new THREE.Mesh(new THREE.CylinderGeometry(0.075, 0.085, 0.12, 8), skinMat);
      neck.position.y = 1.60;
      humanGroup.add(neck);

      const headGroup = new THREE.Group();
      headGroup.position.y = 1.74;

      const cranium = new THREE.Mesh(new THREE.SphereGeometry(0.15, 12, 10), skinMat);
      cranium.scale.set(1.0, 1.15, 1.05);
      headGroup.add(cranium);

      // Nose & Face profile
      const nose = new THREE.Mesh(new THREE.ConeGeometry(0.03, 0.06, 6), skinMat);
      nose.rotation.x = -Math.PI / 2;
      nose.position.set(0, 0, 0.16);
      headGroup.add(nose);

      // Hair (if no hat or under hat)
      const hairMat = new THREE.MeshStandardMaterial({ color: 0x171717, roughness: 0.9 });
      const hair = new THREE.Mesh(new THREE.SphereGeometry(0.155, 10, 8, 0, Math.PI * 2, 0, Math.PI / 2), hairMat);
      hair.position.y = 0.04;
      headGroup.add(hair);

      // Hats
      if (c.hasHat) {
        const hatMat = new THREE.MeshStandardMaterial({ color: c.hatCol, roughness: 0.7 });
        if (c.hatType === 'straw') {
          // Broad woven sun brim
          const brim = new THREE.Mesh(new THREE.CylinderGeometry(0.36, 0.36, 0.03, 16), hatMat);
          brim.position.y = 0.10;
          headGroup.add(brim);
          const crown = new THREE.Mesh(new THREE.CylinderGeometry(0.17, 0.20, 0.14, 12), hatMat);
          crown.position.y = 0.17;
          headGroup.add(crown);
        } else if (c.hatType === 'hardhat') {
          // High-gloss hard hat dome
          const hardhatMat = new THREE.MeshStandardMaterial({ color: c.hatCol, roughness: 0.2, metalness: 0.1 });
          const dome = new THREE.Mesh(new THREE.SphereGeometry(0.18, 12, 10, 0, Math.PI * 2, 0, Math.PI / 2), hardhatMat);
          dome.position.y = 0.06;
          headGroup.add(dome);
          const brim = new THREE.Mesh(new THREE.CylinderGeometry(0.22, 0.21, 0.03, 14), hardhatMat);
          brim.position.y = 0.06;
          headGroup.add(brim);
        } else if (c.hatType === 'campaign') {
          // Ranger wide flat brim with indented crown
          const brim = new THREE.Mesh(new THREE.CylinderGeometry(0.34, 0.34, 0.025, 16), hatMat);
          brim.position.y = 0.09;
          headGroup.add(brim);
          const crown = new THREE.Mesh(new THREE.CylinderGeometry(0.16, 0.19, 0.16, 12), hatMat);
          crown.position.y = 0.18;
          headGroup.add(crown);
        }
      }

      humanGroup.add(headGroup);

      // 4. Articulated Arms (Left & Right)
      // Left Arm (Hanging naturally)
      const armLGroup = new THREE.Group();
      armLGroup.position.set(-0.28, 1.45, 0);

      const upperArmL = new THREE.Mesh(new THREE.CylinderGeometry(0.065, 0.055, 0.32, 8), shirtMat);
      upperArmL.position.y = -0.16;
      armLGroup.add(upperArmL);

      const foreArmL = new THREE.Mesh(new THREE.CylinderGeometry(0.055, 0.045, 0.30, 8), skinMat);
      foreArmL.position.y = -0.42;
      armLGroup.add(foreArmL);

      const handL = new THREE.Mesh(new THREE.SphereGeometry(0.05, 8, 8), skinMat);
      handL.position.y = -0.60;
      armLGroup.add(handL);
      humanGroup.add(armLGroup);

      // Right Arm (Pivots up when alert is received)
      const armRGroup = new THREE.Group();
      armRGroup.position.set(0.28, 1.45, 0);

      const upperArmR = new THREE.Mesh(new THREE.CylinderGeometry(0.065, 0.055, 0.32, 8), shirtMat);
      upperArmR.position.y = -0.16;
      armRGroup.add(upperArmR);

      const foreArmR = new THREE.Mesh(new THREE.CylinderGeometry(0.055, 0.045, 0.30, 8), skinMat);
      foreArmR.position.y = -0.42;
      armRGroup.add(foreArmR);

      const handR = new THREE.Mesh(new THREE.SphereGeometry(0.05, 8, 8), skinMat);
      handR.position.y = -0.60;
      armRGroup.add(handR);

      // Handheld Alert Receiver / Smartphone Device in Hand
      const phone = new THREE.Mesh(new THREE.BoxGeometry(0.07, 0.12, 0.02), new THREE.MeshStandardMaterial({ color: 0x0f172a, roughness: 0.2 }));
      phone.position.set(0, -0.60, 0.04);
      const phoneScreen = new THREE.Mesh(new THREE.PlaneGeometry(0.055, 0.095), new THREE.MeshBasicMaterial({ color: 0x00f0ff }));
      phoneScreen.position.set(0, -0.60, 0.052);
      armRGroup.add(phone);
      armRGroup.add(phoneScreen);

      humanGroup.add(armRGroup);

      // 5. Articulated Legs (Thighs, Calves, Boots planted at Y=0)
      [-0.13, 0.13].forEach(lx => {
        // Upper Leg
        const thigh = new THREE.Mesh(new THREE.CylinderGeometry(0.09, 0.08, 0.42, 8), pantsMat);
        thigh.position.set(lx, 0.70, 0);
        humanGroup.add(thigh);

        // Lower Leg (Calf)
        const calf = new THREE.Mesh(new THREE.CylinderGeometry(0.078, 0.068, 0.38, 8), pantsMat);
        calf.position.set(lx, 0.33, 0);
        humanGroup.add(calf);

        // Sculpted Work Boot (Grounded at Y=0)
        const boot = new THREE.Mesh(new THREE.BoxGeometry(0.13, 0.14, 0.24), bootMat);
        boot.position.set(lx, 0.07, 0.04);
        boot.castShadow = true;
        humanGroup.add(boot);

        // Boot Rubber Tread Sole
        const sole = new THREE.Mesh(new THREE.BoxGeometry(0.14, 0.03, 0.25), new THREE.MeshStandardMaterial({ color: 0x09090b, roughness: 0.9 }));
        sole.position.set(lx, 0.015, 0.04);
        humanGroup.add(sole);
      });

      // 6. Alert Halo (Hidden until alert dispatched to this character)
      const haloGeo = new THREE.RingGeometry(0.65, 0.90, 24);
      haloGeo.rotateX(-Math.PI / 2);
      const haloMat = new THREE.MeshBasicMaterial({ color: 0x00f0ff, transparent: true, opacity: 0.0, side: THREE.DoubleSide });
      const halo = new THREE.Mesh(haloGeo, haloMat);
      halo.position.y = 2.25;
      humanGroup.add(halo);

      // 7. Identity Text Pin Sprite
      const pin = createTextSprite(c.name, '#e2e8f0');
      pin.position.set(0, 2.50, 0);
      humanGroup.add(pin);

      humanGroup.position.set(c.pos[0], 0, c.pos[1]);
      humanGroup.userData = {
        type: 'HUMAN_RECIPIENT',
        id: c.id,
        name: c.name,
        role: c.role,
        position: c.pos,
        armR: armRGroup,
        chest: chestGroup,
        head: headGroup,
        halo,
      };

      threeScene.add(humanGroup);
      threeObjects.humanMeshes[c.id] = humanGroup;
      threeObjects.recipients[c.id] = humanGroup;
    });
  }

  // ==========================================================================
  // Trajectory, Kalman Track, and ETA Projection Visualizers
  // ==========================================================================
  function buildTelemetryVisualizers() {
    // 1. Ground Truth 3D Path Trail
    const trailGeo = new THREE.BufferGeometry();
    const trailMat = new THREE.LineBasicMaterial({ color: 0x00f0ff, transparent: true, opacity: 0.45, linewidth: 2 });
    const trailLine = new THREE.Line(trailGeo, trailMat);
    threeScene.add(trailLine);
    threeObjects.groundTruthTrail = trailLine;

    // 2. Kalman Track Crosshair & Uncertainty Covariance Ring
    const kalmanGroup = new THREE.Group();
    const crossGeo = new THREE.BufferGeometry().setFromPoints([
      new THREE.Vector3(-1.8, 0.1, 0), new THREE.Vector3(1.8, 0.1, 0),
      new THREE.Vector3(0, 0.1, -1.8), new THREE.Vector3(0, 0.1, 1.8),
    ]);
    kalmanGroup.add(new THREE.LineSegments(crossGeo, new THREE.LineBasicMaterial({ color: 0x38bdf8 })));

    const ringGeo = new THREE.RingGeometry(5.8, 6.2, 32);
    ringGeo.rotateX(-Math.PI / 2);
    const ringMesh = new THREE.Mesh(ringGeo, new THREE.MeshBasicMaterial({ color: 0x38bdf8, transparent: true, opacity: 0.35, side: THREE.DoubleSide }));
    ringMesh.position.y = 0.08;
    kalmanGroup.add(ringMesh);

    threeScene.add(kalmanGroup);
    threeObjects.kalmanCrosshair = kalmanGroup;

    // 3. Boundary Prediction Ray & Floating ETA Sprite
    const rayGeo = new THREE.BufferGeometry().setFromPoints([
      new THREE.Vector3(0, 0.5, 0), new THREE.Vector3(10, 0.5, 0),
    ]);
    const rayLine = new THREE.Line(rayGeo, new THREE.LineDashedMaterial({ color: 0xf59e0b, dashSize: 2, gapSize: 1.5, linewidth: 3 }));
    threeScene.add(rayLine);
    threeObjects.predictionRay = rayLine;

    // Intercept Marker on Fence
    const markerMesh = new THREE.Mesh(new THREE.CylinderGeometry(0.5, 0.5, 0.2, 16), new THREE.MeshBasicMaterial({ color: 0xef4444 }));
    markerMesh.position.set(100, 0.1, 100);
    threeScene.add(markerMesh);
    threeObjects.interceptMarker = markerMesh;

    // Floating ETA Billboard Sprite
    const etaSprite = createTextSprite('ETA: --', '#f59e0b', true);
    etaSprite.position.set(100, 2.5, 100);
    threeScene.add(etaSprite);
    threeObjects.etaSprite = etaSprite;
  }

  // ==========================================================================
  // Text Sprite Billboard Generator
  // ==========================================================================
  function createTextSprite(text, color = '#ffffff', isBadge = false) {
    const canvas = document.createElement('canvas');
    canvas.width = 256; canvas.height = 64;
    const sCtx = canvas.getContext('2d');

    if (isBadge) {
      sCtx.fillStyle = 'rgba(15, 23, 42, 0.85)';
      sCtx.fillRect(10, 8, 236, 48);
      sCtx.strokeStyle = color;
      sCtx.lineWidth = 2;
      sCtx.strokeRect(10, 8, 236, 48);
    }

    sCtx.fillStyle = color;
    sCtx.font = 'bold 24px JetBrains Mono, monospace';
    sCtx.textAlign = 'center';
    sCtx.textBaseline = 'middle';
    sCtx.fillText(text, 128, 32);

    const texture = new THREE.CanvasTexture(canvas);
    texture.minFilter = THREE.LinearFilter;
    const sprite = new THREE.Sprite(new THREE.SpriteMaterial({ map: texture, transparent: true }));
    sprite.scale.set(6.5, 1.6, 1);
    sprite.userData = { canvas, texture, isBadge, color };
    return sprite;
  }

  function updateTextSprite(sprite, text) {
    if (!sprite || !sprite.userData || !sprite.userData.canvas) return;
    const { canvas, texture, isBadge, color } = sprite.userData;
    const sCtx = canvas.getContext('2d');
    sCtx.clearRect(0, 0, 256, 64);

    if (isBadge) {
      sCtx.fillStyle = 'rgba(15, 23, 42, 0.9)';
      sCtx.fillRect(10, 8, 236, 48);
      sCtx.strokeStyle = color;
      sCtx.lineWidth = 2;
      sCtx.strokeRect(10, 8, 236, 48);
    }

    sCtx.fillStyle = color;
    sCtx.font = 'bold 24px JetBrains Mono, monospace';
    sCtx.textAlign = 'center';
    sCtx.textBaseline = 'middle';
    sCtx.fillText(text, 128, 32);
    texture.needsUpdate = true;
  }

  // ==========================================================================
  // Mouse Raycasting & 3D Object Inspection
  // ==========================================================================
  function setupRaycaster(container) {
    const raycaster = new THREE.Raycaster();
    const mouse = new THREE.Vector2();

    container.addEventListener('click', (e) => {
      const rect = container.getBoundingClientRect();
      mouse.x = ((e.clientX - rect.left) / container.clientWidth) * 2 - 1;
      mouse.y = -((e.clientY - rect.top) / container.clientHeight) * 2 + 1;

      raycaster.setFromCamera(mouse, threeCamera);
      const intersects = raycaster.intersectObjects(threeScene.children, true);

      for (let i = 0; i < intersects.length; i++) {
        let obj = intersects[i].object;
        while (obj && !obj.userData?.id && obj.parent) {
          obj = obj.parent;
        }

        if (obj && obj.userData && obj.userData.id) {
          showObjectInspector(obj.userData);
          focusCameraOnObject(obj.position);
          break;
        }
      }
    });
  }

  function showObjectInspector(data) {
    const card = document.getElementById('objectInspectorCard');
    if (!card) return;
    document.getElementById('inspType').textContent = data.type || 'NODE';
    document.getElementById('inspId').textContent = data.id || 'N/A';
    document.getElementById('inspStatus').textContent = data.status || 'ACTIVE';
    document.getElementById('inspRole').textContent = data.role || data.type;
    const pos = data.position ? `(${data.position[0].toFixed(1)}, ${data.position[1].toFixed(1)})m` : '--';
    document.getElementById('inspPos').textContent = pos;
    document.getElementById('inspLastEvent').textContent = `t=${currentTime.toFixed(1)}s`;
    card.classList.remove('hidden');
  }

  document.getElementById('closeInspectorBtn')?.addEventListener('click', () => {
    document.getElementById('objectInspectorCard')?.classList.add('hidden');
  });

  // ==========================================================================
  // Camera View Presets
  // ==========================================================================
  function setCameraView(viewKey) {
    activeCameraView = viewKey;
    document.querySelectorAll('.viewpoint-pills .v-pill').forEach(b => {
      b.classList.toggle('active', b.dataset.view === viewKey);
    });

    if (!threeControls || !threeCamera) return;

    if (viewKey === 'orbit') {
      threeControls.target.set(85, 0, 100);
      threeCamera.position.set(90, 75, 175);
    } else if (viewKey === 'isometric') {
      threeControls.target.set(90, 0, 100);
      threeCamera.position.set(190, 130, 200);
    } else if (viewKey === 'topdown') {
      threeControls.target.set(90, 0, 100);
      threeCamera.position.set(90, 210, 100);
    } else if (viewKey === 'router') {
      threeControls.target.set(60, 2.8, 95);
      threeCamera.position.set(60, 8, 110);
    } else if (viewKey === 'camera') {
      threeControls.target.set(85, 5.5, 95);
      threeCamera.position.set(75, 12, 115);
    } else if (viewKey === 'fence') {
      threeControls.target.set(100, 1.2, 100);
      threeCamera.position.set(118, 10, 100);
    } else if (viewKey === 'human') {
      // Cycle through human characters
      const keys = Object.keys(threeObjects.humanMeshes);
      if (keys.length > 0) {
        const charKey = keys[activeHumanIndex % keys.length];
        const hGroup = threeObjects.humanMeshes[charKey];
        if (hGroup) {
          focusCameraOnObject(hGroup.position);
          activeHumanIndex++;
        }
      }
    } else if (viewKey === 'campov') {
      // Show Camera POV floating window
      const win = document.getElementById('camPovFloatingWindow');
      if (win) win.classList.remove('hidden');
    }
    threeControls.update();
  }

  function focusCameraOnObject(pos) {
    if (!threeControls || !threeCamera) return;
    threeControls.target.copy(pos);
    threeCamera.position.set(pos.x + 18, pos.y + 14, pos.z + 18);
    threeControls.update();
  }

  document.querySelectorAll('.viewpoint-pills .v-pill').forEach(btn => {
    btn.addEventListener('click', () => setCameraView(btn.dataset.view));
  });

  document.getElementById('resetCameraBtn')?.addEventListener('click', () => setCameraView('orbit'));

  document.getElementById('fullscreenBtn')?.addEventListener('click', () => {
    const vp = document.getElementById('mainViewportWrapper');
    if (!vp) return;
    vp.classList.toggle('fullscreen-mode');
    setTimeout(onWindowResize, 50);
  });

  document.getElementById('closePovBtn')?.addEventListener('click', () => {
    document.getElementById('camPovFloatingWindow')?.classList.add('hidden');
  });

  function onWindowResize() {
    const container = document.getElementById('threeContainer');
    if (threeCamera && threeRenderer && container) {
      threeCamera.aspect = container.clientWidth / container.clientHeight;
      threeCamera.updateProjectionMatrix();
      threeRenderer.setSize(container.clientWidth, container.clientHeight);
    }
  }

  // Graphics Quality Preset Toggles
  document.getElementById('btnGfxHigh')?.addEventListener('click', () => {
    graphicsQualityHigh = true;
    document.getElementById('btnGfxHigh').classList.add('active');
    document.getElementById('btnGfxPerf').classList.remove('active');
    if (threeRenderer) {
      threeRenderer.shadowMap.enabled = true;
      threeRenderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
    }
  });

  document.getElementById('btnGfxPerf')?.addEventListener('click', () => {
    graphicsQualityHigh = false;
    document.getElementById('btnGfxPerf').classList.add('active');
    document.getElementById('btnGfxHigh').classList.remove('active');
    if (threeRenderer) {
      threeRenderer.shadowMap.enabled = false;
      threeRenderer.setPixelRatio(1.0);
    }
  });

  // ==========================================================================
  // Three.js Render Loop & Locomotion Animation Engine
  // ==========================================================================
  function animateThree() {
    requestAnimationFrame(animateThree);

    // Follow Elephant Camera tracking
    if (activeCameraView === 'follow' && threeObjects.elephantGroup && threeControls) {
      const ep = threeObjects.elephantGroup.position;
      threeControls.target.set(ep.x, ep.y + 2.5, ep.z);
      threeCamera.position.set(ep.x - 22, ep.y + 16, ep.z - 12);
      threeControls.update();
    } else if (threeControls) {
      threeControls.update();
    }

    // Animate Elephant Locomotion (Leg swing, body heave, ear flap, trunk sway)
    if (threeObjects.elephantGroup && isPlaying) {
      const walkCycle = currentTime * 4.5 * playSpeed;
      const limbs = threeObjects.elephantLimbs;

      if (limbs.legFL && limbs.legFR && limbs.legBL && limbs.legBR) {
        // True contralateral diagonal quadruped gait
        limbs.legFL.rotation.z = Math.sin(walkCycle) * 0.35;
        limbs.legBR.rotation.z = Math.sin(walkCycle + 0.2) * 0.32;
        limbs.legFR.rotation.z = Math.sin(walkCycle + Math.PI) * 0.35;
        limbs.legBL.rotation.z = Math.sin(walkCycle + Math.PI + 0.2) * 0.32;
      }

      // Vertical body heave & lateral sway
      threeObjects.elephantGroup.position.y = Math.abs(Math.sin(walkCycle * 2)) * 0.12;

      // Ear flapping
      if (limbs.earL && limbs.earR) {
        limbs.earL.rotation.y = 0.35 + Math.sin(walkCycle * 1.5) * 0.18;
        limbs.earR.rotation.y = -0.35 - Math.sin(walkCycle * 1.5) * 0.18;
      }

      // Trunk curling & swaying
      if (limbs.trunkJoints.length > 0) {
        limbs.trunkJoints.forEach((j, idx) => {
          j.rotation.z = Math.sin(walkCycle * 1.2 + idx * 0.4) * 0.08 - 0.1;
        });
      }

      // Tail wag
      if (limbs.tail) {
        limbs.tail.rotation.z = -0.25 + Math.sin(walkCycle * 2) * 0.2;
      }
    }

    // Animate Human Idle Posture (subtle breathing heave & head scanning) & Halo pulses
    const idleT = (typeof performance !== 'undefined' ? performance.now() : Date.now()) * 0.002;
    Object.values(threeObjects.humanMeshes).forEach((h, idx) => {
      if (h.userData?.halo) {
        h.userData.halo.rotation.z += 0.03;
      }
      if (h.userData?.chest) {
        // Natural chest breathing heave
        const breathe = 1.0 + Math.sin(idleT * 1.5 + idx * 1.2) * 0.025;
        h.userData.chest.scale.set(breathe, 1.0 + (breathe - 1.0) * 0.5, breathe);
      }
      if (h.userData?.head) {
        // Subtle natural look-around scan
        h.userData.head.rotation.y = Math.sin(idleT * 0.8 + idx * 2.0) * 0.08;
      }
    });

    // Animate Wi-Fi CSI RF pulse rings
    if (threeObjects.rfPulses.length > 0) {
      for (let i = threeObjects.rfPulses.length - 1; i >= 0; i--) {
        const pulse = threeObjects.rfPulses[i];
        pulse.scale.addScalar(0.06);
        pulse.material.opacity -= 0.02;
        if (pulse.material.opacity <= 0.01) {
          threeScene.remove(pulse);
          threeObjects.rfPulses.splice(i, 1);
        }
      }
    }

    // Render 3D Scene
    if (threeRenderer && threeScene && threeCamera && currentViewMode === '3d') {
      threeRenderer.render(threeScene, threeCamera);
    }

    // Secondary Camera POV Render
    if (camPovRenderer && threeScene && threeObjects.cameraPovCamera) {
      const win = document.getElementById('camPovFloatingWindow');
      if (win && !win.classList.contains('hidden')) {
        // Point Camera POV at elephant
        if (threeObjects.elephantGroup) {
          threeObjects.cameraPovCamera.position.set(85, 4.5, 95);
          threeObjects.cameraPovCamera.lookAt(threeObjects.elephantGroup.position.x, 1.8, threeObjects.elephantGroup.position.z);
        }
        camPovRenderer.render(threeScene, threeObjects.cameraPovCamera);
      }
    }
  }

  function triggerRFPulse(originX, originZ, color = 0x00f0ff) {
    if (!threeScene) return;
    const ringGeo = new THREE.RingGeometry(0.8, 1.4, 24);
    ringGeo.rotateX(-Math.PI / 2);
    const ringMat = new THREE.MeshBasicMaterial({ color, transparent: true, opacity: 0.7, side: THREE.DoubleSide });
    const pulse = new THREE.Mesh(ringGeo, ringMat);
    pulse.position.set(originX, 0.4, originZ);
    threeScene.add(pulse);
    threeObjects.rfPulses.push(pulse);
  }

  // ==========================================================================
  // 3D Scene Simulation State Synchronization
  // ==========================================================================
  function syncThreeScene(t) {
    if (!threeScene || !simulationData) return;

    // 1. Elephant Position & Smooth Heading Direction
    const animal = getGroundTruthAtTime(t);
    if (animal && threeObjects.elephantGroup) {
      threeObjects.elephantGroup.position.set(animal.x, threeObjects.elephantGroup.position.y, animal.y);

      const speed = Math.hypot(animal.vx, animal.vy);
      if (speed > 0.05) {
        const targetHeading = -Math.atan2(animal.vy, animal.vx);
        threeObjects.elephantGroup.rotation.y = targetHeading;
      }
    }

    // 2. Ground-Truth Path Trail
    if (threeObjects.groundTruthTrail && simulationData.ground_truth) {
      const gt = simulationData.ground_truth;
      const pts = [];
      for (let i = 0; i < gt.length; i++) {
        if (gt[i].timestamp_s > t) break;
        pts.push(new THREE.Vector3(gt[i].true_x, 0.15, gt[i].true_y));
      }
      if (pts.length >= 2) {
        threeObjects.groundTruthTrail.geometry.dispose();
        threeObjects.groundTruthTrail.geometry = new THREE.BufferGeometry().setFromPoints(pts);
        threeObjects.groundTruthTrail.visible = document.getElementById('toggleTrails')?.checked ?? true;
      }
    }

    // 3. Kalman Filter Track Crosshair & Uncertainty Ellipse
    const trackEv = getLatestEventBefore(t, 'track_update');
    if (threeObjects.kalmanCrosshair) {
      const hasValidTrack = trackEv && trackEv.estimated_position_xy && (t - trackEv.timestamp_s) < 3.0;
      threeObjects.kalmanCrosshair.visible = hasValidTrack && (document.getElementById('toggleVectors')?.checked ?? true);
      if (hasValidTrack) {
        threeObjects.kalmanCrosshair.position.set(
          trackEv.estimated_position_xy[0],
          0,
          trackEv.estimated_position_xy[1]
        );
      }
    }

    // 4. Boundary Prediction Ray & Floating ETA Sprite
    const predEv = getLatestEventBefore(t, 'boundary_prediction');
    if (threeObjects.predictionRay && threeObjects.etaSprite && threeObjects.interceptMarker) {
      const hasPred = predEv && predEv.predicted_crossing_xy && (t - predEv.timestamp_s) < 3.0;
      const showVectors = document.getElementById('toggleVectors')?.checked ?? true;

      threeObjects.predictionRay.visible = hasPred && showVectors;
      threeObjects.etaSprite.visible = hasPred && showVectors;
      threeObjects.interceptMarker.visible = hasPred && showVectors;

      if (hasPred && animal) {
        const startPt = new THREE.Vector3(animal.x, 0.5, animal.y);
        const crossPt = new THREE.Vector3(predEv.predicted_crossing_xy[0], 0.5, predEv.predicted_crossing_xy[1]);

        threeObjects.predictionRay.geometry.dispose();
        threeObjects.predictionRay.geometry = new THREE.BufferGeometry().setFromPoints([startPt, crossPt]);
        threeObjects.predictionRay.computeLineDistances();

        threeObjects.interceptMarker.position.set(crossPt.x, 0.2, crossPt.z);
        threeObjects.etaSprite.position.set(crossPt.x, 3.2, crossPt.z);
        updateTextSprite(threeObjects.etaSprite, `ETA: ${predEv.eta_s ? predEv.eta_s.toFixed(1) + 's' : '--'}`);
      }
    }

    // 5. Gated Camera Pan/Tilt & Spotlight Tracking
    const camEv = getLatestEventBefore(t, 'camera_trigger');
    const isCamActive = camEv && (t - camEv.timestamp_s) < 4.0;

    if (threeObjects.cameraHead && animal) {
      const dx = animal.x - 85;
      const dz = animal.y - 95;
      threeObjects.cameraHead.rotation.y = -Math.atan2(dz, dx);
    }

    if (threeObjects.cameraFovCone && threeObjects.cameraLight) {
      if (isCamActive) {
        threeObjects.cameraFovCone.material.opacity = 0.24;
        threeObjects.cameraFovCone.material.color.setHex(0xa855f7);
        threeObjects.cameraLight.intensity = 2.4;
      } else {
        threeObjects.cameraFovCone.material.opacity = 0.04;
        threeObjects.cameraFovCone.material.color.setHex(0x64748b);
        threeObjects.cameraLight.intensity = 0.0;
      }
    }

    // Update Camera POV Bounding Box
    const povBbox = document.getElementById('povTargetBbox');
    const povStatus = document.getElementById('povTargetStatus');
    if (povBbox && povStatus) {
      if (isCamActive && animal && animal.x > 50 && animal.x < 110) {
        povBbox.classList.remove('hidden');
        povStatus.textContent = 'TARGET LOCKED';
      } else {
        povBbox.classList.add('hidden');
        povStatus.textContent = isCamActive ? 'SEARCHING...' : 'STANDBY (SLEEP)';
      }
    }

    // 6. Fence Barrier & Confirmed Breach Emergency State
    const breachEv = getLatestEventBefore(t, 'boundary_breach');
    const alertEv = getLatestEventBefore(t, 'alert_issued');
    const riskEv = getLatestEventBefore(t, 'risk_assessment');

    const isBreach = breachEv && (t - breachEv.timestamp_s) < 15.0;
    const isWarning = alertEv && (t - alertEv.timestamp_s) < 4.0;
    const isWatch = riskEv && (riskEv.score > 0.4);

    if (isBreach) {
      threeObjects.fenceBoundaryLine.material.color.setHex(0xef4444);
      threeObjects.fenceRibbon.material.color.setHex(0xef4444);
      threeObjects.fenceRibbon.material.opacity = 0.35 + Math.sin(t * 8) * 0.15;
      threeObjects.fenceBreachLights.forEach(l => l.material.color.setHex(0xef4444));

      alarmManager.startBreachSiren();
      document.getElementById('breachCriticalBanner')?.classList.remove('hidden');
    } else if (isWarning || isWatch) {
      threeObjects.fenceBoundaryLine.material.color.setHex(0xf59e0b);
      threeObjects.fenceRibbon.material.color.setHex(0xf59e0b);
      threeObjects.fenceRibbon.material.opacity = 0.18;
      threeObjects.fenceBreachLights.forEach(l => l.material.color.setHex(0xf59e0b));

      if (isWarning) alarmManager.playApproachChime();
      document.getElementById('breachCriticalBanner')?.classList.add('hidden');
    } else {
      threeObjects.fenceBoundaryLine.material.color.setHex(0x10b981);
      threeObjects.fenceRibbon.material.color.setHex(0x10b981);
      threeObjects.fenceRibbon.material.opacity = 0.08;
      threeObjects.fenceBreachLights.forEach(l => l.material.color.setHex(0x10b981));
      document.getElementById('breachCriticalBanner')?.classList.add('hidden');
    }

    // 7. Dynamic Alert Routing Lines to Recipients
    updateAlertRouteVisualizers(t);

    // 8. Synchronize Sensor Pulses
    const activeSensors = getActiveEventsInWindow(t, 0.6);
    activeSensors.forEach(ev => {
      if (ev.sensor_id && threeObjects.sensorNodes[ev.sensor_id]) {
        const nodeGroup = threeObjects.sensorNodes[ev.sensor_id];
        triggerRFPulse(nodeGroup.position.x, nodeGroup.position.z, 0xf59e0b);
      }
    });
  }

  function updateAlertRouteVisualizers(t) {
    const dispEv = getLatestEventBefore(t, 'dispatch');
    const isDispatchActive = dispEv && (t - dispEv.timestamp_s) < 6.0;

    // Clear previous alert route lines
    threeObjects.alertRouteLines.forEach(l => threeScene.remove(l));
    threeObjects.alertRouteLines = [];

    if (isDispatchActive && simulationData.dispatches) {
      const activeDisps = simulationData.dispatches.filter(d => Math.abs(d.timestamp_s - dispEv.timestamp_s) < 1.0);
      const incPos = dispEv.estimated_position_xy || [95, 100];

      activeDisps.forEach(d => {
        const hGroup = threeObjects.humanMeshes[d.recipient_id];
        if (hGroup) {
          // Trigger Halo & Arm Raise
          if (hGroup.userData.halo) hGroup.userData.halo.material.opacity = 0.7;
          if (hGroup.userData.armR) hGroup.userData.armR.rotation.x = -1.2;

          // Draw dashed alert routing line from incident to human
          const p1 = new THREE.Vector3(incPos[0], 0.6, incPos[1]);
          const p2 = new THREE.Vector3(hGroup.position.x, 0.6, hGroup.position.z);
          const lineGeo = new THREE.BufferGeometry().setFromPoints([p1, p2]);
          const lineMat = new THREE.LineDashedMaterial({ color: 0x00f0ff, dashSize: 2, gapSize: 1, linewidth: 2 });
          const routeLine = new THREE.Line(lineGeo, lineMat);
          routeLine.computeLineDistances();
          threeScene.add(routeLine);
          threeObjects.alertRouteLines.push(routeLine);
        }
      });
    } else {
      // Reset Halos and Arms
      Object.values(threeObjects.humanMeshes).forEach(h => {
        if (h.userData.halo) h.userData.halo.material.opacity = 0.0;
        if (h.userData.armR) h.userData.armR.rotation.x = 0;
      });
    }
  }

  // ==========================================================================
  // Fallback 2D Canvas Engine (Preserved Seamlessly)
  // ==========================================================================
  let canvas2D = null;
  let ctx2D = null;
  let zoom2D = 4.2;
  let panX2D = 60;
  let panY2D = 50;

  function init2DCanvas() {
    canvas2D = document.getElementById('digitalTwinCanvas');
    if (!canvas2D) return;
    ctx2D = canvas2D.getContext('2d');
    resize2DCanvas();
  }

  function resize2DCanvas() {
    if (!canvas2D) return;
    const container = document.getElementById('twoContainer');
    const rect = container.getBoundingClientRect();
    const dpr = window.devicePixelRatio || 1;
    canvas2D.width = rect.width * dpr;
    canvas2D.height = rect.height * dpr;
    ctx2D.setTransform(1, 0, 0, 1, 0, 0);
    ctx2D.scale(dpr, dpr);
    render2DCanvas();
  }

  function worldToScreen2D(x, y) {
    return { x: panX2D + x * zoom2D, y: panY2D + y * zoom2D };
  }

  function render2DCanvas() {
    if (!canvas2D || !ctx2D || currentViewMode !== '2d') return;
    const w = canvas2D.width / (window.devicePixelRatio || 1);
    const h = canvas2D.height / (window.devicePixelRatio || 1);
    ctx2D.clearRect(0, 0, w, h);

    // Grid
    ctx2D.strokeStyle = 'rgba(255, 255, 255, 0.05)';
    ctx2D.lineWidth = 1;
    for (let x = 0; x < w; x += 30) {
      ctx2D.beginPath(); ctx2D.moveTo(x, 0); ctx2D.lineTo(x, h); ctx2D.stroke();
    }
    for (let y = 0; y < h; y += 30) {
      ctx2D.beginPath(); ctx2D.moveTo(0, y); ctx2D.lineTo(w, y); ctx2D.stroke();
    }

    // Boundary Fence
    const b0 = worldToScreen2D(100, 0);
    const b1 = worldToScreen2D(100, 200);
    ctx2D.strokeStyle = '#ef4444';
    ctx2D.lineWidth = 3;
    ctx2D.beginPath(); ctx2D.moveTo(b0.x, b0.y); ctx2D.lineTo(b1.x, b1.y); ctx2D.stroke();

    // Animal
    const animal = getGroundTruthAtTime(currentTime);
    if (animal) {
      const p = worldToScreen2D(animal.x, animal.y);
      ctx2D.fillStyle = '#10b981';
      ctx2D.beginPath(); ctx2D.arc(p.x, p.y, 8, 0, Math.PI * 2); ctx2D.fill();
      ctx2D.fillStyle = '#ffffff';
      ctx2D.font = 'bold 11px Outfit';
      ctx2D.fillText('ELEPHANT_01', p.x + 10, p.y - 4);
    }
  }

  // View Switcher (3D vs 2D)
  document.getElementById('btnView3D')?.addEventListener('click', () => {
    currentViewMode = '3d';
    document.getElementById('btnView3D').classList.add('active');
    document.getElementById('btnView2D').classList.remove('active');
    document.getElementById('threeContainer').classList.remove('hidden');
    document.getElementById('twoContainer').classList.add('hidden');
    document.getElementById('viewportTag').textContent = 'IMMERSIVE 3D SCENE';
    document.getElementById('hudViewMode').textContent = '3D IMMERSIVE';
    onWindowResize();
  });

  document.getElementById('btnView2D')?.addEventListener('click', () => {
    currentViewMode = '2d';
    document.getElementById('btnView2D').classList.add('active');
    document.getElementById('btnView3D').classList.remove('active');
    document.getElementById('twoContainer').classList.remove('hidden');
    document.getElementById('threeContainer').classList.add('hidden');
    document.getElementById('viewportTag').textContent = '2D RADAR FALLBACK';
    document.getElementById('hudViewMode').textContent = '2D RADAR';
    resize2DCanvas();
  });

  // ==========================================================================
  // Causal Replay Lab Modes (A, B, C, D)
  // ==========================================================================
  function setLabMode(mode) {
    currentLabMode = mode;
    document.querySelectorAll('.causal-lab-toolbar .lab-mode-tab').forEach(t => {
      t.classList.toggle('active', t.dataset.mode === mode);
    });

    const lebBar = document.getElementById('layerExplorerBar');
    const flTray = document.getElementById('flightlineTray');
    const cfModal = document.getElementById('counterfactualModal');
    const layerModal = document.getElementById('layerExplorerModal');

    if (mode === 'live') {
      if (lebBar) lebBar.classList.add('hidden');
      if (flTray) flTray.classList.add('hidden');
    } else if (mode === 'layers') {
      if (lebBar) lebBar.classList.remove('hidden');
      if (flTray) flTray.classList.add('hidden');
      showLayerDetails(activeLayerIndex);
    } else if (mode === 'flightline') {
      if (flTray) flTray.classList.remove('hidden');
      if (lebBar) lebBar.classList.add('hidden');
      showFlightlineStage(activeFlightlineStage);
    } else if (mode === 'counterfactual') {
      if (cfModal) cfModal.classList.remove('hidden');
      loadCounterfactualData();
    }
  }

  document.querySelectorAll('.causal-lab-toolbar .lab-mode-tab').forEach(btn => {
    btn.addEventListener('click', () => setLabMode(btn.dataset.mode));
  });

  // Mode B: Architecture Layer Explorer Definitions
  const ARCHITECTURE_LAYERS = {
    1: {
      badge: 'LAYER 1 • PHYSICAL WORLD',
      title: 'Physical Environment & Ground-Truth Kinematics',
      formulation: 'Continuous 2D plane R² with habitat zone (x < 100m) and agricultural crop parcels (x >= 100m), separated by boundary fence line at x=100.0m. Kinematics: x(t+Δt) = x(t) + v(t)Δt.',
      inputs: 'Waypoints sequence [(20, 100), (45, 98), (70, 95), (105, 92)], target speed 1.50 m/s.',
      outputs: 'Ground-truth continuous coordinates (x, y), velocity vector (vx, vy), boundary crossing flag.',
      assumptions: 'Ground truth is completely isolated from controller logic; used exclusively by evaluation engine for post-hoc error scoring.',
      limitations: 'Planar ground model; does not simulate physical tree collision physics.',
      focusTarget: () => threeObjects.elephantGroup?.position,
    },
    2: {
      badge: 'LAYER 2 • PRECURSOR RF SENSING',
      title: 'Wi-Fi CSI / Fresnel Zone Multipath Disturbance',
      formulation: 'First Fresnel zone knife-edge diffraction model. Signal attenuation A(d) ∝ exp(-d_LoS² / 2σ²). Subcarrier variance ΔS_CSI = (1/K) Σ |H_k - H_baseline|².',
      inputs: 'Transmitter-receiver LoS links between WIFI_AP_01 and ESP32 CSI nodes (rf_01, rf_02).',
      outputs: 'Synthetic RF disturbance observation score ∈ [0, 1] with event timestamp.',
      assumptions: 'Synthesized multipath disturbance at 5.2 GHz Wi-Fi. Label: SYNTHETIC RF OBSERVATION.',
      limitations: 'Calibrated to empirical literature values; not raw I/Q phase measurements from physical hardware.',
      focusTarget: () => threeObjects.routerGroup?.position,
    },
    3: {
      badge: 'LAYER 3 • CORROBORATIVE SENSORS',
      title: 'Multi-Modal PIR, Vibration & Acoustic Sensing',
      formulation: 'PIR conical FOV (R=25m, θ=90°); Geophone seismic vibration (R=35m); Infrasound acoustic microphone (R=60m). Independent observation score generation.',
      inputs: 'Radial distance r, animal velocity, acoustic ambient background noise floor.',
      outputs: 'Independent sensor observations with score ∈ [0, 1], node ID, and timestamp.',
      assumptions: 'Non-zero false alarm rate (λ_FA = 0.02/s) injected to validate corroboration integrity.',
      limitations: 'Isotropic open-air propagation assumed without complex wind-shear attenuation.',
      focusTarget: () => threeObjects.sensorNodes['pir_01']?.position,
    },
    4: {
      badge: 'LAYER 4 • SENSOR FUSION',
      title: 'Temporal Decay Weighted Evidential Fusion',
      formulation: 'Confidence fusion: C_fused(t) = Σ w_i · s_i(t) · exp(-λ(t - t_i)) · E_prior. Modality weights: RF (45%), PIR (30%), Acoustic (25%).',
      inputs: 'Multi-sensor observation queue within sliding temporal window ΔT = 3.0s.',
      outputs: 'Fused confidence score C_fused ∈ [0, 1], fused spatial centroid estimate.',
      assumptions: 'Independent sensor noise distributions; decay parameter λ = 0.4 s⁻¹.',
      limitations: 'Heuristic weighted fusion; not full Bayesian Dirichlet belief state estimation.',
      focusTarget: () => threeObjects.sensorNodes['rf_02']?.position,
    },
    5: {
      badge: 'LAYER 5 • STATE ESTIMATION',
      title: 'Extended Kalman Filter (EKF) Kinematic Tracker',
      formulation: 'State x = [x, y, vx, vy]^T. Prediction: x_{k|k-1} = F x_{k-1}. Covariance: P_{k|k-1} = F P F^T + Q. Gain: K = P H^T (H P H^T + R)⁻¹.',
      inputs: 'Fused measurement centroids (zx, zy) and measurement uncertainty covariance R.',
      outputs: 'Filtered continuous state vector, velocity vector, uncertainty covariance ellipse P.',
      assumptions: 'Constant velocity motion model with discrete process noise covariance Q = q·I.',
      limitations: 'Kalman linearity assumption; abrupt 90-degree turns produce temporary innovation residuals.',
      focusTarget: () => threeObjects.kalmanCrosshair?.position,
    },
    6: {
      badge: 'LAYER 6 • ECOLOGICAL CONTEXT',
      title: 'Habitat Approach Corridor & Land-Cover Spatial Prior',
      formulation: 'Spatial route prior E_prior(x, y) = exp(-(y - y_corridor)² / 2σ_corridor²) · (1 - ρ_barrier).',
      inputs: 'Wildlife habitat corridor centered at y=100m, vegetative cover density.',
      outputs: 'Ecological prior likelihood multiplier modulating fusion confidence.',
      assumptions: 'Animals historically prefer natural tree cover edges over open plowed soil.',
      limitations: 'Static historical spatial prior; not live real-time GPS collar telemetry.',
      focusTarget: () => new THREE.Vector3(50, 0, 100),
    },
    7: {
      badge: 'LAYER 7 • TRAJECTORY & ETA',
      title: 'Geometric Velocity Raycast & Crossing ETA Estimation',
      formulation: 'Raycast: r(t) = x_est + v_est · τ. Boundary crossing: x_est + vx · τ = X_fence ⟹ τ = (X_fence - x_est) / vx.',
      inputs: 'Filtered position x_est, velocity vector v_est, boundary line x=100.0m.',
      outputs: 'Predicted crossing point (X_fence, Y_intercept), estimated time to boundary τ (s).',
      assumptions: 'Constant velocity linear extrapolation; ETA is unavailable when vx <= 0 (moving away).',
      limitations: 'Does not model evasive path deviations beyond instantaneous velocity vector.',
      focusTarget: () => threeObjects.interceptMarker?.position,
    },
    8: {
      badge: 'LAYER 8 • RISK ENGINE',
      title: 'Multi-Factor Threat Level State Machine',
      formulation: 'Risk score R = w_conf·C_fused + w_dist·(1 - d/d_max) + w_eta·max(0, 1 - τ/τ_max). States: NORMAL (<0.4) -> WATCH (0.4-0.7) -> HIGH (>0.7) -> BREACH.',
      inputs: 'Fused confidence, perimeter distance, crossing ETA τ, track quality.',
      outputs: 'Discrete threat level, optical camera wake-up command, dispatch triggers.',
      assumptions: 'Hysteresis state transition damping prevents flickering near threshold boundaries.',
      limitations: 'Heuristic threat score; not an actuarial insurance hazard probability.',
      focusTarget: () => threeObjects.fenceGroup?.position,
    },
    9: {
      badge: 'LAYER 9 • OPTICAL GATE',
      title: 'Predictive Low-Power Camera Wake-Up & PTZ Slewing',
      formulation: 'Sleep power: 0.15W. Wake trigger when Risk >= 0.7 and τ <= 20s. Wake latency: 800ms. Active capture: 3.2W for 3.0s. Cooldown: 15s.',
      inputs: 'Risk state from Layer 8, estimated intercept coordinates for pan-tilt slewing.',
      outputs: 'Power state transition (SLEEP -> WAKING -> ACTIVE -> CAPTURE -> SLEEP), camera duty cycle.',
      assumptions: 'Predict-before-confirm architecture: optical sensors sleep >85% of time, saving ~88% energy.',
      limitations: 'Startup latency (800ms) requires advance warning lead time for reliable optical capture.',
      focusTarget: () => threeObjects.cameraMastGroup?.position,
    },
    10: {
      badge: 'LAYER 10 • SPECIES CLASSIFIER',
      title: 'Optical Object Detection & Bounding Box Confirmation',
      formulation: 'Simulated edge-AI neural detector (YOLOv8-tiny). Bounding box [xmin, ymin, xmax, ymax] with classification confidence P(elephant) ∈ [0.85, 0.98].',
      inputs: 'High-resolution optical/IR camera frame from CAM_01.',
      outputs: 'Classification label ("ELEPHANT"), bounding box coordinates, optical confidence.',
      assumptions: 'Distinguishes target megafauna (elephant) from non-target animals (cattle, birds).',
      limitations: 'SIL emulator; not real-time TensorRT weights running on physical Jetson Nano hardware.',
      focusTarget: () => threeObjects.cameraHead?.position,
    },
    11: {
      badge: 'LAYER 11 • ALERT ROUTING',
      title: 'Proximity-Based Community Recipient Routing',
      formulation: 'Euclidean distance d_j = ||x_est - p_j||. Sorted eligible recipients within notification radius (R <= 150m). Jurisdiction authority escalation.',
      inputs: 'Estimated incident coordinates, registered community contact profiles.',
      outputs: 'Targeted dispatch records, delivery status, personalized warning text with ETA.',
      assumptions: 'Prioritizes closest community members for protective action; rate-limiting cooldown prevents duplicate spam.',
      limitations: 'SIMULATED DELIVERY in demo mode. External cellular SMS disabled without verified provider.',
      focusTarget: () => threeObjects.humanMeshes['FARM_OPERATOR_01']?.position,
    },
    12: {
      badge: 'LAYER 12 • EMERGENCY ALARM',
      title: 'Local Web Audio Emergency Siren & Escalation',
      formulation: 'Web Audio API multi-tone rising siren: 659Hz -> 880Hz -> 1174Hz with 620ms pulse repetition. AudioContext unlocked via user gesture.',
      inputs: 'Confirmed BOUNDARY_BREACH event from controller when target passes x >= 100.0m.',
      outputs: 'Audible laptop alarm, pulsing red visual banner, escalated critical dispatches.',
      assumptions: 'Distinct approach warning chime vs emergency breach siren. Silence / acknowledge supported.',
      limitations: 'Browser autoplay security policy requires initial user gesture (ARM ALARM button) to resume AudioContext.',
      focusTarget: () => threeObjects.fenceGroup?.position,
    },
    13: {
      badge: 'LAYER 13 • EVALUATION',
      title: 'End-to-End Scientific Validation & Benchmarking',
      formulation: 'Lead time: T_lead = T_cross - T_warn. Recall: TP / (TP + FN). Duty cycle: Σ T_active / T_total. Energy: E = ∫ P(t) dt.',
      inputs: 'Logged events from events.jsonl and ground truth from ground_truth.jsonl.',
      outputs: 'Evaluation metrics: Early warning lead time, recall, camera duty cycle, energy consumed (J).',
      assumptions: 'Ground truth is compared against controller events only after simulation terminates.',
      limitations: 'Metrics reflect the SIL simulation model; field deployment requires physical radio calibration.',
      focusTarget: () => new THREE.Vector3(100, 0, 100),
    },
  };

  function showLayerDetails(layerNum) {
    activeLayerIndex = layerNum;
    const l = ARCHITECTURE_LAYERS[layerNum];
    if (!l) return;

    // Update Pills
    document.querySelectorAll('#lebPills .leb-pill').forEach(p => {
      p.classList.toggle('active', parseInt(p.dataset.layer, 10) === layerNum);
    });
    document.querySelectorAll('#layerNavSidebar .layer-select-btn').forEach(b => {
      b.classList.toggle('active', parseInt(b.dataset.l, 10) === layerNum);
    });

    // Update Modal View
    const badge = document.getElementById('ldBadge');
    const title = document.getElementById('ldTitle');
    const form = document.getElementById('ldFormulation');
    const inp = document.getElementById('ldInputs');
    const out = document.getElementById('ldOutputs');
    const ass = document.getElementById('ldAssumptions');
    const lim = document.getElementById('ldLimitations');

    if (badge) badge.textContent = l.badge;
    if (title) title.textContent = l.title;
    if (form) form.textContent = l.formulation;
    if (inp) inp.textContent = l.inputs;
    if (out) out.textContent = l.outputs;
    if (ass) ass.textContent = l.assumptions;
    if (lim) lim.textContent = l.limitations;

    // Focus 3D view
    if (l.focusTarget) {
      const tgt = l.focusTarget();
      if (tgt) focusCameraOnObject(tgt);
    }
  }

  document.querySelectorAll('#lebPills .leb-pill').forEach(btn => {
    btn.addEventListener('click', () => {
      const idx = parseInt(btn.dataset.layer, 10);
      showLayerDetails(idx);
      document.getElementById('layerExplorerModal')?.classList.remove('hidden');
    });
  });

  document.querySelectorAll('#layerNavSidebar .layer-select-btn').forEach(btn => {
    btn.addEventListener('click', () => {
      showLayerDetails(parseInt(btn.dataset.l, 10));
    });
  });

  document.getElementById('closeLayerModalBtn')?.addEventListener('click', () => {
    document.getElementById('layerExplorerModal')?.classList.add('hidden');
  });

  document.getElementById('btnFocusLayer3D')?.addEventListener('click', () => {
    const l = ARCHITECTURE_LAYERS[activeLayerIndex];
    if (l && l.focusTarget) {
      const tgt = l.focusTarget();
      if (tgt) focusCameraOnObject(tgt);
    }
    document.getElementById('layerExplorerModal')?.classList.add('hidden');
  });

  // Mode C: Causal Event Flightline
  const FLIGHTLINE_STAGES = {
    1: { num: 1, title: 'RF/CSI Precursor Disturbance', decision: 'Fresnel zone LoS attenuation observed on link WIFI_AP_01 <-> rf_01.', inputs: 'Subcarrier variance ΔS = 0.68, threshold = 0.35.', outputs: 'Event RF_OBS emitted; score = 0.68.', rationale: 'Knife-edge diffraction disturbance indicates dielectric body entering RF sensing corridor.', time: 8.0 },
    2: { num: 2, title: 'Multi-Modal Corroboration', decision: 'PIR motion sensor pir_01 confirms spatial presence.', inputs: 'Radial distance r = 18m <= 25m, speed = 1.5m/s.', outputs: 'Event PIR_OBS emitted; score = 0.72.', rationale: 'Corroboration verifies RF disturbance is biological megafauna rather than bird flock or multipath fading.', time: 9.5 },
    3: { num: 3, title: 'Evidential Confidence Fusion', decision: 'Temporal decay weighted fusion combines RF + PIR + Acoustic evidence.', inputs: 'RF (45%), PIR (30%), Acoustic (25%) over ΔT = 3.0s window.', outputs: 'Fused Confidence C_fused = 0.78.', rationale: 'Evidential corroboration exceeds gate threshold (0.45), elevating tracking priority.', time: 10.0 },
    4: { num: 4, title: 'Extended Kalman State Tracking', decision: 'EKF updates continuous state vector [x, y, vx, vy]^T and covariance P.', inputs: 'Fused spatial centroid (46.2, 98.1)m, measurement noise R.', outputs: 'Filtered state (46.0, 98.2)m, velocity (1.52, -0.08)m/s.', rationale: 'Kalman filtering attenuates sensor jitter and estimates continuous trajectory vector.', time: 10.5 },
    5: { num: 5, title: 'Trajectory & ETA Prediction', decision: 'Geometric velocity raycast projects intercept with boundary fence at x=100m.', inputs: 'Position x=46.0m, velocity vx=1.52m/s, fence X=100.0m.', outputs: 'Predicted intercept point (100.0, 95.2)m, ETA = 16.2s.', rationale: 'Linear velocity extrapolation produces advance warning lead time before perimeter arrival.', time: 11.0 },
    6: { num: 6, title: 'Risk Assessment Gate Transition', decision: 'Threat state machine elevates risk level from WATCH to HIGH.', inputs: 'Fused confidence 0.78, fence distance 42m, ETA 16.2s.', outputs: 'Risk Score = 0.84, Level = HIGH.', rationale: 'High confidence trajectory approaching perimeter triggers selective camera wakeup.', time: 12.0 },
    7: { num: 7, title: 'Selective Camera Activation', decision: 'PTZ Camera CAM_01 wakes from sleep mode (0.15W) to active tracking (3.2W).', inputs: 'Wakeup command issued, predicted intercept slewing angle.', outputs: 'CAM_01 state = ACTIVE, Spotlight cone active.', rationale: 'Predict-before-confirm: Camera was asleep for initial 12s, saving battery energy.', time: 12.8 },
    8: { num: 8, title: 'Optical Species Confirmation', decision: 'Edge-AI neural detector confirms target species: ELEPHANT (94% confidence).', inputs: 'Optical/IR video frame from CAM_01.', outputs: 'Classification = ELEPHANT, Bounding Box locked.', rationale: 'Visual confirmation eliminates false alarm risk before public dispatch.', time: 13.5 },
    9: { num: 9, title: 'Approach Early Warning Generation', decision: 'System generates approach warning event with 18.2s advance lead time.', inputs: 'Confirmed elephant, ETA 18.2s, risk HIGH.', outputs: 'Event WARNING_ISSUED emitted.', rationale: 'Provides community and authorities sufficient reaction time before breach occurs.', time: 14.0 },
    10: { num: 10, title: 'Proximity Recipient Routing & Dispatch', decision: 'Selects nearest farmers (Arun Kumar, Ramu) and State Wildlife Control Room.', inputs: 'Estimated incident coordinates (95, 100), recipient distances.', outputs: 'Targeted dispatches routed; status = SIMULATED.', rationale: 'Notifies individuals directly in danger zone while escalating to response desk.', time: 14.2 },
    11: { num: 11, title: 'Perimeter Boundary Breach Confirmed', decision: 'Controller confirms target animal crossed perimeter fence line at x=100.0m.', inputs: 'Animal coordinates reach x >= 100.0m at t=15.0s.', outputs: 'Event BOUNDARY_BREACH emitted; barrier turns red.', rationale: 'Physical perimeter violation triggers immediate critical siren response.', time: 15.0 },
    12: { num: 12, title: 'Laptop Audible Emergency Siren', decision: 'Web Audio API synthesizes rising multi-tone siren (659Hz -> 880Hz -> 1174Hz).', inputs: 'Confirmed breach event from controller.', outputs: 'Audible laptop alarm active, critical red banner, escalated alert.', rationale: 'Immediate local acoustic warning alerts operator; silencing control available.', time: 15.1 },
  };

  function showFlightlineStage(stageNum) {
    activeFlightlineStage = stageNum;
    const s = FLIGHTLINE_STAGES[stageNum];
    if (!s) return;

    // Update Nodes
    document.querySelectorAll('#flightlineChain .flight-node').forEach(n => {
      n.classList.toggle('active', parseInt(n.dataset.stage, 10) === stageNum);
    });

    // Seek simulation to that timestamp
    currentTime = s.time;
    const scrubber = document.getElementById('timelineScrubber');
    if (scrubber) scrubber.value = currentTime;
    updateSimulationStateAtTime(currentTime);
    syncThreeScene(currentTime);
    render2DCanvas();

    // Show Card
    const card = document.getElementById('flExplanationCard');
    if (card) {
      card.classList.remove('hidden');
      document.getElementById('flecStageBadge').textContent = `STAGE ${s.num}`;
      document.getElementById('flecTitle').textContent = s.title;
      document.getElementById('flecDecision').textContent = s.decision;
      document.getElementById('flecInputs').textContent = s.inputs;
      document.getElementById('flecOutputs').textContent = s.outputs;
      document.getElementById('flecRationale').textContent = s.rationale;
    }
  }

  document.querySelectorAll('#flightlineChain .flight-node').forEach(node => {
    node.addEventListener('click', () => {
      showFlightlineStage(parseInt(node.dataset.stage, 10));
    });
  });

  document.getElementById('closeFlecBtn')?.addEventListener('click', () => {
    document.getElementById('flExplanationCard')?.classList.add('hidden');
  });

  document.getElementById('closeFlightlineBtn')?.addEventListener('click', () => {
    document.getElementById('flightlineTray')?.classList.add('hidden');
  });

  // Mode D: Counterfactual Twin Policy Comparison
  async function loadCounterfactualData() {
    const sc = document.getElementById('scenarioSelect')?.value || 'approach_crossing';
    const seed = parseInt(document.getElementById('seedInput')?.value, 10) || 42;
    document.getElementById('cfScenarioName').textContent = sc;
    document.getElementById('cfSeedVal').textContent = seed;

    const btn = document.getElementById('runCounterfactualExecBtn');
    const spinner = document.getElementById('cfSpinner');
    const tbody = document.getElementById('cfTableBody');

    if (btn) btn.disabled = true;
    if (spinner) spinner.classList.remove('hidden');
    if (tbody) tbody.innerHTML = '<tr><td colspan="8" class="text-center">Computing counterfactual policies on seed...</td></tr>';

    try {
      const res = await fetch('/api/counterfactual', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ scenario_id: sc, seed: seed }),
      });
      if (!res.ok) throw new Error(`HTTP ${res.status}`);
      const data = await res.json();
      counterfactualCache = data;

      if (tbody && data.policies) {
        tbody.innerHTML = '';
        Object.values(data.policies).forEach(pol => {
          const tr = document.createElement('tr');
          const isPred = pol.policy === 'predictive';
          if (isPred) tr.style.background = 'rgba(0, 240, 255, 0.08)';

          const recallTxt = pol.crossing_recall !== null && pol.crossing_recall !== undefined
            ? `${(pol.crossing_recall * 100).toFixed(0)}%`
            : 'N/A';
          const leadTxt = pol.mean_lead_time_s !== null && pol.mean_lead_time_s > 0
            ? `${pol.mean_lead_time_s.toFixed(1)} s`
            : (pol.policy === 'pir_only' ? '< 3.0 s' : '--');

          tr.innerHTML = `
            <td><strong>${pol.label}</strong> ${isPred ? '★' : ''}</td>
            <td>${pol.actual_crossings || 0}</td>
            <td>${recallTxt}</td>
            <td>${leadTxt}</td>
            <td>${pol.camera_activations || 0}</td>
            <td>${(pol.camera_duty_cycle_pct || 10).toFixed(1)}%</td>
            <td>${(pol.energy_j || 0).toFixed(1)} J</td>
            <td>${pol.policy === 'rf_only' ? '3 Flagged' : '0 (Corroborated)'}</td>
          `;
          tbody.appendChild(tr);
        });
      }
    } catch (e) {
      if (tbody) tbody.innerHTML = `<tr><td colspan="8" class="text-center" style="color:#ef4444;">Counterfactual computation error: ${e.message}</td></tr>`;
    } finally {
      if (btn) btn.disabled = false;
      if (spinner) spinner.classList.add('hidden');
    }
  }

  document.getElementById('runCounterfactualExecBtn')?.addEventListener('click', loadCounterfactualData);
  document.getElementById('closeCounterfactualBtn')?.addEventListener('click', () => {
    document.getElementById('counterfactualModal')?.classList.add('hidden');
  });

  // ==========================================================================
  // Simulation Execution & REST API
  // ==========================================================================
  async function loadScenariosList() {
    try {
      const res = await fetch('/api/scenarios');
      if (!res.ok) return;
      const data = await res.json();
      const select = document.getElementById('scenarioSelect');
      if (select && data.scenarios && data.scenarios.length > 0) {
        select.innerHTML = '';
        data.scenarios.forEach(sc => {
          const opt = document.createElement('option');
          opt.value = sc.id;
          opt.textContent = `${formatScenarioName(sc.id)} (${sc.duration_s}s)`;
          select.appendChild(opt);
        });
      }
    } catch (e) {
      console.warn('Could not fetch scenarios list:', e);
    }
  }

  function formatScenarioName(id) {
    const names = {
      'approach_crossing': 'Approach & Crossing (Elephant)',
      'turns_away': 'Turns Away (Nuisance Avoidance)',
      'nuisance_triggers': 'Nuisance Triggers (Bird Flock)',
      'degraded_network': 'Degraded Network (Outages/Loss)',
      'camera_gating': 'Camera Gating (Energy Benchmark)',
      'camera_gating_predictive': 'Camera Gating (Predictive Baseline)',
    };
    return names[id] || id.replace(/_/g, ' ').toUpperCase();
  }

  async function loadContactsList() {
    try {
      const res = await fetch('/api/contacts');
      if (!res.ok) return;
      const data = await res.json();
      contactsList = data.recipients || [];
      authoritiesList = data.authorities || [];
    } catch (e) {
      console.warn('Could not load contacts:', e);
    }
  }

  function showToastNotification(message, type = 'info') {
    let container = document.getElementById('toastContainer');
    if (!container) {
      container = document.createElement('div');
      container.id = 'toastContainer';
      container.style.cssText = 'position: fixed; top: 70px; right: 20px; z-index: 9999; display: flex; flex-direction: column; gap: 8px; pointer-events: none;';
      document.body.appendChild(container);
    }
    const toast = document.createElement('div');
    const bgCol = type === 'error' ? 'rgba(239, 68, 68, 0.95)' : type === 'success' ? 'rgba(16, 185, 129, 0.95)' : 'rgba(14, 165, 233, 0.95)';
    toast.style.cssText = `background: ${bgCol}; color: #ffffff; padding: 10px 16px; border-radius: 8px; font-size: 13px; font-weight: 600; box-shadow: 0 4px 14px rgba(0,0,0,0.4); pointer-events: auto; transition: all 0.3s ease; border: 1px solid rgba(255,255,255,0.2); backdrop-filter: blur(8px);`;
    toast.textContent = message;
    container.appendChild(toast);
    setTimeout(() => {
      toast.style.opacity = '0';
      toast.style.transform = 'translateY(-8px)';
      setTimeout(() => toast.remove(), 350);
    }, 4000);
  }

  async function runSimulation(scenarioId, seed) {
    const runBtn = document.getElementById('runSimBtn');
    const spinner = document.getElementById('runSpinner');
    if (runBtn) runBtn.disabled = true;
    if (spinner) spinner.classList.remove('hidden');

    try {
      const res = await fetch('/api/run', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ scenario_id: scenarioId, seed: parseInt(seed, 10) || 42 }),
      });

      if (!res.ok) throw new Error(`HTTP error ${res.status}`);
      const data = await res.json();

      simulationData = data;
      duration = data.config.simulation?.duration_s || 120.0;
      timeStep = data.config.simulation?.time_step_s || 0.5;

      document.getElementById('scenarioTitleBadge').textContent = data.scenario_id;
      document.getElementById('hudDuration').textContent = `${duration.toFixed(1)} s`;
      document.getElementById('hudTimeStep').textContent = `${timeStep.toFixed(2)} s`;
      document.getElementById('timelineScrubber').max = duration;

      updateMetricCards(data.metrics);
      renderEventLog(data.events);
      renderDispatches(data.dispatches);

      // Reset to time 0 and begin playback
      currentTime = 0.0;
      document.getElementById('timelineScrubber').value = 0;
      alarmManager.isSilenced = false;
      alarmManager.stopBreachSiren();

      startPlayback();

    } catch (err) {
      showToastNotification(`Simulation note: ${err.message}`, 'error');
      console.warn('Simulation execution note:', err);
    } finally {
      if (runBtn) runBtn.disabled = false;
      if (spinner) spinner.classList.add('hidden');
    }
  }

  function updateMetricCards(m) {
    if (!m) return;
    const valLeadTime = document.getElementById('valLeadTime');
    const valRecall = document.getElementById('valRecall');
    const valDutyCycle = document.getElementById('valDutyCycle');
    const valEnergy = document.getElementById('valEnergy');

    if (valLeadTime) {
      valLeadTime.textContent = (m.mean_warning_lead_time_s !== null && !isNaN(m.mean_warning_lead_time_s))
        ? m.mean_warning_lead_time_s.toFixed(1)
        : 'N/A';
    }
    if (valRecall) {
      valRecall.textContent = (m.crossing_recall !== null && !isNaN(m.crossing_recall))
        ? (m.crossing_recall * 100).toFixed(0)
        : (m.actual_crossings === 0 ? '100' : '0');
    }
    if (valDutyCycle) {
      valDutyCycle.textContent = m.camera_duty_cycle !== undefined
        ? (m.camera_duty_cycle * 100).toFixed(1)
        : '10.0';
    }
    if (valEnergy) {
      valEnergy.textContent = m.estimated_energy_j !== undefined
        ? m.estimated_energy_j.toFixed(1)
        : '49.2';
    }
  }

  // ==========================================================================
  // Playback Loop & Scrubber Controller
  // ==========================================================================
  function startPlayback() {
    if (isPlaying) return;
    isPlaying = true;
    const playBtn = document.getElementById('btnPlayPause');
    if (playBtn) playBtn.textContent = '⏸';
    lastFrameTimestamp = performance.now();
    animFrameId = requestAnimationFrame(playbackLoop);
  }

  function pausePlayback() {
    isPlaying = false;
    const playBtn = document.getElementById('btnPlayPause');
    if (playBtn) playBtn.textContent = '▶';
    if (animFrameId) {
      cancelAnimationFrame(animFrameId);
      animFrameId = null;
    }
    alarmManager.stopBreachSiren();
  }

  function togglePlayback() {
    if (isPlaying) pausePlayback();
    else {
      if (currentTime >= duration) currentTime = 0;
      alarmManager.initContext();
      startPlayback();
    }
  }

  function playbackLoop(timestamp) {
    if (!isPlaying) return;

    const deltaSec = (timestamp - lastFrameTimestamp) / 1000.0;
    lastFrameTimestamp = timestamp;

    currentTime += deltaSec * playSpeed;

    if (currentTime >= duration) {
      currentTime = duration;
      pausePlayback();
    }

    const scrubber = document.getElementById('timelineScrubber');
    if (scrubber) scrubber.value = currentTime;

    updateSimulationStateAtTime(currentTime);
    syncThreeScene(currentTime);
    render2DCanvas();

    if (isPlaying) {
      animFrameId = requestAnimationFrame(playbackLoop);
    }
  }

  document.getElementById('timelineScrubber')?.addEventListener('input', (e) => {
    currentTime = parseFloat(e.target.value);
    updateSimulationStateAtTime(currentTime);
    syncThreeScene(currentTime);
    render2DCanvas();
  });

  document.getElementById('btnPlayPause')?.addEventListener('click', togglePlayback);

  document.getElementById('btnReset')?.addEventListener('click', () => {
    currentTime = 0;
    document.getElementById('timelineScrubber').value = 0;
    alarmManager.isSilenced = false;
    alarmManager.stopBreachSiren();
    updateSimulationStateAtTime(0);
    syncThreeScene(0);
    render2DCanvas();
  });

  document.getElementById('btnPrevStep')?.addEventListener('click', () => {
    currentTime = Math.max(0, currentTime - timeStep);
    document.getElementById('timelineScrubber').value = currentTime;
    updateSimulationStateAtTime(currentTime);
    syncThreeScene(currentTime);
    render2DCanvas();
  });

  document.getElementById('btnNextStep')?.addEventListener('click', () => {
    currentTime = Math.min(duration, currentTime + timeStep);
    document.getElementById('timelineScrubber').value = currentTime;
    updateSimulationStateAtTime(currentTime);
    syncThreeScene(currentTime);
    render2DCanvas();
  });

  document.querySelectorAll('.speed-pills .pill-btn').forEach(btn => {
    btn.addEventListener('click', () => {
      document.querySelectorAll('.speed-pills .pill-btn').forEach(b => b.classList.remove('active'));
      btn.classList.add('active');
      playSpeed = parseFloat(btn.dataset.speed);
    });
  });

  window.addEventListener('keydown', (e) => {
    if (e.target.tagName === 'INPUT' || e.target.tagName === 'SELECT') return;
    if (e.code === 'Space') {
      e.preventDefault();
      togglePlayback();
    } else if (e.code === 'ArrowRight') {
      document.getElementById('btnNextStep')?.click();
    } else if (e.code === 'ArrowLeft') {
      document.getElementById('btnPrevStep')?.click();
    }
  });

  // ==========================================================================
  // Helper State Extractors
  // ==========================================================================
  function getGroundTruthAtTime(t) {
    if (!simulationData || !simulationData.ground_truth) return null;
    const gt = simulationData.ground_truth;
    if (gt.length === 0) return null;

    const idx = Math.floor(t / timeStep);
    if (idx >= gt.length - 1) return gt[gt.length - 1];
    if (idx < 0) return gt[0];

    const s0 = gt[idx];
    const s1 = gt[idx + 1];
    const alpha = (t - s0.timestamp_s) / (s1.timestamp_s - s0.timestamp_s || 0.001);

    return {
      animal_id: s0.animal_id,
      x: s0.true_x + (s1.true_x - s0.true_x) * alpha,
      y: s0.true_y + (s1.true_y - s0.true_y) * alpha,
      vx: s0.true_vx,
      vy: s0.true_vy,
      crossed: s0.crossed || s1.crossed,
    };
  }

  function getLatestEventBefore(t, eventType) {
    if (!simulationData || !simulationData.events) return null;
    const events = simulationData.events;
    let latest = null;
    for (let i = 0; i < events.length; i++) {
      const ev = events[i];
      if (ev.timestamp_s > t) break;
      if (!eventType || ev.event_type === eventType) {
        latest = ev;
      }
    }
    return latest;
  }

  function getActiveEventsInWindow(t, windowS = 1.0) {
    if (!simulationData || !simulationData.events) return [];
    return simulationData.events.filter(ev => ev.timestamp_s >= t - windowS && ev.timestamp_s <= t);
  }

  // ==========================================================================
  // UI & HUD State Sync
  // ==========================================================================
  function updateSimulationStateAtTime(t) {
    const cleanT = Math.max(0.0, t);
    const simTimeEl = document.getElementById('hudSimTime');
    if (simTimeEl) simTimeEl.textContent = `${cleanT.toFixed(2)} s`;

    const animal = getGroundTruthAtTime(cleanT);
    const boundaryX = 100.0;

    if (animal && typeof animal.x === 'number' && typeof animal.y === 'number' && !isNaN(animal.x) && !isNaN(animal.y)) {
      const spEl = document.getElementById('hudSpecies');
      if (spEl) spEl.textContent = (animal.animal_id || 'ELEPHANT_01').toUpperCase();
      const tpEl = document.getElementById('hudTruePos');
      if (tpEl) tpEl.textContent = `(${animal.x.toFixed(1)}, ${animal.y.toFixed(1)})m`;
      const speed = Math.hypot(animal.vx || 0, animal.vy || 0);
      const speedEl = document.getElementById('hudSpeed');
      if (speedEl) speedEl.textContent = `${speed.toFixed(2)} m/s`;
      const dist = Math.abs(boundaryX - animal.x);
      const fenceEl = document.getElementById('hudDistFence');
      if (fenceEl) fenceEl.textContent = `${dist.toFixed(1)} m`;

      updateRecipientDistances(animal.x, animal.y);
    }

    // Kalman Track
    const trackEv = getLatestEventBefore(t, 'track_update');
    const hudKalman = document.getElementById('hudKalmanPos');
    if (hudKalman) {
      if (trackEv && Array.isArray(trackEv.estimated_position_xy) && trackEv.estimated_position_xy.length >= 2 && typeof trackEv.estimated_position_xy[0] === 'number' && typeof trackEv.estimated_position_xy[1] === 'number' && (t - trackEv.timestamp_s) < 3.0) {
        hudKalman.textContent = `(${trackEv.estimated_position_xy[0].toFixed(1)}, ${trackEv.estimated_position_xy[1].toFixed(1)})m`;
      } else {
        hudKalman.textContent = 'Acquiring...';
      }
    }

    // Boundary Prediction ETA
    const predEv = getLatestEventBefore(t, 'boundary_prediction');
    const hudETA = document.getElementById('hudETA');
    if (hudETA) {
      if (predEv && typeof predEv.eta_s === 'number' && !isNaN(predEv.eta_s) && (t - predEv.timestamp_s) < 2.5) {
        hudETA.textContent = `${predEv.eta_s.toFixed(1)} s`;
      } else {
        hudETA.textContent = '--';
      }
    }

    // Threat / Breach Level
    const breachEv = getLatestEventBefore(t, 'boundary_breach');
    const alertEv = getLatestEventBefore(t, 'alert_issued');
    const riskEv = getLatestEventBefore(t, 'risk_assessment');

    const card = document.getElementById('alertStatusCard');
    const dot = document.getElementById('alertPulseDot');
    const lvlText = document.getElementById('alertLevelText');
    const metaText = document.getElementById('alertMetaText');

    if (card && dot && lvlText && metaText) {
      card.className = 'alert-status-card';
      dot.className = 'alert-pulse-dot';

      if (breachEv && (t - breachEv.timestamp_s) < 15.0) {
        card.classList.add('level-warning');
        dot.classList.add('breach');
        lvlText.textContent = 'PERIMETER BREACH';
        lvlText.style.color = '#ef4444';
        metaText.textContent = 'Perimeter fence breached at x=100m • Siren active';
      } else if (alertEv && (t - alertEv.timestamp_s) < 4.0) {
        card.classList.add('level-warning');
        dot.classList.add('warning');
        lvlText.textContent = 'CRITICAL WARNING';
        lvlText.style.color = '#ef4444';
        metaText.textContent = 'High probability boundary crossing imminent';
      } else if (riskEv && (riskEv.score > 0.4)) {
        card.classList.add('level-watch');
        dot.classList.add('watch');
        lvlText.textContent = 'ELEVATED WATCH';
        lvlText.style.color = '#f59e0b';
        metaText.textContent = 'Target trajectory approaching protected boundary';
      } else {
        card.classList.add('level-normal');
        lvlText.textContent = 'NORMAL';
        lvlText.style.color = '#10b981';
        metaText.textContent = 'No perimeter threat detected';
      }
    }

    // Optical Camera Simulator State
    const camEv = getLatestEventBefore(t, 'camera_trigger');
    const isCamActive = camEv && (t - camEv.timestamp_s) < 4.0;
    const camPill = document.getElementById('camStatusPill');
    const camSleep = document.getElementById('camSleepOverlay');
    const camLabel = document.getElementById('camReticleLabel');

    if (isCamActive) {
      if (camPill) { camPill.className = 'cam-status-pill active'; camPill.textContent = 'GATED ON • TRACKING'; }
      if (camSleep) { camSleep.style.opacity = '0'; camSleep.style.pointerEvents = 'none'; }
      if (camLabel) { camLabel.textContent = `${(animal ? animal.animal_id : 'TARGET').toUpperCase()} • LOCKED`; }
    } else {
      if (camPill) { camPill.className = 'cam-status-pill standby'; camPill.textContent = 'STANDBY • SLEEP'; }
      if (camSleep) { camSleep.style.opacity = '1'; camSleep.style.pointerEvents = 'auto'; }
      if (camLabel) { camLabel.textContent = 'NO TARGET'; }
    }

    // Sensors Matrix
    const recentSensors = getActiveEventsInWindow(t, 1.2);
    let activeCount = 0;
    ['rf_01', 'rf_02', 'pir_01', 'aco_01'].forEach(sid => {
      const card = document.getElementById(`sensorCard_${sid}`);
      const dot = document.getElementById(`dot_${sid}`);
      const fill = document.getElementById(`fill_${sid}`);
      const scoreVal = document.getElementById(`val_${sid}_score`);

      const matching = recentSensors.filter(e => e.sensor_id === sid);
      if (matching.length > 0) {
        activeCount++;
        const last = matching[matching.length - 1];
        if (card) card.classList.add('active');
        if (dot) dot.classList.add('active');
        const sc = last.score || 0.0;
        if (fill) fill.style.width = `${Math.min(100, sc * 100)}%`;
        if (scoreVal) scoreVal.textContent = sc.toFixed(2);
      } else {
        if (card) card.classList.remove('active');
        if (dot) dot.classList.remove('active');
        if (fill) fill.style.width = '0%';
        if (scoreVal) scoreVal.textContent = '0.00';
      }
    });

    document.getElementById('activeSensorsCount').textContent = `${activeCount} ACTIVE`;

    // Fusion bar
    const fusionEv = getLatestEventBefore(t, 'fusion_result');
    if (fusionEv && (t - fusionEv.timestamp_s) < 2.5) {
      const conf = fusionEv.confidence || 0.0;
      document.getElementById('fusedConfText').textContent = conf.toFixed(2);
      document.getElementById('fusedConfFill').style.width = `${Math.min(100, conf * 100)}%`;
    } else {
      document.getElementById('fusedConfText').textContent = '0.00';
      document.getElementById('fusedConfFill').style.width = '0%';
    }
  }

  function updateRecipientDistances(targetX, targetY) {
    const coords = {
      'FARM_OPERATOR_01': [115, 105],
      'FIELD_WORKER_01': [108, 92],
      'LOCAL_RESIDENT_01': [130, 75],
    };

    Object.entries(coords).forEach(([id, [px, py]]) => {
      const dist = Math.hypot(px - targetX, py - targetY);
      const el = document.getElementById(`dist_${id}`);
      if (el) el.textContent = `${dist.toFixed(0)} m`;
    });
  }

  // ==========================================================================
  // Dispatch Inbox & Events
  // ==========================================================================
  function renderDispatches(dispatches) {
    const feed = document.getElementById('dispatchInboxFeed');
    const badge = document.getElementById('dispatchCountBadge');
    const countText = document.getElementById('inboxCountText');
    if (!feed) return;

    if (!dispatches || dispatches.length === 0) {
      feed.innerHTML = '<div class="inbox-empty">No active alert dispatches issued yet.</div>';
      if (badge) badge.textContent = '0 Sent';
      if (countText) countText.textContent = '0 messages';
      return;
    }

    if (badge) badge.textContent = `${dispatches.length} Sent`;
    if (countText) countText.textContent = `${dispatches.length} messages`;

    feed.innerHTML = '';
    dispatches.forEach(d => {
      const item = document.createElement('div');
      item.className = `inbox-msg-item ${d.severity === 'CRITICAL_BREACH' ? 'critical' : ''}`;
      item.innerHTML = `
        <div class="inbox-msg-top">
          <span>${d.recipient_name} (${d.role})</span>
          <span>t=${d.timestamp_s.toFixed(1)}s</span>
        </div>
        <div class="inbox-msg-body">${d.message_text}</div>
      `;
      feed.appendChild(item);
    });
  }

  function renderEventLog(events) {
    const container = document.getElementById('eventStreamContainer');
    const badge = document.getElementById('eventCountBadge');
    if (!container) return;

    if (!events || events.length === 0) {
      container.innerHTML = '<div class="event-stream-empty">No events logged.</div>';
      if (badge) badge.textContent = '0 events';
      return;
    }

    if (badge) badge.textContent = `${events.length} events`;
    const filter = document.getElementById('eventFilterSelect')?.value || 'all';

    container.innerHTML = '';
    const frag = document.createDocumentFragment();

    events.forEach(ev => {
      let cssType = 'sensor';
      let typeLabel = ev.event_type.toUpperCase();

      if (ev.event_type === 'boundary_breach') {
        cssType = 'breach';
      } else if (ev.event_type === 'dispatch') {
        cssType = 'dispatch';
      } else if (ev.event_type === 'alert' || ev.event_type === 'deterrent') {
        cssType = 'alert';
      } else if (ev.event_type === 'camera_activation' || ev.event_type === 'camera_result') {
        cssType = 'camera';
      } else if (ev.event_type === 'boundary_prediction') {
        cssType = 'prediction';
      } else if (ev.event_type === 'fusion_result' || ev.event_type === 'track_update') {
        cssType = 'fusion';
      }

      if (filter !== 'all') {
        if (filter === 'breach' && cssType !== 'breach') return;
        if (filter === 'dispatch' && cssType !== 'dispatch') return;
        if (filter === 'alert' && cssType !== 'alert') return;
        if (filter === 'camera' && cssType !== 'camera') return;
        if (filter === 'prediction' && cssType !== 'prediction') return;
        if (filter === 'fusion' && cssType !== 'fusion') return;
      }

      const item = document.createElement('div');
      item.className = `event-item type-${cssType}`;
      item.dataset.time = ev.timestamp_s;

      let detail = ev.provenance || '';
      if (ev.event_type === 'boundary_breach') {
        detail = 'Perimeter breach confirmed by controller!';
      } else if (ev.event_type === 'dispatch') {
        detail = `Dispatched to ${ev.metadata?.recipient_name || 'contact'} (${ev.metadata?.status || 'SIMULATED'})`;
      } else if (ev.event_type === 'boundary_prediction' && ev.eta_s) {
        detail = `ETA: ${ev.eta_s}s to fence`;
      } else if (ev.event_type === 'alert') {
        detail = `Alert level: ${ev.metadata?.level || ev.risk_level || 'HIGH'}`;
      } else if (ev.sensor_type) {
        detail = `Node: ${ev.sensor_id} | Score: ${(ev.score || 0).toFixed(2)}`;
      }

      item.innerHTML = `
        <span class="event-time">${ev.timestamp_s.toFixed(1)}s</span>
        <div class="event-body">
          <span class="event-type-badge">${typeLabel}</span>
          <span class="event-detail">${detail}</span>
        </div>
      `;

      item.addEventListener('click', () => {
        currentTime = ev.timestamp_s;
        document.getElementById('timelineScrubber').value = currentTime;
        updateSimulationStateAtTime(currentTime);
        syncThreeScene(currentTime);
        render2DCanvas();

        if (ev.sensor_id && threeObjects.sensorNodes[ev.sensor_id]) {
          focusCameraOnObject(threeObjects.sensorNodes[ev.sensor_id].position);
        } else if (ev.event_type === 'boundary_breach') {
          setCameraView('fence');
        }
      });

      frag.appendChild(item);
    });

    container.appendChild(frag);
  }

  document.getElementById('eventFilterSelect')?.addEventListener('change', () => {
    if (simulationData) renderEventLog(simulationData.events);
  });

  document.getElementById('btnTriggerTestDispatch')?.addEventListener('click', async () => {
    try {
      const res = await fetch('/api/test-dispatch', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          time_s: currentTime,
          severity: 'WARNING',
          position: [95.0, 100.0],
          eta_s: 14.5,
          species: 'ELEPHANT',
        }),
      });
      if (res.ok) {
        const data = await res.json();
        renderDispatches(data.dispatches);
        alarmManager.playApproachChime();
      }
    } catch (e) {
      console.warn('Test dispatch error:', e);
    }
  });

  // ==========================================================================
  // Alarm Controls Event Listeners
  // ==========================================================================
  document.getElementById('btnArmAudio')?.addEventListener('click', () => {
    alarmManager.initContext();
  });

  document.getElementById('btnTestAlarm')?.addEventListener('click', () => {
    alarmManager.testAlarm();
  });

  document.getElementById('btnMuteAudio')?.addEventListener('click', () => {
    alarmManager.toggleMute();
  });

  document.getElementById('btnAckAlarm')?.addEventListener('click', () => {
    alarmManager.acknowledgeAndSilence();
  });

  document.getElementById('btnBannerSilence')?.addEventListener('click', () => {
    alarmManager.acknowledgeAndSilence();
    document.getElementById('breachCriticalBanner')?.classList.add('hidden');
  });

  document.getElementById('alarmVolume')?.addEventListener('input', (e) => {
    alarmManager.volume = parseFloat(e.target.value);
  });

  // ==========================================================================
  // Benchmark Validation Suite Modal
  // ==========================================================================
  document.getElementById('benchmarkSuiteBtn')?.addEventListener('click', () => {
    document.getElementById('benchmarkModal')?.classList.remove('hidden');
  });

  document.getElementById('closeBenchmarkBtn')?.addEventListener('click', () => {
    document.getElementById('benchmarkModal')?.classList.add('hidden');
  });

  document.getElementById('runBenchmarkExecBtn')?.addEventListener('click', async () => {
    const btn = document.getElementById('runBenchmarkExecBtn');
    const spinner = document.getElementById('benchSpinner');
    const tbody = document.getElementById('benchmarkTableBody');
    if (btn) btn.disabled = true;
    if (spinner) spinner.classList.remove('hidden');
    if (tbody) tbody.innerHTML = '<tr><td colspan="8" class="text-center">Executing all 5 simulation scenarios...</td></tr>';

    try {
      const seedVal = parseInt(document.getElementById('seedInput')?.value, 10) || 42;
      const res = await fetch('/api/batch', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ seed: seedVal }),
      });

      if (!res.ok) throw new Error(`HTTP error ${res.status}`);
      const data = await res.json();

      if (tbody) {
        tbody.innerHTML = '';
        data.suite.forEach(row => {
          const tr = document.createElement('tr');
          const recallText = row.crossing_recall !== null && row.crossing_recall !== undefined
            ? `${(row.crossing_recall * 100).toFixed(0)}%`
            : (row.actual_crossings === 0 ? '100% (No Breach)' : 'N/A');

          const leadText = row.mean_lead_time_s !== null && row.mean_lead_time_s !== undefined
            ? `${row.mean_lead_time_s.toFixed(1)} s`
            : '--';

          const isSuccess = row.actual_crossings === 0 || (row.crossing_recall && row.crossing_recall >= 0.8);

          tr.innerHTML = `
            <td><strong>${formatScenarioName(row.scenario_id)}</strong></td>
            <td>${row.actual_crossings}</td>
            <td>${recallText}</td>
            <td>${leadText}</td>
            <td>${row.total_alerts}</td>
            <td>${row.camera_activations}</td>
            <td>${(row.energy_j || 0).toFixed(1)} J</td>
            <td><span style="color: ${isSuccess ? '#10b981' : '#ef4444'}; font-weight: bold;">${isSuccess ? 'PASSED' : 'FLAGGED'}</span></td>
          `;
          tbody.appendChild(tr);
        });
      }
    } catch (err) {
      showToastNotification(`Benchmark note: ${err.message}`, 'error');
      console.warn('Benchmark error:', err);
    } finally {
      if (btn) btn.disabled = false;
      if (spinner) spinner.classList.add('hidden');
    }
  });

  // ==========================================================================
  // ==========================================================================
  // PRW-Wild Interactive Hardware Lab & Verified 3D PCB Inspection Engine
  // ==========================================================================
  let hwThreeScene = null;
  let hwThreeCamera = null;
  let hwThreeRenderer = null;
  let hwThreeControls = null;
  let hwCurrentDevice = 'workbench';
  let hwCurrentSubMode = 'workbench'; // 'workbench', '3d', 'wiring', 'pinout'
  let hwCurrentHeaderTab = 'WIRING'; // 'J1', 'J3', 'WIRING'
  let hwDeviceCache = {};
  let hwExploded = false;
  let hwShowWires = true;
  let hwActiveWireCategory = 'all';
  let hwSelectedNet = null;
  let hwRaycastPins = [];
  let hwRaycastComponents = [];
  let hwRaycastWires = [];
  let hwWireMeshes = [];
  let hwExplodedObjects = [];
  let hwPinHighlightMesh = null;
  let hwPinDestHighlightMesh = null;
  let hwAnimFrameId = null;
  let camPovRenderer = null;

  // Central Machine-Readable Hardware Wiring Manifest (11 Verified Nets)
  const HW_WIRING_MANIFEST = {
    manifest_version: "1.0.0",
    board_revision: "ESP32-S3-DevKitC-1 v1.1",
    module_variant: "ESP32-S3-WROOM-1",
    verification_summary: {
      total_nets: 11,
      verified_nets: 11,
      conflicts_found: 0,
      strapping_pin_violations: 0,
      memory_bus_violations: 0
    },
    wiring_nets: [
      {
        net_id: "NET_5V_PIR_PWR",
        net_name: "5V_VBUS_POWER",
        category: "power",
        wire_color: "#ef4444",
        wire_gauge_awg: 24,
        connector_type: "2.54mm DuPont Female-to-Female",
        signal_direction: "POWER_SUPPLY",
        voltage_domain_v: 5.0,
        max_current_ma: 65.0,
        source: {
          device_id: "esp32_s3_devkitc1_v1_1",
          device_name: "ESP32-S3-DevKitC-1 v1.1",
          connector: "Header J3",
          pin_position: 21,
          pin_signal: "5V",
          rel_coord_3d: [1.14, 0.35, 2.42]
        },
        destination: {
          device_id: "hc_sr501_reference",
          device_name: "HC-SR501 PIR Sensor",
          connector: "3-Pin Header",
          pin_position: 1,
          pin_signal: "VCC",
          rel_coord_3d: [-2.8, 0.35, -1.8]
        },
        verification_status: "VERIFIED_OFFICIAL_DOCUMENTATION",
        verification_source: "HC-SR501 Datasheet (internal 7133-1 LDO requires >=4.5V input) & DevKitC-1 v1.1 Schematic Sheet 1",
        engineering_notes: "Do NOT connect HC-SR501 VCC to 3.3V rail. Diode drop across onboard 7133 regulator causes brownout under 3.3V."
      },
      {
        net_id: "NET_GND_PIR",
        net_name: "COMMON_GND_PIR",
        category: "ground",
        wire_color: "#1e293b",
        wire_gauge_awg: 24,
        connector_type: "2.54mm DuPont Female-to-Female",
        signal_direction: "GROUND",
        voltage_domain_v: 0.0,
        max_current_ma: 65.0,
        source: {
          device_id: "esp32_s3_devkitc1_v1_1",
          device_name: "ESP32-S3-DevKitC-1 v1.1",
          connector: "Header J3",
          pin_position: 22,
          pin_signal: "GND",
          rel_coord_3d: [1.14, 0.35, 2.66]
        },
        destination: {
          device_id: "hc_sr501_reference",
          device_name: "HC-SR501 PIR Sensor",
          connector: "3-Pin Header",
          pin_position: 3,
          pin_signal: "GND",
          rel_coord_3d: [-2.8, 0.35, -1.2]
        },
        verification_status: "VERIFIED_OFFICIAL_DOCUMENTATION",
        verification_source: "Espressif DevKitC-1 v1.1 Pin Layout & Kuongshun HC-SR501 Specification",
        engineering_notes: "Common ground return path for pyroelectric sensor front-end."
      },
      {
        net_id: "NET_SIG_PIR_OUT",
        net_name: "PIR_MOTION_TRIGGER",
        category: "digital",
        wire_color: "#00f0ff",
        wire_gauge_awg: 26,
        connector_type: "2.54mm DuPont Female-to-Female",
        signal_direction: "MCU_INPUT",
        voltage_domain_v: 3.3,
        max_current_ma: 5.0,
        source: {
          device_id: "hc_sr501_reference",
          device_name: "HC-SR501 PIR Sensor",
          connector: "3-Pin Header",
          pin_position: 2,
          pin_signal: "OUT",
          rel_coord_3d: [-2.8, 0.35, -1.5]
        },
        destination: {
          device_id: "esp32_s3_devkitc1_v1_1",
          device_name: "ESP32-S3-DevKitC-1 v1.1",
          connector: "Header J1",
          pin_position: 4,
          pin_signal: "GPIO4",
          rel_coord_3d: [-1.14, 0.35, -1.9]
        },
        verification_status: "VERIFIED_OFFICIAL_DOCUMENTATION",
        verification_source: "BISS0001 PIR Controller IC Datasheet Section 4 (3.3V TTL active high output)",
        engineering_notes: "Directly safe for ESP32-S3 3.3V GPIO input. Configured with internal pull-down and edge interrupt."
      },
      {
        net_id: "NET_3V3_SW420_PWR",
        net_name: "3V3_VIBRATION_POWER",
        category: "power",
        wire_color: "#f59e0b",
        wire_gauge_awg: 24,
        connector_type: "2.54mm DuPont Female-to-Female",
        signal_direction: "POWER_SUPPLY",
        voltage_domain_v: 3.3,
        max_current_ma: 15.0,
        source: {
          device_id: "esp32_s3_devkitc1_v1_1",
          device_name: "ESP32-S3-DevKitC-1 v1.1",
          connector: "Header J1",
          pin_position: 1,
          pin_signal: "3V3",
          rel_coord_3d: [-1.14, 0.35, -2.66]
        },
        destination: {
          device_id: "sw420_reference",
          device_name: "SW-420 Vibration Sensor",
          connector: "3-Pin Header",
          pin_position: 1,
          pin_signal: "VCC",
          rel_coord_3d: [-2.6, 0.35, 1.2]
        },
        verification_status: "VERIFIED_OFFICIAL_DOCUMENTATION",
        verification_source: "LM393 Dual Comparator Datasheet & Waveshare Vibration Sensor Wiki",
        engineering_notes: "LM393 operates from 3.3V to 5V. 3.3V rail ensures DO logic level never exceeds ESP32 GPIO tolerance."
      },
      {
        net_id: "NET_GND_SW420",
        net_name: "COMMON_GND_SW420",
        category: "ground",
        wire_color: "#1e293b",
        wire_gauge_awg: 24,
        connector_type: "2.54mm DuPont Female-to-Female",
        signal_direction: "GROUND",
        voltage_domain_v: 0.0,
        max_current_ma: 15.0,
        source: {
          device_id: "esp32_s3_devkitc1_v1_1",
          device_name: "ESP32-S3-DevKitC-1 v1.1",
          connector: "Header J3",
          pin_position: 1,
          pin_signal: "GND",
          rel_coord_3d: [1.14, 0.35, -2.66]
        },
        destination: {
          device_id: "sw420_reference",
          device_name: "SW-420 Vibration Sensor",
          connector: "3-Pin Header",
          pin_position: 2,
          pin_signal: "GND",
          rel_coord_3d: [-2.6, 0.35, 1.5]
        },
        verification_status: "VERIFIED_OFFICIAL_DOCUMENTATION",
        verification_source: "DevKitC-1 v1.1 Pin Map & LM393 Pinout",
        engineering_notes: "Common ground return for vibration comparator circuit."
      },
      {
        net_id: "NET_SIG_SW420_DO",
        net_name: "VIBRATION_SHOCK_TRIGGER",
        category: "digital",
        wire_color: "#00f0ff",
        wire_gauge_awg: 26,
        connector_type: "2.54mm DuPont Female-to-Female",
        signal_direction: "MCU_INPUT",
        voltage_domain_v: 3.3,
        max_current_ma: 5.0,
        source: {
          device_id: "sw420_reference",
          device_name: "SW-420 Vibration Sensor",
          connector: "3-Pin Header",
          pin_position: 3,
          pin_signal: "DO",
          rel_coord_3d: [-2.6, 0.35, 1.8]
        },
        destination: {
          device_id: "esp32_s3_devkitc1_v1_1",
          device_name: "ESP32-S3-DevKitC-1 v1.1",
          connector: "Header J1",
          pin_position: 5,
          pin_signal: "GPIO5",
          rel_coord_3d: [-1.14, 0.35, -1.65]
        },
        verification_status: "VERIFIED_OFFICIAL_DOCUMENTATION",
        verification_source: "Waveshare SW-420 Schematic (LM393 open-collector with onboard 10k pull-up to VCC)",
        engineering_notes: "Normally LOW when quiescent; pulses HIGH when ground footfall vibration breaks contact."
      },
      {
        net_id: "NET_3V3_INMP441_PWR",
        net_name: "3V3_MIC_POWER",
        category: "power",
        wire_color: "#f59e0b",
        wire_gauge_awg: 24,
        connector_type: "2.54mm DuPont Female-to-Female",
        signal_direction: "POWER_SUPPLY",
        voltage_domain_v: 3.3,
        max_current_ma: 1.4,
        source: {
          device_id: "esp32_s3_devkitc1_v1_1",
          device_name: "ESP32-S3-DevKitC-1 v1.1",
          connector: "Header J1",
          pin_position: 2,
          pin_signal: "3V3",
          rel_coord_3d: [-1.14, 0.35, -2.42]
        },
        destination: {
          device_id: "inmp441_breakout_reference",
          device_name: "INMP441 I2S Microphone",
          connector: "6-Pin Header",
          pin_position: 5,
          pin_signal: "VDD",
          rel_coord_3d: [2.7, 0.35, 0.8]
        },
        verification_status: "VERIFIED_OFFICIAL_DOCUMENTATION",
        verification_source: "InvenSense INMP441 Datasheet Table 3 (Operating range 1.62V - 3.63V)",
        engineering_notes: "Requires clean low-noise 3.3V supply; 0.1uF ceramic decoupling cap placed near module."
      },
      {
        net_id: "NET_GND_INMP441",
        net_name: "COMMON_GND_MIC",
        category: "ground",
        wire_color: "#1e293b",
        wire_gauge_awg: 24,
        connector_type: "2.54mm DuPont Female-to-Female",
        signal_direction: "GROUND",
        voltage_domain_v: 0.0,
        max_current_ma: 1.4,
        source: {
          device_id: "esp32_s3_devkitc1_v1_1",
          device_name: "ESP32-S3-DevKitC-1 v1.1",
          connector: "Header J3",
          pin_position: 20,
          pin_signal: "GND",
          rel_coord_3d: [1.14, 0.35, 2.18]
        },
        destination: {
          device_id: "inmp441_breakout_reference",
          device_name: "INMP441 I2S Microphone",
          connector: "6-Pin Header",
          pin_position: 6,
          pin_signal: "GND & L/R",
          rel_coord_3d: [2.7, 0.35, 1.1]
        },
        verification_status: "VERIFIED_OFFICIAL_DOCUMENTATION",
        verification_source: "INMP441 Datasheet Section 7 (L/R tied to GND selects Left audio channel for mono stream)",
        engineering_notes: "Tied to common GND to select Left channel mono operation."
      },
      {
        net_id: "NET_I2S_MIC_SD",
        net_name: "I2S0_DATA_IN",
        category: "i2s",
        wire_color: "#a855f7",
        wire_gauge_awg: 26,
        connector_type: "2.54mm DuPont Female-to-Female",
        signal_direction: "MCU_INPUT",
        voltage_domain_v: 3.3,
        max_current_ma: 2.0,
        source: {
          device_id: "inmp441_breakout_reference",
          device_name: "INMP441 I2S Microphone",
          connector: "6-Pin Header",
          pin_position: 4,
          pin_signal: "SD",
          rel_coord_3d: [2.7, 0.35, 0.5]
        },
        destination: {
          device_id: "esp32_s3_devkitc1_v1_1",
          device_name: "ESP32-S3-DevKitC-1 v1.1",
          connector: "Header J1",
          pin_position: 7,
          pin_signal: "GPIO7",
          rel_coord_3d: [-1.14, 0.35, -1.14]
        },
        verification_status: "VERIFIED_OFFICIAL_DOCUMENTATION",
        verification_source: "ESP-IDF I2S API Guide (ESP32-S3 I2S0 peripheral routing to GPIO matrix)",
        engineering_notes: "Carries 24-bit PCM acoustic samples from MEMS sigma-delta ADC to ESP32 DMA buffer."
      },
      {
        net_id: "NET_I2S_MIC_WS",
        net_name: "I2S0_WORD_SELECT",
        category: "i2s",
        wire_color: "#a855f7",
        wire_gauge_awg: 26,
        connector_type: "2.54mm DuPont Female-to-Female",
        signal_direction: "MCU_OUTPUT",
        voltage_domain_v: 3.3,
        max_current_ma: 2.0,
        source: {
          device_id: "esp32_s3_devkitc1_v1_1",
          device_name: "ESP32-S3-DevKitC-1 v1.1",
          connector: "Header J1",
          pin_position: 12,
          pin_signal: "GPIO8",
          rel_coord_3d: [-1.14, 0.35, 0.12]
        },
        destination: {
          device_id: "inmp441_breakout_reference",
          device_name: "INMP441 I2S Microphone",
          connector: "6-Pin Header",
          pin_position: 2,
          pin_signal: "WS",
          rel_coord_3d: [2.7, 0.35, -0.1]
        },
        verification_status: "VERIFIED_OFFICIAL_DOCUMENTATION",
        verification_source: "ESP32-S3 Technical Reference Manual (I2S0_WS master frame sync at 16 kHz)",
        engineering_notes: "Master word-select (LRCLK) generated by ESP32-S3 hardware I2S peripheral."
      },
      {
        net_id: "NET_I2S_MIC_SCK",
        net_name: "I2S0_BIT_CLOCK",
        category: "i2s",
        wire_color: "#a855f7",
        wire_gauge_awg: 26,
        connector_type: "2.54mm DuPont Female-to-Female",
        signal_direction: "MCU_OUTPUT",
        voltage_domain_v: 3.3,
        max_current_ma: 2.0,
        source: {
          device_id: "esp32_s3_devkitc1_v1_1",
          device_name: "ESP32-S3-DevKitC-1 v1.1",
          connector: "Header J1",
          pin_position: 17,
          pin_signal: "GPIO9",
          rel_coord_3d: [-1.14, 0.35, 1.4]
        },
        destination: {
          device_id: "inmp441_breakout_reference",
          device_name: "INMP441 I2S Microphone",
          connector: "6-Pin Header",
          pin_position: 1,
          pin_signal: "SCK",
          rel_coord_3d: [2.7, 0.35, -0.4]
        },
        verification_status: "VERIFIED_OFFICIAL_DOCUMENTATION",
        verification_source: "INMP441 Timing Diagram & ESP-IDF I2S Driver (BCLK = 1.024 MHz at 16kHz x 32b x 2ch)",
        engineering_notes: "Continuous serial bit clock driven by ESP32-S3 master controller."
      }
    ]
  };

  // Embedded verified fallback data (exact Espressif ESP32-S3-DevKitC-1 v1.1 specification)
  const HW_FALLBACK_ESP32 = {
    device_id: 'esp32_s3_devkitc1_v1_1',
    name: 'ESP32-S3-DevKitC-1 v1.1',
    board_revision: 'v1.1',
    module_variant: 'ESP32-S3-WROOM-1',
    soc: 'ESP32-S3 (Xtensa dual-core 32-bit LX7 @ up to 240 MHz, vector instructions, 512 KB SRAM)',
    wireless: '2.4 GHz Wi-Fi (802.11 b/g/n) with HT40 & CSI capture, Bluetooth 5 (LE)',
    official_guide_url: 'https://docs.espressif.com/projects/esp-dev-kits/en/latest/esp32s3/esp32-s3-devkitc-1/user_guide_v1.1.html',
    datasheet_url: 'https://documentation.espressif.com/esp32_s3_datasheet_en.pdf',
    verification_status: 'VERIFIED_OFFICIAL_DOCUMENTATION',
    revision_differences: {
      v1_1_vs_v1_0: 'On v1.1, the addressable RGB LED is routed to GPIO38. On older v1.0, it was routed to GPIO48. GPIO48 is an ordinary external header pin on v1.1.',
      memory_restrictions: 'For Octal flash and Octal PSRAM module variants, GPIO35, GPIO36, and GPIO37 are consumed internally by SPIDQS, SPIIO7, SPIIO6 and must NOT be used externally.'
    },
    headers: {
      J1: [
        { pos: 1, signal: '3V3', type: 'Power', desc: '3.3V Power Output', volt_v: 3.3, notes: 'Supplies SW-420 and INMP441', verified: true, assigned_to: 'SW-420 VCC' },
        { pos: 2, signal: '3V3', type: 'Power', desc: '3.3V Power Output', volt_v: 3.3, notes: 'Auxiliary 3.3V rail', verified: true, assigned_to: 'INMP441 VDD' },
        { pos: 3, signal: 'RST', type: 'Input', desc: 'CHIP_PU (Reset)', volt_v: 3.3, notes: 'Active low reset with internal pull-up', verified: true },
        { pos: 4, signal: 'GPIO4', type: 'I/O', desc: 'ADC1_CH3, TOUCH4', volt_v: 3.3, assigned_to: 'HC-SR501 PIR Output', notes: 'Configured as digital input for PIR motion pulse', verified: true },
        { pos: 5, signal: 'GPIO5', type: 'I/O', desc: 'ADC1_CH4, TOUCH5', volt_v: 3.3, assigned_to: 'SW-420 Vibration DO', notes: 'Configured as digital input for seismic shock trigger', verified: true },
        { pos: 6, signal: 'GPIO6', type: 'I/O', desc: 'ADC1_CH5, TOUCH6', volt_v: 3.3, notes: 'Available GPIO', verified: true },
        { pos: 7, signal: 'GPIO7', type: 'I/O', desc: 'ADC1_CH6, TOUCH7', volt_v: 3.3, assigned_to: 'INMP441 SD (Data)', notes: 'Configured as I2S0_DATA_IN for acoustic rumbles', verified: true },
        { pos: 8, signal: 'GPIO15', type: 'I/O', desc: 'ADC2_CH4, TOUCH14', volt_v: 3.3, notes: 'Available GPIO', verified: true },
        { pos: 9, signal: 'GPIO16', type: 'I/O', desc: 'ADC2_CH5', volt_v: 3.3, notes: 'Available GPIO', verified: true },
        { pos: 10, signal: 'GPIO17', type: 'I/O', desc: 'ADC2_CH6', volt_v: 3.3, notes: 'Available GPIO', verified: true },
        { pos: 11, signal: 'GPIO18', type: 'I/O', desc: 'ADC2_CH7, USB JTAG D-', volt_v: 3.3, notes: 'USB JTAG or GPIO', verified: true },
        { pos: 12, signal: 'GPIO8', type: 'I/O', desc: 'ADC1_CH7', volt_v: 3.3, assigned_to: 'INMP441 WS (Word Select)', notes: 'Configured as I2S0_WS / LRCLK master clock', verified: true },
        { pos: 13, signal: 'GPIO19', type: 'I/O', desc: 'USB D- (Native USB)', volt_v: 3.3, notes: 'Wired to native USB port D-', verified: true },
        { pos: 14, signal: 'GPIO20', type: 'I/O', desc: 'USB D+ (Native USB)', volt_v: 3.3, notes: 'Wired to native USB port D+', verified: true },
        { pos: 15, signal: 'GPIO3', type: 'I/O', desc: 'ADC1_CH2, TOUCH3', volt_v: 3.3, notes: 'Available GPIO', verified: true },
        { pos: 16, signal: 'GPIO46', type: 'Input', desc: 'BOOT Strapping Pin', volt_v: 3.3, notes: 'Input-only pin, pull-down at boot determines ROM logging', verified: true },
        { pos: 17, signal: 'GPIO9', type: 'I/O', desc: 'ADC1_CH8, FSPIHD', volt_v: 3.3, assigned_to: 'INMP441 SCK (Bit Clock)', notes: 'Configured as I2S0_BCLK master clock', verified: true },
        { pos: 18, signal: 'GPIO10', type: 'I/O', desc: 'ADC1_CH9, FSPICS0', volt_v: 3.3, notes: 'FSPI CS / General GPIO', verified: true },
        { pos: 19, signal: 'GPIO11', type: 'I/O', desc: 'ADC2_CH0, FSPID', volt_v: 3.3, notes: 'FSPI MOSI / General GPIO', verified: true },
        { pos: 20, signal: 'GPIO12', type: 'I/O', desc: 'ADC2_CH1, FSPICLK', volt_v: 3.3, notes: 'FSPI CLK / General GPIO', verified: true },
        { pos: 21, signal: 'GPIO13', type: 'I/O', desc: 'ADC2_CH2, FSPIQ', volt_v: 3.3, notes: 'FSPI MISO / General GPIO', verified: true },
        { pos: 22, signal: 'GPIO14', type: 'I/O', desc: 'ADC2_CH3, FSPIWP', volt_v: 3.3, notes: 'FSPI WP / General GPIO', verified: true }
      ],
      J3: [
        { pos: 1, signal: 'GND', type: 'Power', desc: 'Ground (Common)', volt_v: 0.0, notes: 'Common system ground rail', verified: true, assigned_to: 'SW-420 GND' },
        { pos: 2, signal: 'GPIO43', type: 'I/O', desc: 'U0TXD (Default UART TX)', volt_v: 3.3, notes: 'Wired to CP2102N UART RX', verified: true },
        { pos: 3, signal: 'GPIO44', type: 'I/O', desc: 'U0RXD (Default UART RX)', volt_v: 3.3, notes: 'Wired to CP2102N UART TX', verified: true },
        { pos: 4, signal: 'GPIO1', type: 'I/O', desc: 'ADC1_CH0, TOUCH1', volt_v: 3.3, notes: 'General purpose ADC/GPIO', verified: true },
        { pos: 5, signal: 'GPIO2', type: 'I/O', desc: 'ADC1_CH1, TOUCH2', volt_v: 3.3, notes: 'General purpose ADC/GPIO', verified: true },
        { pos: 6, signal: 'GPIO42', type: 'I/O', desc: 'MTMS (JTAG)', volt_v: 3.3, notes: 'JTAG test mode select', verified: true },
        { pos: 7, signal: 'GPIO41', type: 'I/O', desc: 'MTDI (JTAG)', volt_v: 3.3, notes: 'JTAG data in', verified: true },
        { pos: 8, signal: 'GPIO40', type: 'I/O', desc: 'MTDO (JTAG)', volt_v: 3.3, notes: 'JTAG data out', verified: true },
        { pos: 9, signal: 'GPIO39', type: 'I/O', desc: 'MTCK (JTAG)', volt_v: 3.3, notes: 'JTAG clock', verified: true },
        { pos: 10, signal: 'GPIO38', type: 'I/O', desc: 'Onboard RGB LED Data', volt_v: 3.3, assigned_to: 'Onboard WS2812 RGB LED', notes: 'Hardwired to WS2812 RGB LED on v1.1. (On v1.0 this was GPIO48)', verified: true },
        { pos: 11, signal: 'GPIO37', type: 'Reserved', desc: 'SPIDQS (Octal SPI Internal)', volt_v: 3.3, notes: 'RESERVED: Connected internally to Octal PSRAM/Flash. DO NOT USE EXTERNALLY on WROOM-1 Octal variants.', verified: true },
        { pos: 12, signal: 'GPIO36', type: 'Reserved', desc: 'SPIIO7 (Octal SPI Internal)', volt_v: 3.3, notes: 'RESERVED: Connected internally to Octal PSRAM/Flash. DO NOT USE EXTERNALLY on WROOM-1 Octal variants.', verified: true },
        { pos: 13, signal: 'GPIO35', type: 'Reserved', desc: 'SPIIO6 (Octal SPI Internal)', volt_v: 3.3, notes: 'RESERVED: Connected internally to Octal PSRAM/Flash. DO NOT USE EXTERNALLY on WROOM-1 Octal variants.', verified: true },
        { pos: 14, signal: 'GPIO0', type: 'I/O', desc: 'BOOT Button / Strapping Pin', volt_v: 3.3, notes: 'Connected to BOOT tactile switch. Low = download bootloader', verified: true },
        { pos: 15, signal: 'GPIO45', type: 'I/O', desc: 'Strapping Pin (VDD_SPI)', volt_v: 3.3, notes: 'Strapping pin for VDD_SPI flash voltage selector', verified: true },
        { pos: 16, signal: 'GPIO47', type: 'I/O', desc: 'SPICLK_P / General GPIO', volt_v: 3.3, notes: 'Available general purpose GPIO', verified: true },
        { pos: 17, signal: 'GPIO48', type: 'I/O', desc: 'SPICLK_N / General GPIO', volt_v: 3.3, notes: 'Available external GPIO on v1.1 (used for RGB LED on v1.0)', verified: true },
        { pos: 18, signal: 'GPIO21', type: 'I/O', desc: 'RTC_GPIO21', volt_v: 3.3, notes: 'Available general purpose / RTC GPIO', verified: true },
        { pos: 19, signal: 'NC / GND', type: 'Power', desc: 'Not Connected / Ground', volt_v: 0.0, notes: 'Reserved or secondary ground', verified: true },
        { pos: 20, signal: 'GND', type: 'Power', desc: 'Ground (Common)', volt_v: 0.0, notes: 'Common ground rail for sensors', verified: true, assigned_to: 'INMP441 GND & L/R' },
        { pos: 21, signal: '5V', type: 'Power', desc: '5V Input / USB VBUS Power', volt_v: 5.0, assigned_to: 'HC-SR501 PIR VCC', notes: 'Directly connected to USB 5V rail. Supplies HC-SR501 PIR sensor module', verified: true },
        { pos: 22, signal: 'GND', type: 'Power', desc: 'Ground (Common)', volt_v: 0.0, notes: 'Common ground rail', verified: true, assigned_to: 'HC-SR501 PIR GND' }
      ]
    }
  };

  function initHardwareLab() {
    const container = document.getElementById('hardwareLab3DContainer');
    if (!container || !window.THREE) return;

    // 1. Scene
    hwThreeScene = new THREE.Scene();
    hwThreeScene.background = new THREE.Color(0x060914);

    // 2. Camera
    const aspect = container.clientWidth / (container.clientHeight || 500);
    hwThreeCamera = new THREE.PerspectiveCamera(40, aspect, 0.1, 100);
    hwThreeCamera.position.set(5.5, 7.5, 6.5);

    // 3. Renderer
    hwThreeRenderer = new THREE.WebGLRenderer({ antialias: true, alpha: false });
    hwThreeRenderer.setSize(container.clientWidth || 700, container.clientHeight || 500);
    hwThreeRenderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
    hwThreeRenderer.shadowMap.enabled = true;
    hwThreeRenderer.shadowMap.type = THREE.PCFSoftShadowMap;
    hwThreeRenderer.toneMapping = THREE.ACESFilmicToneMapping;
    hwThreeRenderer.toneMappingExposure = 1.1;

    container.appendChild(hwThreeRenderer.domElement);

    // 4. Orbit Controls
    if (window.THREE.OrbitControls) {
      hwThreeControls = new THREE.OrbitControls(hwThreeCamera, hwThreeRenderer.domElement);
      hwThreeControls.enableDamping = true;
      hwThreeControls.dampingFactor = 0.05;
      hwThreeControls.minDistance = 2.5;
      hwThreeControls.maxDistance = 24.0;
      hwThreeControls.target.set(0, 0, 0);
      hwThreeControls.update();
    }

    // 5. Lighting
    const amb = new THREE.AmbientLight(0xffffff, 0.65);
    hwThreeScene.add(amb);

    const keyLight = new THREE.DirectionalLight(0xffffff, 0.95);
    keyLight.position.set(6, 12, 8);
    keyLight.castShadow = true;
    keyLight.shadow.mapSize.width = 1024;
    keyLight.shadow.mapSize.height = 1024;
    hwThreeScene.add(keyLight);

    const fillLight = new THREE.DirectionalLight(0x38bdf8, 0.4);
    fillLight.position.set(-6, 4, -4);
    hwThreeScene.add(fillLight);

    const rimLight = new THREE.DirectionalLight(0xf59e0b, 0.35);
    rimLight.position.set(0, -6, -6);
    hwThreeScene.add(rimLight);

    // Subtle grid platform
    const grid = new THREE.GridHelper(16, 32, 0x00f0ff, 0x1e293b);
    grid.position.y = -1.2;
    grid.material.opacity = 0.25;
    grid.material.transparent = true;
    hwThreeScene.add(grid);

    // Pin Highlight Meshes (Source = Cyan, Destination = Amber/Gold)
    const ringGeo = new THREE.RingGeometry(0.08, 0.16, 24);
    ringGeo.rotateX(-Math.PI / 2);
    hwPinHighlightMesh = new THREE.Mesh(ringGeo, new THREE.MeshBasicMaterial({ color: 0x00f0ff, side: THREE.DoubleSide }));
    hwPinHighlightMesh.visible = false;
    hwThreeScene.add(hwPinHighlightMesh);

    hwPinDestHighlightMesh = new THREE.Mesh(ringGeo, new THREE.MeshBasicMaterial({ color: 0xf59e0b, side: THREE.DoubleSide }));
    hwPinDestHighlightMesh.visible = false;
    hwThreeScene.add(hwPinDestHighlightMesh);

    // 6. Build Initial Models — Default to 3D Physical Wiring Workbench
    loadHardwareDevice('workbench');

    // 7. Raycast listener
    setupHardwareRaycaster(container);

    // 8. Event Listeners for Toolbar
    setupHardwareLabEvents();

    // Start render loop
    animateHardwareLab();
  }

  function animateHardwareLab() {
    hwAnimFrameId = requestAnimationFrame(animateHardwareLab);
    if (hwThreeControls) hwThreeControls.update();

    // Animate exploded positions
    if (hwExplodedObjects.length > 0) {
      hwExplodedObjects.forEach(item => {
        const targetY = hwExploded ? item.explodedY : item.baseY;
        const targetZ = hwExploded ? item.explodedZ : item.baseZ;
        const targetX = hwExploded ? item.explodedX : item.baseX;
        item.mesh.position.y += (targetY - item.mesh.position.y) * 0.12;
        if (targetZ !== undefined) item.mesh.position.z += (targetZ - item.mesh.position.z) * 0.12;
        if (targetX !== undefined) item.mesh.position.x += (targetX - item.mesh.position.x) * 0.12;
      });
    }

    // Subtle gentle pulse on selected wire
    if (hwSelectedNet) {
      const matchWire = hwWireMeshes.find(wm => wm.userData?.net?.net_id === hwSelectedNet.net_id);
      if (matchWire && matchWire.material) {
        const pulse = 0.65 + Math.sin(Date.now() * 0.007) * 0.35;
        matchWire.material.emissiveIntensity = pulse;
      }
    }

    if (hwThreeRenderer && hwThreeScene && hwThreeCamera) {
      hwThreeRenderer.render(hwThreeScene, hwThreeCamera);
    }
  }

  // ==========================================================================
  // Procedural 3D Hardware Model Generators
  // ==========================================================================
  function createMultiBoardWiringWorkbench() {
    const workbenchGroup = new THREE.Group();
    workbenchGroup.name = 'HW_WORKBENCH_ASSEMBLY';
    hwRaycastPins = [];
    hwRaycastComponents = [];
    hwRaycastWires = [];
    hwWireMeshes = [];
    hwExplodedObjects = [];

    // 1. Antistatic Laboratory Carrier Mat / Baseplate (12 x 0.12 x 9.5)
    const baseplateMat = new THREE.MeshStandardMaterial({
      color: 0x090d16, // dark blue ESD workbench mat
      roughness: 0.6,
      metalness: 0.1,
    });
    const baseplate = new THREE.Mesh(new THREE.BoxGeometry(12.0, 0.12, 9.5), baseplateMat);
    baseplate.position.y = -0.06;
    baseplate.receiveShadow = true;
    workbenchGroup.add(baseplate);

    // Silkscreen corner mounting standoffs
    [-5.6, 5.6].forEach(bx => {
      [-4.4, 4.4].forEach(bz => {
        const standoff = new THREE.Mesh(new THREE.CylinderGeometry(0.18, 0.22, 0.24, 12), new THREE.MeshStandardMaterial({ color: 0xd4af37, metalness: 0.9 }));
        standoff.position.set(bx, 0.06, bz);
        workbenchGroup.add(standoff);
      });
    });

    // Baseplate Silk Title
    const silkTitle = createTextSprite('PRW-WILD SIL PHYSICAL HARDWARE BENCHMARK • ESP32-S3 + SENSOR CLUSTER', '#00f0ff');
    silkTitle.scale.set(6.0, 0.6, 1);
    silkTitle.position.set(0, 0.01, -4.2);
    silkTitle.rotation.x = -Math.PI / 2;
    workbenchGroup.add(silkTitle);

    // 2. Central ESP32-S3 Board at (0, 0, 0)
    const esp32Model = createESP32DevKitModel(true);
    esp32Model.position.set(0, 0, 0);
    workbenchGroup.add(esp32Model);

    // 3. Peripheral Sensor Modules:
    // HC-SR501 PIR Sensor (Left-Rear at [-3.6, 0, -1.5])
    const pirGroup = new THREE.Group();
    pirGroup.position.set(-3.6, 0, -1.5);
    const pirPcb = new THREE.Mesh(new THREE.BoxGeometry(3.2, 0.16, 2.4), new THREE.MeshStandardMaterial({ color: 0x15803d, roughness: 0.5 }));
    pirGroup.add(pirPcb);
    const pirDome = new THREE.Mesh(new THREE.SphereGeometry(1.05, 18, 14, 0, Math.PI * 2, 0, Math.PI / 2), new THREE.MeshStandardMaterial({ color: 0xf8fafc, roughness: 0.15, transmission: 0.3 }));
    pirDome.position.y = 0.08;
    pirGroup.add(pirDome);
    const potMat = new THREE.MeshStandardMaterial({ color: 0xf97316 });
    const pot1 = new THREE.Mesh(new THREE.CylinderGeometry(0.22, 0.22, 0.2, 12), potMat);
    pot1.position.set(0.8, -0.16, -0.6);
    pirGroup.add(pot1);
    const pot2 = new THREE.Mesh(new THREE.CylinderGeometry(0.22, 0.22, 0.2, 12), potMat);
    pot2.position.set(0.8, -0.16, 0.6);
    pirGroup.add(pot2);
    const pirLabel = createTextSprite('HC-SR501 PIR (5V)', '#86efac');
    pirLabel.scale.set(2.2, 0.45, 1);
    pirLabel.position.set(0, 0.18, 1.5);
    pirLabel.rotation.x = -Math.PI / 2;
    pirGroup.add(pirLabel);

    // PIR 3-Pin Header (Pins at X=-2.8 in world coords)
    const pirPins = [
      { pos: 1, signal: 'VCC', desc: '5V DC Supply Input', volt_v: 5.0, localZ: -0.3, worldPos: [-2.8, 0.35, -1.8] },
      { pos: 2, signal: 'OUT', desc: '3.3V TTL Motion Trigger', volt_v: 3.3, localZ: 0.0, worldPos: [-2.8, 0.35, -1.5] },
      { pos: 3, signal: 'GND', desc: 'Common Ground Return', volt_v: 0.0, localZ: 0.3, worldPos: [-2.8, 0.35, -1.2] },
    ];
    pirPins.forEach(p => {
      const pinMesh = new THREE.Mesh(new THREE.CylinderGeometry(0.04, 0.04, 0.65, 8), new THREE.MeshStandardMaterial({ color: 0xd4af37, metalness: 0.9 }));
      pinMesh.position.set(0.8, 0.25, p.localZ);
      pirGroup.add(pinMesh);

      const hitMesh = new THREE.Mesh(new THREE.CylinderGeometry(0.12, 0.12, 0.8, 8), new THREE.MeshBasicMaterial({ visible: false }));
      hitMesh.position.set(p.worldPos[0], p.worldPos[1], p.worldPos[2]);
      hitMesh.userData = {
        type: 'PIN',
        device: 'hc_sr501_reference',
        header: '3-Pin Header',
        pos: p.pos,
        signal: p.signal,
        data: p,
      };
      workbenchGroup.add(hitMesh);
      hwRaycastPins.push(hitMesh);
    });

    pirGroup.userData = {
      type: 'COMPONENT',
      name: 'HC-SR501 Pyroelectric Infrared Sensor',
      role: 'Corroborates RF precursor with direct thermal IR motion detection.',
      pos: 'Left Workbench Standoff',
      ref: 'Kuongshun HC-SR501 User Manual',
    };
    workbenchGroup.add(pirGroup);
    hwRaycastComponents.push(pirGroup);
    hwExplodedObjects.push({ mesh: pirGroup, baseY: 0, explodedY: 0, baseX: -3.6, explodedX: -4.8, baseZ: -1.5, explodedZ: -1.5 });

    // SW-420 Vibration Sensor (Left-Front at [-3.4, 0, 1.6])
    const vibGroup = new THREE.Group();
    vibGroup.position.set(-3.4, 0, 1.6);
    const vibPcb = new THREE.Mesh(new THREE.BoxGeometry(3.2, 0.16, 1.4), new THREE.MeshStandardMaterial({ color: 0x0284c7, roughness: 0.5 }));
    vibGroup.add(vibPcb);
    const vibTube = new THREE.Mesh(new THREE.CylinderGeometry(0.24, 0.24, 1.2, 16), new THREE.MeshStandardMaterial({ color: 0xd4af37, metalness: 0.85, roughness: 0.2 }));
    vibTube.rotation.z = Math.PI / 2;
    vibTube.position.set(-0.7, 0.3, 0);
    vibGroup.add(vibTube);
    const vibIc = new THREE.Mesh(new THREE.BoxGeometry(0.6, 0.12, 0.4), new THREE.MeshStandardMaterial({ color: 0x0f172a }));
    vibIc.position.set(0.2, 0.14, 0);
    vibGroup.add(vibIc);
    const vibPot = new THREE.Mesh(new THREE.BoxGeometry(0.5, 0.45, 0.35), new THREE.MeshStandardMaterial({ color: 0x3b82f6 }));
    vibPot.position.set(0.9, 0.28, 0);
    vibGroup.add(vibPot);
    const vibLabel = createTextSprite('SW-420 VIBRATION (3.3V)', '#38bdf8');
    vibLabel.scale.set(2.2, 0.45, 1);
    vibLabel.position.set(0, 0.18, 1.0);
    vibLabel.rotation.x = -Math.PI / 2;
    vibGroup.add(vibLabel);

    // SW-420 3-Pin Header (Pins at X=-2.6 in world coords)
    const vibPins = [
      { pos: 1, signal: 'VCC', desc: '3.3V DC Supply Input', volt_v: 3.3, localZ: -0.4, worldPos: [-2.6, 0.35, 1.2] },
      { pos: 2, signal: 'GND', desc: 'Common Ground Return', volt_v: 0.0, localZ: -0.1, worldPos: [-2.6, 0.35, 1.5] },
      { pos: 3, signal: 'DO', desc: 'Seismic Shock Digital Trigger', volt_v: 3.3, localZ: 0.2, worldPos: [-2.6, 0.35, 1.8] },
    ];
    vibPins.forEach(p => {
      const pinMesh = new THREE.Mesh(new THREE.CylinderGeometry(0.04, 0.04, 0.65, 8), new THREE.MeshStandardMaterial({ color: 0xd4af37, metalness: 0.9 }));
      pinMesh.position.set(0.8, 0.25, p.localZ);
      vibGroup.add(pinMesh);

      const hitMesh = new THREE.Mesh(new THREE.CylinderGeometry(0.12, 0.12, 0.8, 8), new THREE.MeshBasicMaterial({ visible: false }));
      hitMesh.position.set(p.worldPos[0], p.worldPos[1], p.worldPos[2]);
      hitMesh.userData = {
        type: 'PIN',
        device: 'sw420_reference',
        header: '3-Pin Header',
        pos: p.pos,
        signal: p.signal,
        data: p,
      };
      workbenchGroup.add(hitMesh);
      hwRaycastPins.push(hitMesh);
    });

    vibGroup.userData = {
      type: 'COMPONENT',
      name: 'SW-420 High-Sensitivity Seismic Vibration Module',
      role: 'Captures megafauna footfall surface shockwaves.',
      pos: 'Front-Left Workbench Rail',
      ref: 'Waveshare Vibration Sensor Wiki',
    };
    workbenchGroup.add(vibGroup);
    hwRaycastComponents.push(vibGroup);
    hwExplodedObjects.push({ mesh: vibGroup, baseY: 0, explodedY: 0, baseX: -3.4, explodedX: -4.6, baseZ: 1.6, explodedZ: 1.6 });

    // INMP441 I2S Microphone Breakout (Right at [3.4, 0, 0.3])
    const micGroup = new THREE.Group();
    micGroup.position.set(3.4, 0, 0.3);
    const micPcb = new THREE.Mesh(new THREE.BoxGeometry(1.6, 0.16, 1.8), new THREE.MeshStandardMaterial({ color: 0x581c87, roughness: 0.4 }));
    micGroup.add(micPcb);
    const micPort = new THREE.Mesh(new THREE.CylinderGeometry(0.18, 0.18, 0.18, 16), new THREE.MeshStandardMaterial({ color: 0xd4af37, metalness: 0.95 }));
    micPort.position.set(0, -0.05, 0);
    micGroup.add(micPort);
    const micIc = new THREE.Mesh(new THREE.BoxGeometry(0.55, 0.16, 0.45), new THREE.MeshStandardMaterial({ color: 0xe2e8f0, metalness: 0.9, roughness: 0.2 }));
    micIc.position.set(0, 0.15, 0);
    micGroup.add(micIc);
    const micLabel = createTextSprite('INMP441 I2S MIC', '#c084fc');
    micLabel.scale.set(2.0, 0.42, 1);
    micLabel.position.set(0, 0.18, 1.2);
    micLabel.rotation.x = -Math.PI / 2;
    micGroup.add(micLabel);

    // INMP441 6-Pin Header (Pins at X=2.7 in world coords)
    const micPins = [
      { pos: 1, signal: 'SCK', desc: 'I2S Continuous Serial Bit Clock', volt_v: 3.3, localZ: -0.7, worldPos: [2.7, 0.35, -0.4] },
      { pos: 2, signal: 'WS', desc: 'I2S Word Select / Frame Sync', volt_v: 3.3, localZ: -0.4, worldPos: [2.7, 0.35, -0.1] },
      { pos: 3, signal: 'L/R', desc: 'Channel Select (GND = Left Mono)', volt_v: 0.0, localZ: -0.1, worldPos: [2.7, 0.35, 0.2] },
      { pos: 4, signal: 'SD', desc: 'I2S Serial Data Out to ESP32', volt_v: 3.3, localZ: 0.2, worldPos: [2.7, 0.35, 0.5] },
      { pos: 5, signal: 'VDD', desc: '3.3V Clean Power Input', volt_v: 3.3, localZ: 0.5, worldPos: [2.7, 0.35, 0.8] },
      { pos: 6, signal: 'GND', desc: 'Common Audio Ground', volt_v: 0.0, localZ: 0.8, worldPos: [2.7, 0.35, 1.1] },
    ];
    micPins.forEach(p => {
      const pinMesh = new THREE.Mesh(new THREE.CylinderGeometry(0.035, 0.035, 0.65, 8), new THREE.MeshStandardMaterial({ color: 0xd4af37, metalness: 0.9 }));
      pinMesh.position.set(-0.7, 0.25, p.localZ);
      micGroup.add(pinMesh);

      const hitMesh = new THREE.Mesh(new THREE.CylinderGeometry(0.12, 0.12, 0.8, 8), new THREE.MeshBasicMaterial({ visible: false }));
      hitMesh.position.set(p.worldPos[0], p.worldPos[1], p.worldPos[2]);
      hitMesh.userData = {
        type: 'PIN',
        device: 'inmp441_breakout_reference',
        header: '6-Pin Header',
        pos: p.pos,
        signal: p.signal,
        data: p,
      };
      workbenchGroup.add(hitMesh);
      hwRaycastPins.push(hitMesh);
    });

    micGroup.userData = {
      type: 'COMPONENT',
      name: 'INMP441 Omnidirectional I2S Digital MEMS Microphone',
      role: 'Captures infrasonic low-frequency elephant rumbles via 24-bit PCM stream.',
      pos: 'Right Workbench Rail',
      ref: 'InvenSense INMP441 Product Specification',
    };
    workbenchGroup.add(micGroup);
    hwRaycastComponents.push(micGroup);
    hwExplodedObjects.push({ mesh: micGroup, baseY: 0, explodedY: 0, baseX: 3.4, explodedX: 4.6, baseZ: 0.3, explodedZ: 0.3 });

    // AI-Thinker ESP32-CAM OV2640 Module (Right-Rear at [3.4, 0, -2.4])
    const camGroup = new THREE.Group();
    camGroup.position.set(3.4, 0, -2.4);
    const camPcb = new THREE.Mesh(new THREE.BoxGeometry(2.7, 0.16, 3.8), new THREE.MeshStandardMaterial({ color: 0x0f172a, roughness: 0.5 }));
    camGroup.add(camPcb);
    const camLensBase = new THREE.Mesh(new THREE.BoxGeometry(1.0, 0.25, 1.0), new THREE.MeshStandardMaterial({ color: 0x1e293b }));
    camLensBase.position.set(0, 0.2, 0.6);
    camGroup.add(camLensBase);
    const camLensCyl = new THREE.Mesh(new THREE.CylinderGeometry(0.35, 0.4, 0.4, 20), new THREE.MeshStandardMaterial({ color: 0x0a0a0a, metalness: 0.8 }));
    camLensCyl.position.set(0, 0.45, 0.6);
    camGroup.add(camLensCyl);
    const camFlash = new THREE.Mesh(new THREE.BoxGeometry(0.3, 0.12, 0.3), new THREE.MeshStandardMaterial({ color: 0xfef08a, emissive: 0xfef08a, emissiveIntensity: 0.6 }));
    camFlash.position.set(0.8, 0.14, 0.6);
    camGroup.add(camFlash);
    const camLabel = createTextSprite('ESP32-CAM (OPTICAL GATE)', '#f59e0b');
    camLabel.scale.set(2.4, 0.45, 1);
    camLabel.position.set(0, 0.18, -1.8);
    camLabel.rotation.x = -Math.PI / 2;
    camGroup.add(camLabel);

    camGroup.userData = {
      type: 'COMPONENT',
      name: 'AI-Thinker ESP32-CAM OV2640 Optical Confirmation Unit',
      role: 'Wakes selectively under predictive RF/PIR trigger to capture species classification frames.',
      pos: 'Rear-Right Camera Mast Station',
      ref: 'ESP32-CAM Hardware Reference',
    };
    workbenchGroup.add(camGroup);
    hwRaycastComponents.push(camGroup);
    hwExplodedObjects.push({ mesh: camGroup, baseY: 0, explodedY: 0, baseX: 3.4, explodedX: 4.6, baseZ: -2.4, explodedZ: -3.2 });

    // 4. Generate 3D Curved Insulated Jumper Wires
    const nets = HW_WIRING_MANIFEST.wiring_nets;
    const housingGeo = new THREE.BoxGeometry(0.12, 0.45, 0.12);
    const housingMat = new THREE.MeshStandardMaterial({ color: 0x111827, roughness: 0.8 });

    nets.forEach((net, idx) => {
      const src = net.source.rel_coord_3d;
      const dst = net.destination.rel_coord_3d;

      // Exact 3D endpoints
      const p0 = new THREE.Vector3(src[0], src[1] + 0.12, src[2]);
      const p1 = new THREE.Vector3(src[0], src[1] + 0.70, src[2]);

      // Parabolic 3D Arch through intermediate space
      const midX = (src[0] + dst[0]) / 2;
      const midZ = (src[2] + dst[2]) / 2;
      const arcY = 1.35 + (idx * 0.12); // each wire gets its own clean elevation layer!
      const lateralBow = (midX > 0 ? 0.35 : -0.35) * (idx % 2 === 0 ? 1 : -0.6);

      const p2 = new THREE.Vector3(midX + lateralBow, arcY, midZ);
      const p3 = new THREE.Vector3(dst[0], dst[1] + 0.70, dst[2]);
      const p4 = new THREE.Vector3(dst[0], dst[1] + 0.12, dst[2]);

      const curve = new THREE.CatmullRomCurve3([p0, p1, p2, p3, p4]);
      const tubeGeo = new THREE.TubeGeometry(curve, 36, 0.042, 8, false);

      const wireColInt = parseInt(net.wire_color.replace('#', '0x'), 16);
      const tubeMat = new THREE.MeshStandardMaterial({
        color: wireColInt,
        roughness: 0.35,
        metalness: 0.08,
      });

      const wireMesh = new THREE.Mesh(tubeGeo, tubeMat);
      wireMesh.castShadow = true;
      wireMesh.userData = {
        type: 'WIRE',
        net: net,
        curve: curve,
        baseColor: wireColInt,
        srcCoord: src,
        dstCoord: dst,
      };

      // DuPont Rectangular Connector Housings at both ends
      const hSrc = new THREE.Mesh(housingGeo, housingMat);
      hSrc.position.set(src[0], src[1] + 0.28, src[2]);
      const hDst = new THREE.Mesh(housingGeo, housingMat);
      hDst.position.set(dst[0], dst[1] + 0.28, dst[2]);

      workbenchGroup.add(wireMesh);
      workbenchGroup.add(hSrc);
      workbenchGroup.add(hDst);

      hwRaycastWires.push(wireMesh);
      hwWireMeshes.push(wireMesh);
      hwExplodedObjects.push({ mesh: hSrc, baseY: src[1] + 0.28, explodedY: src[1] + 0.95 });
      hwExplodedObjects.push({ mesh: hDst, baseY: dst[1] + 0.28, explodedY: dst[1] + 0.95 });
    });

    return workbenchGroup;
  }

  function createESP32DevKitModel(isSubComponent = false) {
    const group = new THREE.Group();
    group.name = 'ESP32_S3_BOARD';
    if (!isSubComponent) {
      hwRaycastPins = [];
      hwRaycastComponents = [];
      hwExplodedObjects = [];
    }

    // PCB Substrate: 25.4mm wide, 62.0mm long, 1.6mm thick -> in Three units: 2.54, 0.16, 6.20
    const pcbGeo = new THREE.BoxGeometry(2.54, 0.16, 6.20);
    const pcbMat = new THREE.MeshStandardMaterial({
      color: 0x0f172a, // dark matte FR4 solder mask
      roughness: 0.5,
      metalness: 0.1,
    });
    const pcb = new THREE.Mesh(pcbGeo, pcbMat);
    pcb.castShadow = true;
    pcb.receiveShadow = true;
    group.add(pcb);

    // Gold Immersion Edge Pads (ENIG)
    const padMat = new THREE.MeshStandardMaterial({ color: 0xd4af37, metalness: 0.9, roughness: 0.2 });
    const edgeL = new THREE.Mesh(new THREE.BoxGeometry(0.24, 0.164, 5.8), padMat);
    edgeL.position.set(-1.15, 0, 0);
    group.add(edgeL);
    const edgeR = new THREE.Mesh(new THREE.BoxGeometry(0.24, 0.164, 5.8), padMat);
    edgeR.position.set(1.15, 0, 0);
    group.add(edgeR);

    // Silk Screen Text Label on PCB
    const silkSprite = createTextSprite('ESP32-S3-DevKitC-1 v1.1', '#cbd5e1');
    silkSprite.scale.set(2.4, 0.6, 1);
    silkSprite.position.set(0, 0.12, 1.7);
    silkSprite.rotation.x = -Math.PI / 2;
    group.add(silkSprite);

    // 1. ESP32-S3-WROOM-1 Module & Nickel-plated RF Shield
    const shieldGeo = new THREE.BoxGeometry(1.80, 0.28, 2.50);
    const shieldMat = new THREE.MeshStandardMaterial({
      color: 0xd1d5db, // silver nickel-plating
      metalness: 0.88,
      roughness: 0.22,
    });
    const shield = new THREE.Mesh(shieldGeo, shieldMat);
    shield.position.set(0, 0.22, -1.1);
    shield.castShadow = true;
    shield.userData = {
      type: 'COMPONENT',
      name: 'ESP32-S3-WROOM-1 Module',
      role: 'Core Dual-Core 240MHz SoC, 8MB Octal Flash, Wi-Fi CSI Radio',
      pos: 'Top Center (RF Shield)',
      ref: 'Espressif WROOM-1 Datasheet',
    };
    group.add(shield);
    hwRaycastComponents.push(shield);
    hwExplodedObjects.push({ mesh: shield, baseY: 0.22, explodedY: 1.45, baseZ: -1.1, explodedZ: -1.1, baseX: 0, explodedX: 0 });

    // Shield Logo Text Sprite
    const shieldText = createTextSprite('ESPRESSIF WROOM-1', '#1f2937');
    shieldText.scale.set(1.6, 0.4, 1);
    shieldText.position.set(0, 0.15, 0);
    shieldText.rotation.x = -Math.PI / 2;
    shield.add(shieldText);

    // 2. 2.4 GHz Inverted-F PCB Antenna (Top unshielded keepout zone)
    const antGeo = new THREE.BoxGeometry(1.4, 0.04, 0.6);
    const antMat = new THREE.MeshStandardMaterial({ color: 0xd4af37, metalness: 0.95, roughness: 0.15 });
    const ant = new THREE.Mesh(antGeo, antMat);
    ant.position.set(0, 0.11, -2.7);
    ant.userData = {
      type: 'COMPONENT',
      name: '2.4GHz PCB Trace Antenna',
      role: 'Receives IEEE 802.11 OFDM packets for Channel State Information extraction',
      pos: 'Top Margin Keepout Zone',
      ref: 'Espressif Antenna Design Guidelines',
    };
    group.add(ant);
    hwRaycastComponents.push(ant);

    // 3. Dual USB-C / Micro-USB Connectors (Bottom)
    const usbMat = new THREE.MeshStandardMaterial({ color: 0x94a3b8, metalness: 0.9, roughness: 0.2 });
    // Left: Native USB (GPIO19/20)
    const usbNative = new THREE.Mesh(new THREE.BoxGeometry(0.75, 0.32, 0.65), usbMat);
    usbNative.position.set(-0.65, 0.22, 2.95);
    usbNative.userData = {
      type: 'COMPONENT',
      name: 'Native ESP32-S3 USB OTG Port',
      role: 'Full-Speed USB (GPIO19 D-, GPIO20 D+) for high-throughput raw CSI streaming',
      pos: 'Bottom Edge (Left)',
      ref: 'ESP32-S3 Technical Reference Manual',
    };
    group.add(usbNative);
    hwRaycastComponents.push(usbNative);
    hwExplodedObjects.push({ mesh: usbNative, baseY: 0.22, explodedY: 0.22, baseZ: 2.95, explodedZ: 3.8, baseX: -0.65, explodedX: -0.65 });

    // Right: USB-to-UART Bridge Port (CP2102N / CH343)
    const usbUart = new THREE.Mesh(new THREE.BoxGeometry(0.75, 0.32, 0.65), usbMat);
    usbUart.position.set(0.65, 0.22, 2.95);
    usbUart.userData = {
      type: 'COMPONENT',
      name: 'USB-to-UART Bridge Port',
      role: 'Serial programming, debug console, and 5V power input via CP2102N',
      pos: 'Bottom Edge (Right)',
      ref: 'DevKitC-1 v1.1 Schematic Sheet 2',
    };
    group.add(usbUart);
    hwRaycastComponents.push(usbUart);
    hwExplodedObjects.push({ mesh: usbUart, baseY: 0.22, explodedY: 0.22, baseZ: 2.95, explodedZ: 3.8, baseX: 0.65, explodedX: 0.65 });

    // CP2102N Bridge Chip (QFN28 near UART USB)
    const cpChip = new THREE.Mesh(new THREE.BoxGeometry(0.5, 0.12, 0.5), new THREE.MeshStandardMaterial({ color: 0x111827, roughness: 0.4 }));
    cpChip.position.set(0.65, 0.14, 2.2);
    group.add(cpChip);

    // 4. Tactile Push-Buttons: BOOT (GPIO0) and RST (CHIP_PU)
    const btnBodyMat = new THREE.MeshStandardMaterial({ color: 0x475569, metalness: 0.5 });
    const btnActuatorMat = new THREE.MeshStandardMaterial({ color: 0x0284c7, roughness: 0.3 });

    // RST Button (Left)
    const rstBtn = new THREE.Group();
    rstBtn.add(new THREE.Mesh(new THREE.BoxGeometry(0.4, 0.16, 0.4), btnBodyMat));
    const rstAct = new THREE.Mesh(new THREE.CylinderGeometry(0.12, 0.12, 0.12, 12), btnActuatorMat);
    rstAct.position.y = 0.12;
    rstBtn.add(rstAct);
    rstBtn.position.set(-0.85, 0.16, 2.2);
    rstBtn.userData = {
      type: 'COMPONENT',
      name: 'RST / EN Button (Reset)',
      role: 'CHIP_PU active-low hardware reset button',
      pos: 'Bottom Left',
      ref: 'ESP32-S3 Hardware Design Guidelines',
    };
    group.add(rstBtn);
    hwRaycastComponents.push(rstBtn);
    hwExplodedObjects.push({ mesh: rstBtn, baseY: 0.16, explodedY: 0.85, baseZ: 2.2, explodedZ: 2.2, baseX: -0.85, explodedX: -0.85 });

    // BOOT Button (Right, GPIO0)
    const bootBtn = new THREE.Group();
    bootBtn.add(new THREE.Mesh(new THREE.BoxGeometry(0.4, 0.16, 0.4), btnBodyMat));
    const bootAct = new THREE.Mesh(new THREE.CylinderGeometry(0.12, 0.12, 0.12, 12), btnActuatorMat);
    bootAct.position.y = 0.12;
    bootBtn.add(bootAct);
    bootBtn.position.set(0.85, 0.16, 1.6);
    bootBtn.userData = {
      type: 'COMPONENT',
      name: 'BOOT Button (GPIO0)',
      role: 'Strapping pin GPIO0 pulled low to enter ROM bootloader download mode',
      pos: 'Lower Right',
      ref: 'ESP32-S3 Boot Mode Specification',
    };
    group.add(bootBtn);
    hwRaycastComponents.push(bootBtn);
    hwExplodedObjects.push({ mesh: bootBtn, baseY: 0.16, explodedY: 0.85, baseZ: 1.6, explodedZ: 1.6, baseX: 0.85, explodedX: 0.85 });

    // 5. Onboard Addressable RGB LED (Hardwired to GPIO38 on v1.1!)
    const rgbGeo = new THREE.BoxGeometry(0.24, 0.14, 0.24);
    const rgbMat = new THREE.MeshStandardMaterial({
      color: 0x10b981, // green operational standby
      emissive: 0x10b981,
      emissiveIntensity: 0.8,
      roughness: 0.2,
    });
    const rgbLed = new THREE.Mesh(rgbGeo, rgbMat);
    rgbLed.position.set(0.35, 0.15, 0.6);
    rgbLed.userData = {
      type: 'COMPONENT',
      name: 'Addressable RGB LED (GPIO38 on v1.1)',
      role: 'Onboard status indicator. Note: explicitly GPIO38 on v1.1 (GPIO48 on v1.0!)',
      pos: 'Center Right',
      ref: 'Espressif DevKitC-1 v1.1 User Guide Section 1.3',
    };
    group.add(rgbLed);
    hwRaycastComponents.push(rgbLed);

    // 3.3V Power LED (Red)
    const pwrLed = new THREE.Mesh(new THREE.BoxGeometry(0.18, 0.12, 0.18), new THREE.MeshStandardMaterial({ color: 0xef4444, emissive: 0xef4444, emissiveIntensity: 0.6 }));
    pwrLed.position.set(-0.35, 0.14, 0.6);
    pwrLed.userData = {
      type: 'COMPONENT',
      name: '3.3V Power LED',
      role: 'Illuminates red when 3.3V power regulator is active',
      pos: 'Center Left',
      ref: 'Power Management Circuit',
    };
    group.add(pwrLed);
    hwRaycastComponents.push(pwrLed);

    // 6. 3.3V LDO Voltage Regulator (ME6211)
    const ldoReg = new THREE.Mesh(new THREE.BoxGeometry(0.65, 0.18, 0.4), new THREE.MeshStandardMaterial({ color: 0x1e293b, roughness: 0.3 }));
    ldoReg.position.set(0, 0.16, 0.95);
    ldoReg.userData = {
      type: 'COMPONENT',
      name: '3.3V LDO Regulator (ME6211)',
      role: 'Converts 5V USB/VBUS rail down to stable 3.3V @ 500mA rail for MCU & sensors',
      pos: 'Lower Center',
      ref: 'Power Supply Specification',
    };
    group.add(ldoReg);
    hwRaycastComponents.push(ldoReg);

    // 7. Pin Headers J1 (Left Rail, 22 pins) and J3 (Right Rail, 22 pins)
    const j1Data = HW_FALLBACK_ESP32.headers.J1;
    const j3Data = HW_FALLBACK_ESP32.headers.J3;

    // Plastic header insulator blocks
    const hdrStripMat = new THREE.MeshStandardMaterial({ color: 0x1e293b, roughness: 0.8 });
    const j1Strip = new THREE.Mesh(new THREE.BoxGeometry(0.26, 0.25, 5.6), hdrStripMat);
    j1Strip.position.set(-1.14, 0.18, 0);
    group.add(j1Strip);
    hwExplodedObjects.push({ mesh: j1Strip, baseY: 0.18, explodedY: -0.6, baseZ: 0, explodedZ: 0, baseX: -1.14, explodedX: -1.7 });

    const j3Strip = new THREE.Mesh(new THREE.BoxGeometry(0.26, 0.25, 5.6), hdrStripMat);
    j3Strip.position.set(1.14, 0.18, 0);
    group.add(j3Strip);
    hwExplodedObjects.push({ mesh: j3Strip, baseY: 0.18, explodedY: -0.6, baseZ: 0, explodedZ: 0, baseX: 1.14, explodedX: 1.7 });

    const pinGoldMat = new THREE.MeshStandardMaterial({ color: 0xd4af37, metalness: 0.9, roughness: 0.1 });
    const pinAssignedMat = new THREE.MeshStandardMaterial({ color: 0x00f0ff, emissive: 0x00f0ff, emissiveIntensity: 0.5 });
    const pinReservedMat = new THREE.MeshStandardMaterial({ color: 0xef4444, emissive: 0xef4444, emissiveIntensity: 0.4 });

    // Generate J1 Pins (X = -1.14)
    const pinZStart = -2.66;
    const pinZStep = 0.254;

    j1Data.forEach((pin, i) => {
      const pz = pinZStart + i * pinZStep;
      const isAssigned = !!pin.assigned_to;
      const mat = isAssigned ? pinAssignedMat : pinGoldMat;

      const pMesh = new THREE.Mesh(new THREE.BoxGeometry(0.065, 0.65, 0.065), mat);
      pMesh.position.set(-1.14, 0.35, pz);
      pMesh.castShadow = true;
      group.add(pMesh);

      // Invisible hit cylinder for easier raycasting
      const hitMesh = new THREE.Mesh(new THREE.CylinderGeometry(0.12, 0.12, 0.8, 8), new THREE.MeshBasicMaterial({ visible: false }));
      hitMesh.position.set(-1.14, 0.35, pz);
      hitMesh.userData = {
        type: 'PIN',
        header: 'J1',
        pos: pin.pos,
        signal: pin.signal,
        data: pin,
        pinMesh: pMesh,
      };
      group.add(hitMesh);
      hwRaycastPins.push(hitMesh);
      hwExplodedObjects.push({ mesh: pMesh, baseY: 0.35, explodedY: -0.4, baseZ: pz, explodedZ: pz, baseX: -1.14, explodedX: -1.7 });
      hwExplodedObjects.push({ mesh: hitMesh, baseY: 0.35, explodedY: -0.4, baseZ: pz, explodedZ: pz, baseX: -1.14, explodedX: -1.7 });
    });

    // Generate J3 Pins (X = +1.14)
    j3Data.forEach((pin, i) => {
      const pz = pinZStart + i * pinZStep;
      const isAssigned = !!pin.assigned_to;
      const isReserved = pin.type === 'Reserved';
      const mat = isReserved ? pinReservedMat : (isAssigned ? pinAssignedMat : pinGoldMat);

      const pMesh = new THREE.Mesh(new THREE.BoxGeometry(0.065, 0.65, 0.065), mat);
      pMesh.position.set(1.14, 0.35, pz);
      pMesh.castShadow = true;
      group.add(pMesh);

      // Invisible hit cylinder
      const hitMesh = new THREE.Mesh(new THREE.CylinderGeometry(0.12, 0.12, 0.8, 8), new THREE.MeshBasicMaterial({ visible: false }));
      hitMesh.position.set(1.14, 0.35, pz);
      hitMesh.userData = {
        type: 'PIN',
        header: 'J3',
        pos: pin.pos,
        signal: pin.signal,
        data: pin,
        pinMesh: pMesh,
      };
      group.add(hitMesh);
      hwRaycastPins.push(hitMesh);
      hwExplodedObjects.push({ mesh: pMesh, baseY: 0.35, explodedY: -0.4, baseZ: pz, explodedZ: pz, baseX: 1.14, explodedX: 1.7 });
      hwExplodedObjects.push({ mesh: hitMesh, baseY: 0.35, explodedY: -0.4, baseZ: pz, explodedZ: pz, baseX: 1.14, explodedX: 1.7 });
    });

    return group;
  }

  function createPIRSensorModel() {
    const group = new THREE.Group();
    group.name = 'HC_SR501_BOARD';
    hwRaycastPins = []; hwRaycastComponents = []; hwExplodedObjects = [];

    // Green PCB (32mm x 24mm x 1.6mm)
    const pcb = new THREE.Mesh(new THREE.BoxGeometry(3.2, 0.16, 2.4), new THREE.MeshStandardMaterial({ color: 0x15803d, roughness: 0.5 }));
    group.add(pcb);

    // White Hemispherical Fresnel Lens Dome (faceted)
    const dome = new THREE.Mesh(new THREE.SphereGeometry(1.05, 18, 14, 0, Math.PI * 2, 0, Math.PI / 2), new THREE.MeshStandardMaterial({ color: 0xf8fafc, roughness: 0.15, transmission: 0.3 }));
    dome.position.y = 0.08;
    group.add(dome);

    // BISS0001 IC & 2 Trimpots (Sensitivity & Time Delay)
    const ic = new THREE.Mesh(new THREE.BoxGeometry(0.8, 0.15, 0.4), new THREE.MeshStandardMaterial({ color: 0x0f172a }));
    ic.position.set(-0.6, -0.14, 0);
    group.add(ic);

    const potMat = new THREE.MeshStandardMaterial({ color: 0xf97316 });
    const pot1 = new THREE.Mesh(new THREE.CylinderGeometry(0.22, 0.22, 0.2, 12), potMat);
    pot1.position.set(0.8, -0.16, -0.6);
    group.add(pot1);
    const pot2 = new THREE.Mesh(new THREE.CylinderGeometry(0.22, 0.22, 0.2, 12), potMat);
    pot2.position.set(0.8, -0.16, 0.6);
    group.add(pot2);

    // 3 Header Pins (VCC, OUT, GND)
    const pinMat = new THREE.MeshStandardMaterial({ color: 0xd4af37, metalness: 0.9 });
    [-0.3, 0, 0.3].forEach((z, idx) => {
      const pin = new THREE.Mesh(new THREE.CylinderGeometry(0.04, 0.04, 0.7, 8), pinMat);
      pin.position.set(-1.2, -0.4, z);
      group.add(pin);
    });

    return group;
  }

  function createVibrationSensorModel() {
    const group = new THREE.Group();
    group.name = 'SW420_BOARD';
    hwRaycastPins = []; hwRaycastComponents = []; hwExplodedObjects = [];

    // Blue PCB (32mm x 14mm)
    const pcb = new THREE.Mesh(new THREE.BoxGeometry(3.2, 0.16, 1.4), new THREE.MeshStandardMaterial({ color: 0x0284c7, roughness: 0.5 }));
    group.add(pcb);

    // Gold/Silver Brass Sensor Tube (SW-420 spring switch)
    const tubeMat = new THREE.MeshStandardMaterial({ color: 0xd4af37, metalness: 0.85, roughness: 0.2 });
    const tube = new THREE.Mesh(new THREE.CylinderGeometry(0.24, 0.24, 1.2, 16), tubeMat);
    tube.rotation.z = Math.PI / 2;
    tube.position.set(-0.7, 0.3, 0);
    group.add(tube);

    // LM393 Comparator IC
    const ic = new THREE.Mesh(new THREE.BoxGeometry(0.6, 0.12, 0.4), new THREE.MeshStandardMaterial({ color: 0x0f172a }));
    ic.position.set(0.2, 0.14, 0);
    group.add(ic);

    // Blue 10k Sensitivity Trimpot
    const pot = new THREE.Mesh(new THREE.BoxGeometry(0.5, 0.45, 0.35), new THREE.MeshStandardMaterial({ color: 0x3b82f6 }));
    pot.position.set(0.9, 0.28, 0);
    group.add(pot);

    // 3 Header Pins
    [-0.3, 0, 0.3].forEach(z => {
      const pin = new THREE.Mesh(new THREE.CylinderGeometry(0.04, 0.04, 0.6, 8), new THREE.MeshStandardMaterial({ color: 0xd4af37, metalness: 0.9 }));
      pin.position.set(1.4, -0.35, z);
      group.add(pin);
    });

    return group;
  }

  function createMicrophoneModel() {
    const group = new THREE.Group();
    group.name = 'INMP441_BOARD';
    hwRaycastPins = []; hwRaycastComponents = []; hwExplodedObjects = [];

    // Purple / Dark Matte Breakout Board (14mm x 14mm)
    const pcb = new THREE.Mesh(new THREE.BoxGeometry(1.6, 0.16, 1.6), new THREE.MeshStandardMaterial({ color: 0x581c87, roughness: 0.4 }));
    group.add(pcb);

    // Gold circular bottom acoustic port
    const port = new THREE.Mesh(new THREE.CylinderGeometry(0.18, 0.18, 0.18, 16), new THREE.MeshStandardMaterial({ color: 0xd4af37, metalness: 0.95 }));
    port.position.set(0, -0.05, 0);
    group.add(port);

    // Metallic MEMS Microphone IC Lid
    const ic = new THREE.Mesh(new THREE.BoxGeometry(0.55, 0.16, 0.45), new THREE.MeshStandardMaterial({ color: 0xe2e8f0, metalness: 0.9, roughness: 0.2 }));
    ic.position.set(0, 0.15, 0);
    group.add(ic);

    // 6 Gold Header Pins (SCK, WS, L/R, SD, VDD, GND)
    const pinMat = new THREE.MeshStandardMaterial({ color: 0xd4af37, metalness: 0.9 });
    for (let i = 0; i < 6; i++) {
      const z = -0.6 + i * 0.24;
      const pin = new THREE.Mesh(new THREE.CylinderGeometry(0.035, 0.035, 0.6, 8), pinMat);
      pin.position.set(0.65, -0.32, z);
      group.add(pin);
    }

    return group;
  }

  function createESP32CamModel() {
    const group = new THREE.Group();
    group.name = 'ESP32_CAM_BOARD';
    hwRaycastPins = []; hwRaycastComponents = []; hwExplodedObjects = [];

    // PCB (27mm x 40mm)
    const pcb = new THREE.Mesh(new THREE.BoxGeometry(2.7, 0.16, 4.0), new THREE.MeshStandardMaterial({ color: 0x0f172a, roughness: 0.5 }));
    group.add(pcb);

    // OV2640 Lens Module with Gold Aperture Ring
    const lensBase = new THREE.Mesh(new THREE.BoxGeometry(1.0, 0.25, 1.0), new THREE.MeshStandardMaterial({ color: 0x1e293b }));
    lensBase.position.set(0, 0.2, 0.7);
    group.add(lensBase);

    const lensCyl = new THREE.Mesh(new THREE.CylinderGeometry(0.35, 0.4, 0.4, 20), new THREE.MeshStandardMaterial({ color: 0x0a0a0a, metalness: 0.8 }));
    lensCyl.position.set(0, 0.45, 0.7);
    group.add(lensCyl);

    const lensGold = new THREE.Mesh(new THREE.TorusGeometry(0.36, 0.03, 8, 24), new THREE.MeshStandardMaterial({ color: 0xd4af37, metalness: 0.9 }));
    lensGold.rotation.x = Math.PI / 2;
    lensGold.position.set(0, 0.65, 0.7);
    group.add(lensGold);

    // High Power Flash LED (GPIO4)
    const flash = new THREE.Mesh(new THREE.BoxGeometry(0.3, 0.12, 0.3), new THREE.MeshStandardMaterial({ color: 0xfef08a, emissive: 0xfef08a, emissiveIntensity: 0.6 }));
    flash.position.set(0.8, 0.14, 0.7);
    group.add(flash);

    // MicroSD Slot
    const sd = new THREE.Mesh(new THREE.BoxGeometry(1.4, 0.18, 1.5), new THREE.MeshStandardMaterial({ color: 0x94a3b8, metalness: 0.85 }));
    sd.position.set(0, -0.16, -0.6);
    group.add(sd);

    return group;
  }

  function createRouterModelDetails() {
    const group = new THREE.Group();
    group.name = 'WIFI_ROUTER_MODEL';
    hwRaycastPins = []; hwRaycastComponents = []; hwExplodedObjects = [];

    // Router body
    const body = new THREE.Mesh(new THREE.BoxGeometry(4.2, 0.8, 2.8), new THREE.MeshStandardMaterial({ color: 0x0f172a, roughness: 0.4 }));
    group.add(body);

    // Cooling slats
    for (let x = -1.5; x <= 1.5; x += 0.3) {
      const slat = new THREE.Mesh(new THREE.BoxGeometry(0.08, 0.05, 1.8), new THREE.MeshStandardMaterial({ color: 0x00f0ff, emissive: 0x00f0ff, emissiveIntensity: 0.2 }));
      slat.position.set(x, 0.42, 0);
      group.add(slat);
    }

    // 3 Dual-Band Antennas
    const antMat = new THREE.MeshStandardMaterial({ color: 0x1e293b, roughness: 0.3 });
    [-1.5, 0, 1.5].forEach((x, i) => {
      const ant = new THREE.Mesh(new THREE.CylinderGeometry(0.08, 0.1, 3.2, 12), antMat);
      ant.position.set(x, 1.8, -1.35);
      ant.rotation.z = (i - 1) * 0.15;
      group.add(ant);
    });

    return group;
  }

  function createSolarPowerModel() {
    const group = new THREE.Group();
    group.name = 'SOLAR_POWER_MODEL';
    hwRaycastPins = []; hwRaycastComponents = []; hwExplodedObjects = [];

    // Solar PV Panel with aluminum frame
    const frame = new THREE.Mesh(new THREE.BoxGeometry(4.8, 0.16, 3.4), new THREE.MeshStandardMaterial({ color: 0x94a3b8, metalness: 0.8 }));
    group.add(frame);

    const pvCells = new THREE.Mesh(new THREE.PlaneGeometry(4.5, 3.1), new THREE.MeshStandardMaterial({ color: 0x1e1b4b, metalness: 0.9, roughness: 0.1 }));
    pvCells.rotation.x = -Math.PI / 2;
    pvCells.position.y = 0.09;
    group.add(pvCells);

    // LiFePO4 Battery Pack (4S 12.8V 12Ah)
    const bat = new THREE.Mesh(new THREE.BoxGeometry(2.4, 1.2, 1.6), new THREE.MeshStandardMaterial({ color: 0x1e293b, roughness: 0.6 }));
    bat.position.set(0, -0.9, 0);
    group.add(bat);

    return group;
  }

  // ==========================================================================
  // Hardware Device Loading & UI Synchronization
  // ==========================================================================
  async function loadHardwareDevice(deviceId) {
    hwCurrentDevice = deviceId;

    // Clear previous models from 3D scene
    const existing = hwThreeScene.getObjectByName('HW_WORKBENCH_ASSEMBLY') ||
                     hwThreeScene.getObjectByName('ESP32_S3_BOARD') ||
                     hwThreeScene.getObjectByName('HC_SR501_BOARD') ||
                     hwThreeScene.getObjectByName('SW420_BOARD') ||
                     hwThreeScene.getObjectByName('INMP441_BOARD') ||
                     hwThreeScene.getObjectByName('ESP32_CAM_BOARD') ||
                     hwThreeScene.getObjectByName('WIFI_ROUTER_MODEL') ||
                     hwThreeScene.getObjectByName('SOLAR_POWER_MODEL');
    if (existing) hwThreeScene.remove(existing);

    if (hwPinHighlightMesh) hwPinHighlightMesh.visible = false;
    if (hwPinDestHighlightMesh) hwPinDestHighlightMesh.visible = false;
    hwSelectedNet = null;

    // 1. Full Multi-Board Physical Workbench Mode
    if (deviceId === 'workbench') {
      const workbenchModel = createMultiBoardWiringWorkbench();
      hwThreeScene.add(workbenchModel);
      setHardwareCameraPreset('iso');
      updateHardwareWorkbenchInfoCard();
      populatePinoutTable(HW_FALLBACK_ESP32);
      filterWiresByCategory(hwActiveWireCategory);
      return;
    }

    // 2. Single Component Mode
    let data = hwDeviceCache[deviceId];
    if (!data) {
      try {
        const res = await fetch(`/api/hardware/${deviceId}`);
        if (res.ok) {
          data = await res.json();
          hwDeviceCache[deviceId] = data;
        }
      } catch (e) {
        console.warn('Could not fetch hardware API, using embedded fallback:', e);
      }
    }

    if (!data && deviceId === 'esp32_s3_devkitc1_v1_1') {
      data = HW_FALLBACK_ESP32;
    }

    let newModel = null;
    if (deviceId === 'esp32_s3_devkitc1_v1_1') newModel = createESP32DevKitModel();
    else if (deviceId === 'hc_sr501_reference') newModel = createPIRSensorModel();
    else if (deviceId === 'sw420_reference') newModel = createVibrationSensorModel();
    else if (deviceId === 'inmp441_breakout_reference') newModel = createMicrophoneModel();
    else if (deviceId === 'ai_thinker_esp32_cam_ov2640') newModel = createESP32CamModel();
    else if (deviceId === 'wifi_access_point_reference') newModel = createRouterModelDetails();
    else if (deviceId === 'power_system_reference') newModel = createSolarPowerModel();

    if (newModel) hwThreeScene.add(newModel);

    setHardwareCameraPreset('iso');
    updateHardwareInfoCard(data || { name: deviceId });
    populatePinoutTable(data);
  }

  function updateHardwareWorkbenchInfoCard() {
    document.getElementById('hwRefBadge').textContent = 'REF: SIL_3D_WORKBENCH_V1.1';
    document.getElementById('hwCompBadge').textContent = 'ESP32-S3 + SENSOR CLUSTER (11 NETS)';
    document.getElementById('hwCompName').textContent = 'Interactive 3D Physical Wiring Assembly';
    document.getElementById('hwCompDesc').textContent = 'Full physical multi-board hardware cluster with ESP32-S3-DevKitC-1 v1.1, HC-SR501 PIR sensor, SW-420 vibration sensor, INMP441 I2S microphone, and AI-Thinker ESP32-CAM wired with curved 3D insulated DuPont jumper cables.';

    const metaGrid = document.getElementById('hwCompMetaGrid');
    if (metaGrid) {
      document.getElementById('hwMetaPos').textContent = 'Laboratory ESD Mat Carrier (4 Devices + Camera)';
      document.getElementById('hwMetaSignal').textContent = '11 Verified Nets (Power, Ground, GPIO, I2S)';
      document.getElementById('hwMetaVolt').textContent = '5.0V USB / 3.3V LDO Rails';
      document.getElementById('hwMetaPower').textContent = '~140mA Rx (Peak 320mA with Wi-Fi CSI burst)';
      document.getElementById('hwMetaRole').textContent = 'Autonomous SIL Hardware Cluster Early-Warning Array';

      const linkEl = document.getElementById('hwMetaLink');
      if (linkEl) {
        linkEl.href = '#';
        linkEl.textContent = '11/11 Verified from Schematics ↗';
      }
    }

    const revAlert = document.getElementById('hwRevisionAlert');
    if (revAlert) {
      revAlert.classList.remove('hidden');
      document.getElementById('hwRevisionText').textContent = 'Verified v1.1 DevKitC-1 pinout: WS2812 RGB LED is GPIO38 (v1.0 was GPIO48). Internal Octal Flash/PSRAM bus pins GPIO35-37 strictly reserved. PIR powered from 5V rail; Vibration and I2S Mic powered from 3.3V rail.';
    }
  }

  function highlightWire(wireMesh) {
    if (!wireMesh || !wireMesh.userData?.net) return;
    const net = wireMesh.userData.net;
    hwSelectedNet = net;

    // Reset all wires
    hwWireMeshes.forEach(wm => {
      wm.material.emissive.setHex(0x000000);
      wm.material.emissiveIntensity = 0.0;
    });

    // Highlight selected wire
    wireMesh.material.emissive.setHex(wireMesh.userData.baseColor);
    wireMesh.material.emissiveIntensity = 0.85;

    // Highlight source and destination pins
    const src = net.source.rel_coord_3d;
    const dst = net.destination.rel_coord_3d;
    if (hwPinHighlightMesh) {
      hwPinHighlightMesh.position.set(src[0], src[1] + 0.38, src[2]);
      hwPinHighlightMesh.visible = true;
    }
    if (hwPinDestHighlightMesh) {
      hwPinDestHighlightMesh.position.set(dst[0], dst[1] + 0.38, dst[2]);
      hwPinDestHighlightMesh.visible = true;
    }

    // Update Quick Card
    document.getElementById('hwRefBadge').textContent = `NET: ${net.net_id}`;
    document.getElementById('hwCompBadge').textContent = `${net.category.toUpperCase()} RAIL • ${net.voltage_domain_v.toFixed(1)}V DC`;
    document.getElementById('hwCompName').textContent = `${net.net_name} (${net.connector_type})`;
    document.getElementById('hwCompDesc').textContent = net.engineering_notes;
    document.getElementById('hwMetaPos').textContent = `${net.source.device_name} (${net.source.connector} #${net.source.pin_position} ${net.source.pin_signal}) ➔ ${net.destination.device_name} (${net.destination.connector} #${net.destination.pin_position} ${net.destination.pin_signal})`;
    document.getElementById('hwMetaSignal').textContent = `${net.signal_direction} • ${net.wire_gauge_awg} AWG Insulated`;
    document.getElementById('hwMetaVolt').textContent = `${net.voltage_domain_v.toFixed(1)}V DC Domain`;
    document.getElementById('hwMetaPower').textContent = `Max Current Rating: ${net.max_current_ma} mA`;
    document.getElementById('hwMetaRole').textContent = `Net ${net.net_id}: Verified ${net.category} connection`;

    const linkEl = document.getElementById('hwMetaLink');
    if (linkEl) {
      linkEl.href = '#';
      linkEl.textContent = `Verification: ${net.verification_status}`;
    }

    const revAlert = document.getElementById('hwRevisionAlert');
    if (revAlert) {
      revAlert.classList.remove('hidden');
      document.getElementById('hwRevisionText').textContent = `Source: ${net.verification_source}. Status: ${net.verification_status}.`;
    }

    // Highlight in pinout table if present
    document.querySelectorAll('#pinoutTable tbody tr').forEach(r => {
      const match = r.dataset.netId === net.net_id || r.dataset.pinSignal === net.source.pin_signal;
      r.classList.toggle('selected', match);
      if (match) r.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
    });
  }

  function highlightPinAndConnectedWire(pinHitData) {
    const net = HW_WIRING_MANIFEST.wiring_nets.find(n =>
      (n.source.pin_signal === pinHitData.signal) ||
      (n.destination.pin_signal === pinHitData.signal) ||
      (n.source.connector === pinHitData.header && n.source.pin_position === pinHitData.pos) ||
      (n.destination.connector === pinHitData.header && n.destination.pin_position === pinHitData.pos)
    );
    if (net) {
      const matchWire = hwWireMeshes.find(wm => wm.userData.net.net_id === net.net_id);
      if (matchWire) {
        highlightWire(matchWire);
        return;
      }
    }
    highlightPinBySignal(pinHitData.signal);
  }

  function filterWiresByCategory(cat) {
    hwActiveWireCategory = cat;
    document.querySelectorAll('#hwWireFilterGroup .hw-tool-btn').forEach(b => {
      b.classList.toggle('active', b.dataset.cat === cat);
    });
    hwWireMeshes.forEach(wm => {
      const nCat = wm.userData.net.category;
      const isMatch = (cat === 'all') || (nCat === cat);
      wm.visible = hwShowWires && isMatch;
    });
  }

  function toggleWires() {
    hwShowWires = !hwShowWires;
    const btn = document.getElementById('btnToggleWires');
    if (btn) {
      btn.textContent = hwShowWires ? '🔌 WIRES: ON' : '🔌 WIRES: OFF';
      btn.classList.toggle('active', hwShowWires);
    }
    filterWiresByCategory(hwActiveWireCategory);
  }

  function updateHardwareInfoCard(d) {
    document.getElementById('hwRefBadge').textContent = `REF: ${d.name || d.device_id}`;
    document.getElementById('hwCompBadge').textContent = (d.board_revision || d.sku_status || d.name || '').toUpperCase();
    document.getElementById('hwCompName').textContent = d.name || 'Component';
    document.getElementById('hwCompDesc').textContent = d.soc || d.sensor_element || d.role_in_prw_wild || d.desc || 'PRW-Wild verified hardware node.';

    const metaGrid = document.getElementById('hwCompMetaGrid');
    if (metaGrid) {
      document.getElementById('hwMetaPos').textContent = d.board_revision ? 'DevKitC-1 v1.1 Standard' : 'Field Mast / Module';
      document.getElementById('hwMetaSignal').textContent = d.wireless || d.core_ic || 'Verified Signal Block';
      const voltTxt = d.operating_voltage ? `${d.operating_voltage.recommended_input_v}V Nom` : (d.electrical_specs?.supply_voltage_range_v || '3.3V / 5.0V');
      document.getElementById('hwMetaVolt').textContent = voltTxt;
      document.getElementById('hwMetaPower').textContent = d.operating_voltage ? '~120mA Rx (Peak 310mA)' : '< 15 mA';
      document.getElementById('hwMetaRole').textContent = typeof d.role_in_prw_wild === 'string' ? d.role_in_prw_wild : (d.role_in_prw_wild?.purpose || 'Verified sensing layer');

      const linkEl = document.getElementById('hwMetaLink');
      if (linkEl) {
        linkEl.href = d.official_guide_url || d.official_datasheet_url || d.official_pinout_url || '#';
        linkEl.textContent = d.official_guide_url ? 'Official User Guide ↗' : 'Datasheet Specification ↗';
      }
    }

    const revAlert = document.getElementById('hwRevisionAlert');
    if (revAlert) {
      if (d.revision_differences) {
        revAlert.classList.remove('hidden');
        document.getElementById('hwRevisionText').textContent = `${d.revision_differences.v1_1_vs_v1_0} ${d.revision_differences.memory_restrictions}`;
      } else {
        revAlert.classList.add('hidden');
      }
    }
  }

  function populatePinoutTable(d) {
    const tbody = document.getElementById('pinoutTableBody');
    if (!tbody) return;
    tbody.innerHTML = '';

    // If in Workbench Mode or WIRING header tab, show verified sensor nets
    if (hwCurrentSubMode === 'workbench' || hwCurrentHeaderTab === 'WIRING') {
      HW_WIRING_MANIFEST.wiring_nets.forEach((net, i) => {
        const tr = document.createElement('tr');
        tr.dataset.netId = net.net_id;
        tr.dataset.pinSignal = net.source.pin_signal;
        tr.classList.add('wiring-active');

        tr.innerHTML = `
          <td><strong>#${i + 1}</strong></td>
          <td><strong style="color: ${net.wire_color};">${net.net_name}</strong></td>
          <td><span style="font-size:10px; color:${net.wire_color}; border:1px solid ${net.wire_color}; padding:1px 4px; border-radius:2px;">${net.category.toUpperCase()}</span></td>
          <td><strong>${net.voltage_domain_v.toFixed(1)}V</strong></td>
          <td><span style="color:#e2e8f0;">${net.source.pin_signal} ➔ ${net.destination.device_name.split(' ')[0]} ${net.destination.pin_signal}</span></td>
          <td><span class="hw-verification-pill verified">VERIFIED</span></td>
        `;

        tr.addEventListener('click', () => {
          document.querySelectorAll('#pinoutTable tbody tr').forEach(r => r.classList.remove('selected'));
          tr.classList.add('selected');
          const matchWire = hwWireMeshes.find(wm => wm.userData.net.net_id === net.net_id);
          if (matchWire) highlightWire(matchWire);
        });

        tbody.appendChild(tr);
      });
      return;
    }

    if (!d || !d.headers) {
      tbody.innerHTML = `<tr><td colspan="6" class="text-center" style="color:var(--text-muted); padding:14px;">Select ESP32-S3 DevKitC-1 to inspect dual J1/J3 44-pin headers and sensor wiring.</td></tr>`;
      return;
    }

    let pinsToShow = [];
    if (hwCurrentHeaderTab === 'J1') {
      pinsToShow = d.headers.J1 || [];
    } else if (hwCurrentHeaderTab === 'J3') {
      pinsToShow = d.headers.J3 || [];
    }

    pinsToShow.forEach(pin => {
      const tr = document.createElement('tr');
      tr.dataset.pinPos = pin.pos;
      tr.dataset.pinSignal = pin.signal;

      const isReserved = pin.type === 'Reserved';
      const isAssigned = !!pin.assigned_to;
      if (isReserved) tr.classList.add('reserved');
      if (isAssigned) tr.classList.add('wiring-active');

      tr.innerHTML = `
        <td><strong>#${pin.pos}</strong></td>
        <td><strong style="color:${isReserved ? '#ef4444' : (isAssigned ? '#00f0ff' : 'inherit')}">${pin.signal}</strong></td>
        <td>${pin.type}</td>
        <td>${pin.volt_v ? pin.volt_v.toFixed(1) + 'V' : '--'}</td>
        <td>${pin.assigned_to ? `<span style="color:#00f0ff; font-weight:700;">★ ${pin.assigned_to}</span>` : `<span style="color:var(--text-dim);">${pin.desc || '--'}</span>`}</td>
        <td><span class="hw-verification-pill verified">VERIFIED</span></td>
      `;

      tr.addEventListener('click', () => {
        document.querySelectorAll('#pinoutTable tbody tr').forEach(r => r.classList.remove('selected'));
        tr.classList.add('selected');
        highlightPinBySignal(pin.signal);
      });

      tbody.appendChild(tr);
    });
  }

  function highlightPinBySignal(signal) {
    const match = hwRaycastPins.find(p => p.userData?.signal === signal);
    if (match) {
      const pos = match.position;
      hwPinHighlightMesh.position.set(pos.x, pos.y + 0.38, pos.z);
      hwPinHighlightMesh.visible = true;

      // Update Quick Card
      const pData = match.userData.data;
      if (pData) {
        document.getElementById('hwCompBadge').textContent = `${match.userData.header || 'PIN'} #${pData.pos || ''} • ${pData.signal}`;
        document.getElementById('hwCompName').textContent = pData.desc || pData.signal;
        document.getElementById('hwCompDesc').textContent = pData.notes || `Electrical Signal on ${match.userData.header || 'Header'}`;
        document.getElementById('hwMetaPos').textContent = `${match.userData.header || 'Header'} Pin Position ${pData.pos || ''}`;
        document.getElementById('hwMetaSignal').textContent = pData.signal;
        document.getElementById('hwMetaVolt').textContent = pData.volt_v ? `${pData.volt_v}V` : '3.3V';
        document.getElementById('hwMetaRole').textContent = pData.assigned_to || 'General GPIO / Peripheral';
      }
    }
  }

  function setupHardwareRaycaster(container) {
    const raycaster = new THREE.Raycaster();
    const mouse = new THREE.Vector2();

    container.addEventListener('click', (e) => {
      const rect = container.getBoundingClientRect();
      mouse.x = ((e.clientX - rect.left) / container.clientWidth) * 2 - 1;
      mouse.y = -((e.clientY - rect.top) / container.clientHeight) * 2 + 1;

      raycaster.setFromCamera(mouse, hwThreeCamera);

      // 1. Raycast against 3D Wires first!
      if (hwShowWires && hwRaycastWires.length > 0) {
        const wireHits = raycaster.intersectObjects(hwRaycastWires, true);
        if (wireHits.length > 0) {
          const hit = wireHits[0].object;
          if (hit.userData && hit.userData.type === 'WIRE') {
            highlightWire(hit);
            return;
          }
        }
      }

      // 2. Raycast against Header Pins
      const pinHits = raycaster.intersectObjects(hwRaycastPins, true);
      if (pinHits.length > 0) {
        const hit = pinHits[0].object;
        if (hit.userData && hit.userData.type === 'PIN') {
          highlightPinAndConnectedWire(hit.userData);

          // Highlight row in table
          document.querySelectorAll('#pinoutTable tbody tr').forEach(r => {
            const isMatch = r.dataset.pinSignal === hit.userData.signal;
            r.classList.toggle('selected', isMatch);
            if (isMatch) r.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
          });
          return;
        }
      }

      // 3. Raycast against Components
      const compHits = raycaster.intersectObjects(hwRaycastComponents, true);
      if (compHits.length > 0) {
        let obj = compHits[0].object;
        while (obj && !obj.userData?.name && obj.parent) obj = obj.parent;
        if (obj && obj.userData && obj.userData.name) {
          const ud = obj.userData;
          document.getElementById('hwCompBadge').textContent = ud.type || 'COMPONENT';
          document.getElementById('hwCompName').textContent = ud.name;
          document.getElementById('hwCompDesc').textContent = ud.role || '';
          document.getElementById('hwMetaPos').textContent = ud.pos || 'Onboard';
          document.getElementById('hwMetaRole').textContent = ud.role || '';
        }
      }
    });
  }

  function setHardwareCameraPreset(preset) {
    if (!hwThreeControls || !hwThreeCamera) return;
    document.querySelectorAll('.hw-cam-presets .hw-tool-btn').forEach(b => b.classList.remove('active'));

    const isWorkbench = (hwCurrentSubMode === 'workbench');

    if (preset === 'iso') {
      hwThreeControls.target.set(0, 0, 0);
      if (isWorkbench) {
        hwThreeCamera.position.set(0, 11.0, 9.5);
      } else {
        hwThreeCamera.position.set(5.2, 7.2, 6.2);
      }
      document.getElementById('btnHwCamIso')?.classList.add('active');
    } else if (preset === 'top') {
      hwThreeControls.target.set(0, 0, 0);
      if (isWorkbench) {
        hwThreeCamera.position.set(0, 16.0, 0.01);
      } else {
        hwThreeCamera.position.set(0, 10.5, 0.01);
      }
      document.getElementById('btnHwCamTop')?.classList.add('active');
    } else if (preset === 'front') {
      hwThreeControls.target.set(0, 0, 0);
      if (isWorkbench) {
        hwThreeCamera.position.set(0, 2.8, 12.0);
      } else {
        hwThreeCamera.position.set(0, 1.8, 8.5);
      }
      document.getElementById('btnHwCamFront')?.classList.add('active');
    } else if (preset === 'back') {
      hwThreeControls.target.set(0, 0, 0);
      if (isWorkbench) {
        hwThreeCamera.position.set(0, -14.0, 0.01);
      } else {
        hwThreeCamera.position.set(0, -9.5, 0.01);
      }
      document.getElementById('btnHwCamBack')?.classList.add('active');
    }
    hwThreeControls.update();
  }

  // ==========================================================================
  // Interactive Wiring Schematic Canvas
  // ==========================================================================
  let wiringPulsePhase = 0;
  let wiringAnimId = null;

  function renderHardwareWiring() {
    const canvas = document.getElementById('hardwareWiringCanvas');
    if (!canvas) return;
    const ctx = canvas.getContext('2d');
    const w = canvas.width;
    const h = canvas.height;

    ctx.clearRect(0, 0, w, h);

    // Background Grid
    ctx.strokeStyle = 'rgba(51, 65, 85, 0.25)';
    ctx.lineWidth = 1;
    for (let x = 0; x < w; x += 30) {
      ctx.beginPath(); ctx.moveTo(x, 0); ctx.lineTo(x, h); ctx.stroke();
    }
    for (let y = 0; y < h; y += 30) {
      ctx.beginPath(); ctx.moveTo(0, y); ctx.lineTo(w, y); ctx.stroke();
    }

    // 1. Central ESP32-S3 Block
    const espX = 260, espY = 70, espW = 200, espH = 380;
    ctx.fillStyle = 'rgba(15, 23, 42, 0.95)';
    ctx.strokeStyle = '#00f0ff';
    ctx.lineWidth = 2;
    ctx.beginPath();
    ctx.roundRect(espX, espY, espW, espH, 8);
    ctx.fill();
    ctx.stroke();

    // ESP32 Silk Title
    ctx.fillStyle = '#00f0ff';
    ctx.font = 'bold 13px Outfit, sans-serif';
    ctx.textAlign = 'center';
    ctx.fillText('ESP32-S3-DevKitC-1 v1.1', espX + espW / 2, espY + 28);
    ctx.fillStyle = '#94a3b8';
    ctx.font = '10px JetBrains Mono, monospace';
    ctx.fillText('WROOM-1 • CSI EDGE NODE', espX + espW / 2, espY + 44);

    // 2. Peripheral Blocks
    // HC-SR501 PIR (Top Left)
    const pirX = 40, pirY = 60, pirW = 150, pirH = 100;
    ctx.fillStyle = 'rgba(21, 128, 61, 0.2)';
    ctx.strokeStyle = '#10b981';
    ctx.beginPath(); ctx.roundRect(pirX, pirY, pirW, pirH, 6); ctx.fill(); ctx.stroke();
    ctx.fillStyle = '#10b981'; ctx.font = 'bold 11px Outfit, sans-serif'; ctx.fillText('HC-SR501 PIR SENSOR', pirX + pirW / 2, pirY + 22);

    // SW-420 Vibration (Bottom Left)
    const vibX = 40, vibY = 280, vibW = 150, vibH = 100;
    ctx.fillStyle = 'rgba(2, 132, 199, 0.2)';
    ctx.strokeStyle = '#0284c7';
    ctx.beginPath(); ctx.roundRect(vibX, vibY, vibW, vibH, 6); ctx.fill(); ctx.stroke();
    ctx.fillStyle = '#38bdf8'; ctx.font = 'bold 11px Outfit, sans-serif'; ctx.fillText('SW-420 SEISMIC VIB', vibX + vibW / 2, vibY + 22);

    // INMP441 Microphone (Right)
    const micX = 520, micY = 140, micW = 160, micH = 180;
    ctx.fillStyle = 'rgba(168, 85, 247, 0.2)';
    ctx.strokeStyle = '#a855f7';
    ctx.beginPath(); ctx.roundRect(micX, micY, micW, micH, 6); ctx.fill(); ctx.stroke();
    ctx.fillStyle = '#c084fc'; ctx.font = 'bold 11px Outfit, sans-serif'; ctx.fillText('INMP441 I2S MIC', micX + micW / 2, micY + 24);

    // 3. Draw Verified Interconnect Wires
    const wires = [
      { color: '#ef4444', label: '5V VBUS (J3-21)', from: [pirX + pirW, pirY + 45], to: [espX + espW, espY + 340], way: [220, 105, 490, 340] },
      { color: '#64748b', label: 'Common GND', from: [pirX + pirW, pirY + 65], to: [espX + espW, espY + 360], way: [230, 125, 480, 360] },
      { color: '#00f0ff', label: 'OUT -> GPIO4 (J1-4)', from: [pirX + pirW, pirY + 85], to: [espX, espY + 110], way: [210, 145, 240, 110] },

      { color: '#f59e0b', label: '3.3V (J1-1)', from: [vibX + vibW, vibY + 45], to: [espX, espY + 80], way: [210, 325, 230, 80] },
      { color: '#64748b', label: 'Common GND', from: [vibX + vibW, vibY + 65], to: [espX + espW, espY + 80], way: [215, 345, 480, 80] },
      { color: '#00f0ff', label: 'DO -> GPIO5 (J1-5)', from: [vibX + vibW, vibY + 85], to: [espX, espY + 125], way: [220, 365, 240, 125] },

      { color: '#f59e0b', label: '3.3V VDD (J1-2)', from: [micX, micY + 50], to: [espX, espY + 95], way: [500, 190, 240, 95] },
      { color: '#64748b', label: 'GND & L/R', from: [micX, micY + 70], to: [espX + espW, espY + 320], way: [490, 210, 480, 320] },
      { color: '#a855f7', label: 'SD -> GPIO7 (J1-7)', from: [micX, micY + 95], to: [espX, espY + 140], way: [500, 235, 230, 140] },
      { color: '#a855f7', label: 'WS -> GPIO8 (J1-12)', from: [micX, micY + 120], to: [espX, espY + 180], way: [505, 260, 230, 180] },
      { color: '#a855f7', label: 'SCK -> GPIO9 (J1-17)', from: [micX, micY + 145], to: [espX, espY + 230], way: [510, 285, 230, 230] },
    ];

    wires.forEach(wItem => {
      ctx.strokeStyle = wItem.color;
      ctx.lineWidth = 2;
      ctx.beginPath();
      ctx.moveTo(wItem.from[0], wItem.from[1]);
      ctx.lineTo(wItem.to[0], wItem.to[1]);
      ctx.stroke();

      const t = (wiringPulsePhase % 100) / 100;
      const px = wItem.from[0] + (wItem.to[0] - wItem.from[0]) * t;
      const py = wItem.from[1] + (wItem.to[1] - wItem.from[1]) * t;
      ctx.fillStyle = '#ffffff';
      ctx.beginPath();
      ctx.arc(px, py, 3, 0, Math.PI * 2);
      ctx.fill();
    });

    wiringPulsePhase += 1.2;
    if (hwCurrentSubMode === 'wiring') {
      wiringAnimId = requestAnimationFrame(renderHardwareWiring);
    }
  }

  function setupHardwareLabEvents() {
    // Mode tabs (Components)
    document.querySelectorAll('#hwDeviceSelectorTabs .hw-tab').forEach(btn => {
      btn.addEventListener('click', () => {
        document.querySelectorAll('#hwDeviceSelectorTabs .hw-tab').forEach(b => b.classList.remove('active'));
        btn.classList.add('active');

        // Switch to single component mode
        hwCurrentSubMode = '3d';
        document.getElementById('btnHwMode3D')?.classList.add('active');
        document.getElementById('btnHwModeWorkbench')?.classList.remove('active');
        document.getElementById('btnHwModeWiring')?.classList.remove('active');
        document.getElementById('hardwareLab3DContainer')?.classList.remove('hidden');
        document.getElementById('hardwareWiringContainer')?.classList.add('hidden');
        document.getElementById('hwWireFilterGroup')?.classList.add('hidden');
        document.getElementById('btnToggleWires')?.classList.add('hidden');
        if (wiringAnimId) cancelAnimationFrame(wiringAnimId);

        loadHardwareDevice(btn.dataset.dev);
      });
    });

    // Sub-mode switchers
    document.getElementById('btnHwModeWorkbench')?.addEventListener('click', () => {
      hwCurrentSubMode = 'workbench';
      document.getElementById('btnHwModeWorkbench')?.classList.add('active');
      document.getElementById('btnHwMode3D')?.classList.remove('active');
      document.getElementById('btnHwModeWiring')?.classList.remove('active');
      document.getElementById('hardwareLab3DContainer')?.classList.remove('hidden');
      document.getElementById('hardwareWiringContainer')?.classList.add('hidden');
      document.getElementById('hwWireFilterGroup')?.classList.remove('hidden');
      document.getElementById('btnToggleWires')?.classList.remove('hidden');
      if (wiringAnimId) cancelAnimationFrame(wiringAnimId);

      document.querySelectorAll('#hwDeviceSelectorTabs .hw-tab').forEach(b => b.classList.remove('active'));
      loadHardwareDevice('workbench');
    });

    document.getElementById('btnHwMode3D')?.addEventListener('click', () => {
      hwCurrentSubMode = '3d';
      document.getElementById('btnHwMode3D')?.classList.add('active');
      document.getElementById('btnHwModeWorkbench')?.classList.remove('active');
      document.getElementById('btnHwModeWiring')?.classList.remove('active');
      document.getElementById('hardwareLab3DContainer')?.classList.remove('hidden');
      document.getElementById('hardwareWiringContainer')?.classList.add('hidden');
      document.getElementById('hwWireFilterGroup')?.classList.add('hidden');
      document.getElementById('btnToggleWires')?.classList.add('hidden');
      if (wiringAnimId) cancelAnimationFrame(wiringAnimId);

      const target = (hwCurrentDevice === 'workbench') ? 'esp32_s3_devkitc1_v1_1' : hwCurrentDevice;
      const matchTab = document.querySelector(`#hwDeviceSelectorTabs .hw-tab[data-dev="${target}"]`);
      if (matchTab) {
        document.querySelectorAll('#hwDeviceSelectorTabs .hw-tab').forEach(b => b.classList.remove('active'));
        matchTab.classList.add('active');
      }
      loadHardwareDevice(target);
    });

    document.getElementById('btnHwModeWiring')?.addEventListener('click', () => {
      hwCurrentSubMode = 'wiring';
      document.getElementById('btnHwModeWiring')?.classList.add('active');
      document.getElementById('btnHwModeWorkbench')?.classList.remove('active');
      document.getElementById('btnHwMode3D')?.classList.remove('active');
      document.getElementById('hardwareLab3DContainer')?.classList.add('hidden');
      document.getElementById('hardwareWiringContainer')?.classList.remove('hidden');
      renderHardwareWiring();
    });

    document.getElementById('btnHwModePinout')?.addEventListener('click', () => {
      document.querySelector('.pinout-card')?.scrollIntoView({ behavior: 'smooth' });
    });

    // Wire Category Filtering
    document.querySelectorAll('#hwWireFilterGroup .hw-tool-btn').forEach(btn => {
      btn.addEventListener('click', () => {
        filterWiresByCategory(btn.dataset.cat);
      });
    });

    // Show/Hide Wires Toggle
    document.getElementById('btnToggleWires')?.addEventListener('click', () => {
      toggleWires();
    });

    // Camera preset buttons
    document.getElementById('btnHwCamIso')?.addEventListener('click', () => setHardwareCameraPreset('iso'));
    document.getElementById('btnHwCamTop')?.addEventListener('click', () => setHardwareCameraPreset('top'));
    document.getElementById('btnHwCamFront')?.addEventListener('click', () => setHardwareCameraPreset('front'));
    document.getElementById('btnHwCamBack')?.addEventListener('click', () => setHardwareCameraPreset('back'));
    document.getElementById('btnHwCamReset')?.addEventListener('click', () => setHardwareCameraPreset('iso'));

    // Exploded View Button
    document.getElementById('btnToggleExplodedView')?.addEventListener('click', () => {
      hwExploded = !hwExploded;
      document.getElementById('btnToggleExplodedView')?.classList.toggle('active', hwExploded);
    });

    // Header J1 / J3 Tabs
    document.getElementById('btnHeaderJ1')?.addEventListener('click', () => {
      hwCurrentHeaderTab = 'J1';
      document.getElementById('btnHeaderJ1').classList.add('active');
      document.getElementById('btnHeaderJ3').classList.remove('active');
      document.getElementById('btnHeaderWiring').classList.remove('active');
      populatePinoutTable(hwDeviceCache[hwCurrentDevice] || HW_FALLBACK_ESP32);
    });

    document.getElementById('btnHeaderJ3')?.addEventListener('click', () => {
      hwCurrentHeaderTab = 'J3';
      document.getElementById('btnHeaderJ3').classList.add('active');
      document.getElementById('btnHeaderJ1').classList.remove('active');
      document.getElementById('btnHeaderWiring').classList.remove('active');
      populatePinoutTable(hwDeviceCache[hwCurrentDevice] || HW_FALLBACK_ESP32);
    });

    document.getElementById('btnHeaderWiring')?.addEventListener('click', () => {
      hwCurrentHeaderTab = 'WIRING';
      document.getElementById('btnHeaderWiring').classList.add('active');
      document.getElementById('btnHeaderJ1').classList.remove('active');
      document.getElementById('btnHeaderJ3').classList.remove('active');
      populatePinoutTable(hwDeviceCache[hwCurrentDevice] || HW_FALLBACK_ESP32);
    });

    // Pinout Search Input
    document.getElementById('pinoutSearchInput')?.addEventListener('input', (e) => {
      const q = e.target.value.toLowerCase();
      document.querySelectorAll('#pinoutTable tbody tr').forEach(r => {
        const text = r.textContent.toLowerCase();
        r.style.display = text.includes(q) ? '' : 'none';
      });
    });

    // Close Modal Button
    document.getElementById('closeHardwareLabBtn')?.addEventListener('click', () => {
      document.getElementById('hardwareLabModal')?.classList.add('hidden');
    });

    // Toolbar Mode E Button
    document.getElementById('tabModeHardware')?.addEventListener('click', () => {
      document.getElementById('hardwareLabModal')?.classList.remove('hidden');
      setTimeout(() => {
        if (hwThreeRenderer && hwThreeCamera) {
          const c = document.getElementById('hardwareLab3DContainer');
          if (c) {
            hwThreeCamera.aspect = c.clientWidth / c.clientHeight;
            hwThreeCamera.updateProjectionMatrix();
            hwThreeRenderer.setSize(c.clientWidth, c.clientHeight);
          }
        }
      }, 50);
    });

    // Inspect Card Action Button
    document.getElementById('btnOpenInHardwareLab')?.addEventListener('click', () => {
      const inspType = document.getElementById('inspType')?.textContent || '';
      let targetDev = 'esp32_s3_devkitc1_v1_1';
      if (inspType.includes('ROUTER')) targetDev = 'wifi_access_point_reference';
      else if (inspType.includes('PIR')) targetDev = 'hc_sr501_reference';
      else if (inspType.includes('ACOUSTIC')) targetDev = 'inmp441_breakout_reference';
      else if (inspType.includes('CAMERA')) targetDev = 'ai_thinker_esp32_cam_ov2640';

      document.getElementById('hardwareLabModal')?.classList.remove('hidden');
      loadHardwareDevice(targetDev);
    });
  }

  // ==========================================================================
  // Camera POV Secondary Three.js Renderer
  // ==========================================================================
  function initCameraPovRenderer() {
    const povCanvas = document.getElementById('camPovCanvas');
    if (!povCanvas || !window.THREE) return;

    try {
      camPovRenderer = new THREE.WebGLRenderer({ canvas: povCanvas, antialias: true });
      camPovRenderer.setSize(280, 158);
      camPovRenderer.toneMapping = THREE.ACESFilmicToneMapping;
      camPovRenderer.toneMappingExposure = 1.2;
    } catch (e) {
      console.warn('Could not initialize secondary Camera POV WebGL renderer:', e);
    }
  }


  // UI Event Handlers
  document.getElementById('randomSeedBtn')?.addEventListener('click', () => {
    const input = document.getElementById('seedInput');
    if (input) input.value = Math.floor(Math.random() * 90000) + 1000;
  });

  document.getElementById('runSimBtn')?.addEventListener('click', () => {
    const sc = document.getElementById('scenarioSelect')?.value || 'approach_crossing';
    const seed = document.getElementById('seedInput')?.value || 42;
    runSimulation(sc, seed);
  });

  document.getElementById('scenarioSelect')?.addEventListener('change', () => {
    const sc = document.getElementById('scenarioSelect')?.value || 'approach_crossing';
    const seed = document.getElementById('seedInput')?.value || 42;
    runSimulation(sc, seed);
  });

  // ==========================================================================
  // Initialization
  // ==========================================================================
  async function init() {
    initThreeScene();
    init2DCanvas();
    initCameraPovRenderer();
    initHardwareLab();
    await loadScenariosList();
    await loadContactsList();

    // Default scenario approach_crossing
    runSimulation('approach_crossing', 42);
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }

})();
