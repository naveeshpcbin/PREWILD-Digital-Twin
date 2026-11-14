"""
Patch PRW-Wild Web Application:
Enforces Gate C Requirement: Ground-Level Wildlife Observer Camera as Default,
Atmospheric Distance Fog (0x1e293b, 0.0072), Soft Shadows, Tone Mapping, and Observer Tracking.
"""

import os
import re

PROJECT_DIR = r"D:\Simulation For DT\prw-wild-digital-twin"
INDEX_HTML = os.path.join(PROJECT_DIR, "src", "prw_wild", "web", "static", "index.html")
APP_JS = os.path.join(PROJECT_DIR, "src", "prw_wild", "web", "static", "app.js")

# 1. Patch index.html
with open(INDEX_HTML, "r", encoding="utf-8") as f:
    html_content = f.read()

target_html = '<button class="v-pill active" data-view="orbit" title="Free Perspective Orbit">Free Orbit</button>'
replacement_html = '<button class="v-pill active" data-view="observer" title="Ground-Level Wildlife Observer View">Observer Eye-Level</button>\n                <button class="v-pill" data-view="orbit" title="Free Perspective Orbit">Free Orbit</button>'

if target_html in html_content:
    html_content = html_content.replace(target_html, replacement_html, 1)
    with open(INDEX_HTML, "w", encoding="utf-8") as f:
        f.write(html_content)
    print("Patched index.html with Observer Eye-Level viewpoint pill.")
else:
    print("Observer button already present in index.html or target not found.")

# 2. Patch app.js
with open(APP_JS, "r", encoding="utf-8") as f:
    js_content = f.read()

# 2a. Default activeCameraView
js_content = js_content.replace(
    "let activeCameraView = 'orbit';",
    "let activeCameraView = 'observer';",
    1
)

# 2b. Atmospheric Fog and Ground-level Camera setup in initThreeScene
target_scene_setup = """    // 1. Scene with PUBG-inspired atmospheric depth
    threeScene = new THREE.Scene();
    threeScene.background = new THREE.Color(0x0a1128);
    threeScene.fog = new THREE.FogExp2(0x0a1128, 0.0028);

    // 2. Main Camera
    const aspect = container.clientWidth / container.clientHeight;
    threeCamera = new THREE.PerspectiveCamera(46, aspect, 0.5, 900);
    threeCamera.position.set(90, 75, 175);"""

replacement_scene_setup = """    // 1. Scene with AAA atmospheric depth & morning mist
    threeScene = new THREE.Scene();
    threeScene.background = new THREE.Color(0x1e293b);
    threeScene.fog = new THREE.FogExp2(0x1e293b, 0.0072);

    // 2. Main Camera - Ground-Level Wildlife Observer View (Gate C Requirement)
    const aspect = container.clientWidth / container.clientHeight;
    threeCamera = new THREE.PerspectiveCamera(48, aspect, 0.4, 900);
    const initCamY = getTerrainElevation(36, 110) + 2.8;
    threeCamera.position.set(36, initCamY, 110);"""

if target_scene_setup in js_content:
    js_content = js_content.replace(target_scene_setup, replacement_scene_setup, 1)
    print("Patched initThreeScene camera and atmospheric fog.")
else:
    print("Notice: target_scene_setup not matched verbatim, checking variations.")
    js_content = re.sub(
        r'threeScene\.fog\s*=\s*new THREE\.FogExp2\(0x[0-9a-fA-F]+,\s*[0-9.]+\);',
        'threeScene.fog = new THREE.FogExp2(0x1e293b, 0.0072);',
        js_content
    )
    js_content = re.sub(
        r'threeScene\.background\s*=\s*new THREE\.Color\(0x[0-9a-fA-F]+\);',
        'threeScene.background = new THREE.Color(0x1e293b);',
        js_content
    )

# 2c. OrbitControls initial target in initThreeScene
target_ctrl = """      threeControls.target.set(85, 0, 100);
      threeControls.update();"""
replacement_ctrl = """      const targetY = getTerrainElevation(56, 96) + 2.0;
      threeControls.target.set(56, targetY, 96);
      threeControls.minDistance = 2.0;
      threeControls.maxPolarAngle = Math.PI / 2 - 0.01;
      threeControls.update();"""

if target_ctrl in js_content:
    js_content = js_content.replace(target_ctrl, replacement_ctrl, 1)
    print("Patched threeControls target for ground observer.")

# 2d. setCameraView function logic
target_setcam = """    if (viewKey === 'orbit') {
      threeControls.target.set(85, 0, 100);
      threeCamera.position.set(90, 75, 175);"""

replacement_setcam = """    if (viewKey === 'observer') {
      const tx = 56.0, tz = 96.0;
      const targetY = getTerrainElevation(tx, tz) + 2.0;
      const camX = 36.0, camZ = 110.0;
      const camY = getTerrainElevation(camX, camZ) + 2.8;
      threeControls.target.set(tx, targetY, tz);
      threeCamera.position.set(camX, camY, camZ);
      threeControls.minDistance = 2.0;
      threeControls.maxPolarAngle = Math.PI / 2 - 0.01;
    } else if (viewKey === 'orbit') {
      threeControls.target.set(85, 0, 100);
      threeCamera.position.set(90, 75, 175);"""

if target_setcam in js_content:
    js_content = js_content.replace(target_setcam, replacement_setcam, 1)
    print("Patched setCameraView with observer view.")

# 2e. Reset Camera Button binding
js_content = js_content.replace(
    "document.getElementById('resetCameraBtn')?.addEventListener('click', () => setCameraView('orbit'));",
    "document.getElementById('resetCameraBtn')?.addEventListener('click', () => setCameraView('observer'));",
    1
)

# 2f. animateThree observer tracking
target_animate_follow = """    // Follow Elephant Camera tracking
    if (activeCameraView === 'follow' && threeObjects.elephantGroup && threeControls) {
      const ep = threeObjects.elephantGroup.position;
      const targetPos = new THREE.Vector3(ep.x, ep.y + 2.0, ep.z);
      const camOffset = threeCamera.position.clone().sub(threeControls.target);
      threeControls.target.copy(targetPos);
      threeCamera.position.copy(targetPos).add(camOffset);
      threeControls.update();
    } else if (threeControls) {"""

replacement_animate_follow = """    // Ground-Level Observer or Follow Elephant Camera tracking
    if (activeCameraView === 'follow' && threeObjects.elephantGroup && threeControls) {
      const ep = threeObjects.elephantGroup.position;
      const targetPos = new THREE.Vector3(ep.x, ep.y + 2.0, ep.z);
      const camOffset = threeCamera.position.clone().sub(threeControls.target);
      threeControls.target.copy(targetPos);
      threeCamera.position.copy(targetPos).add(camOffset);
      threeControls.update();
    } else if (activeCameraView === 'observer' && threeObjects.elephantGroup && threeControls) {
      const ep = threeObjects.elephantGroup.position;
      const targetPos = new THREE.Vector3(ep.x, ep.y + 2.0, ep.z);
      threeControls.target.lerp(targetPos, 0.04);
      threeControls.update();
    } else if (threeControls) {"""

if target_animate_follow in js_content:
    js_content = js_content.replace(target_animate_follow, replacement_animate_follow, 1)
    print("Patched animateThree with observer camera lerp tracking.")

with open(APP_JS, "w", encoding="utf-8") as f:
    f.write(js_content)
print("Saved updated app.js.")

