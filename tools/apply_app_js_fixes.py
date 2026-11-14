import re

path = r"D:\Simulation For DT\prw-wild-digital-twin\src\prw_wild\web\static\app.js"
with open(path, "r", encoding="utf-8") as f:
    code = f.read()

# 1. Update Sky Dome and Lighting in buildSceneLighting()
target_lighting = """    // 1. Realistic Outdoor Sky Dome
    const skyGeo = new THREE.SphereGeometry(750, 32, 24);
    skyGeo.scale(-1, 1, 1);
    const skyMat = new THREE.MeshBasicMaterial({
      color: 0x8ecae6,
      side: THREE.BackSide,
    });
    const skyDome = new THREE.Mesh(skyGeo, skyMat);
    skyDome.position.set(100, 0, 100);
    threeScene.add(skyDome);

    // 2. Hemisphere Skylight (sky blue to warm soil amber) & Soft Natural Ambient
    const hemiLight = new THREE.HemisphereLight(0xe0f2fe, 0x6e5844, 1.15);
    threeScene.add(hemiLight);

    const ambientLight = new THREE.AmbientLight(0xffffff, 0.40);
    threeScene.add(ambientLight);

    // 3. Directional Sun (Warm natural daylight with soft PCF shadows)
    const dirLight = new THREE.DirectionalLight(0xfff7ed, 1.4);"""

replacement_lighting = """    // 1. Realistic Outdoor Sky Dome with Atmospheric Rayleigh Gradient (AAA Game Sky)
    const skyCanvas = document.createElement('canvas');
    skyCanvas.width = 512;
    skyCanvas.height = 512;
    const sCtx = skyCanvas.getContext('2d');
    const grad = sCtx.createLinearGradient(0, 0, 0, 512);
    // Horizon glow to zenith twilight: golden haze -> azure -> deep blue
    grad.addColorStop(0.0, '#0c2340');
    grad.addColorStop(0.35, '#1e5f8a');
    grad.addColorStop(0.70, '#569cd6');
    grad.addColorStop(0.90, '#fef08a');
    grad.addColorStop(1.0, '#fed7aa');
    sCtx.fillStyle = grad;
    sCtx.fillRect(0, 0, 512, 512);

    // Cirrus cloud wisps
    sCtx.fillStyle = 'rgba(255, 255, 255, 0.15)';
    for (let c = 0; c < 14; c++) {
      const cy = 160 + c * 16 + Math.sin(c) * 8;
      sCtx.beginPath();
      sCtx.ellipse(256 + Math.cos(c) * 110, cy, 190 + Math.sin(c) * 40, 10 + (c % 3) * 4, 0, 0, Math.PI * 2);
      sCtx.fill();
    }
    const skyTex = new THREE.CanvasTexture(skyCanvas);
    const skyGeo = new THREE.SphereGeometry(750, 32, 24);
    skyGeo.scale(-1, 1, 1);
    const skyMat = new THREE.MeshBasicMaterial({
      map: skyTex,
      side: THREE.BackSide,
    });
    const skyDome = new THREE.Mesh(skyGeo, skyMat);
    skyDome.position.set(100, 0, 100);
    threeScene.add(skyDome);

    // 2. Cinematic Hemisphere Light (warm sky to golden soil bounce fill)
    const hemiLight = new THREE.HemisphereLight(0xbae6fd, 0x54402e, 1.35);
    threeScene.add(hemiLight);

    const ambientLight = new THREE.AmbientLight(0xffeedd, 0.45);
    threeScene.add(ambientLight);

    // 3. Directional Sun (Warm natural daylight with soft PCF shadows)
    const dirLight = new THREE.DirectionalLight(0xfffaed, 1.55);"""

assert target_lighting in code, "Lighting target not found"
code = code.replace(target_lighting, replacement_lighting, 1)

# 2. Fix elephant fallbackGroup rotation
target_fallback = """    // Procedural Fallback Group
    const fallbackGroup = new THREE.Group();
    fallbackGroup.name = 'Elephant_Procedural_Fallback';
    threeObjects.elephantFallbackGroup = fallbackGroup;
    elGroup.add(fallbackGroup);"""

replacement_fallback = """    // Procedural Fallback Group (Oriented to standard glTF forward -Z)
    const fallbackGroup = new THREE.Group();
    fallbackGroup.name = 'Elephant_Procedural_Fallback';
    fallbackGroup.rotation.y = Math.PI / 2;
    threeObjects.elephantFallbackGroup = fallbackGroup;
    elGroup.add(fallbackGroup);"""

assert target_fallback in code, "Fallback target not found"
code = code.replace(target_fallback, replacement_fallback, 1)

# 3. Fix setLabMode modal dismissal
target_lab = """    if (mode === 'live') {
      if (lebBar) lebBar.classList.add('hidden');
      if (flTray) flTray.classList.add('hidden');
    } else if (mode === 'layers') {"""

replacement_lab = """    // Dismiss modal backdrops when switching away from counterfactual or layers
    if (mode !== 'counterfactual' && cfModal) cfModal.classList.add('hidden');
    if (mode !== 'layers' && layerModal) layerModal.classList.add('hidden');

    if (mode === 'live') {
      if (lebBar) lebBar.classList.add('hidden');
      if (flTray) flTray.classList.add('hidden');
    } else if (mode === 'layers') {"""

assert target_lab in code, "Lab mode target not found"
code = code.replace(target_lab, replacement_lab, 1)

# 4. Expose window.renderIndividualAnimalDirectory
target_render_fn = """    listEl.innerHTML = html;
  }

  window.focusAnimalCamera = function(animalId) {"""

replacement_render_fn = """    listEl.innerHTML = html;
  }
  window.renderIndividualAnimalDirectory = renderIndividualAnimalDirectory;

  window.focusAnimalCamera = function(animalId) {"""

assert target_render_fn in code, "renderIndividualAnimalDirectory target not found"
code = code.replace(target_render_fn, replacement_render_fn, 1)

with open(path, "w", encoding="utf-8") as f:
    f.write(code)

print("Successfully applied app.js fixes!")

