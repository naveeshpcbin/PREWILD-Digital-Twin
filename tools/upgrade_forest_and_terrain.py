import re

app_path = r"D:\Simulation For DT\prw-wild-digital-twin\src\prw_wild\web\static\app.js"
with open(app_path, "r", encoding="utf-8") as f:
    text = f.read()

# 1. Update loadPBR in PBRTextures for sRGB encoding and proper repeat tiling
old_load_pbr = """        const loadPBR = (url, rx, ry, isColor = false) => {
          const t = texLoader.load(url);
          t.wrapS = t.wrapT = THREE.RepeatWrapping;
          t.repeat.set(rx, ry);
          if (isColor && THREE.SRGBColorSpace) t.colorSpace = THREE.SRGBColorSpace;
          return t;
        };

        this.furrowSoil = loadPBR('assets/environment/terrain/farm_soil_diff.jpg', 8, 8, true);
        this.furrowSoilNor = loadPBR('assets/environment/terrain/farm_soil_nor.jpg', 8, 8, false);
        this.furrowSoilRough = loadPBR('assets/environment/terrain/farm_soil_rough.jpg', 8, 8, false);

        this.forestGround = loadPBR('assets/environment/terrain/forest_ground_diff.jpg', 10, 10, true);
        this.forestGroundNor = loadPBR('assets/environment/terrain/forest_ground_nor.jpg', 10, 10, false);
        this.forestGroundRough = loadPBR('assets/environment/terrain/forest_ground_rough.jpg', 10, 10, false);

        this.corridorMud = loadPBR('assets/environment/terrain/corridor_mud_diff.jpg', 6, 2, true);
        this.corridorMudNor = loadPBR('assets/environment/terrain/corridor_mud_nor.jpg', 6, 2, false);
        this.corridorMudRough = loadPBR('assets/environment/terrain/corridor_mud_rough.jpg', 6, 2, false);"""

new_load_pbr = """        const loadPBR = (url, rx, ry, isColor = false) => {
          const t = texLoader.load(url);
          t.wrapS = t.wrapT = THREE.RepeatWrapping;
          t.repeat.set(rx, ry);
          if (isColor) {
            if (THREE.SRGBColorSpace) t.colorSpace = THREE.SRGBColorSpace;
            else if (THREE.sRGBEncoding) t.encoding = THREE.sRGBEncoding;
          }
          return t;
        };

        this.furrowSoil = loadPBR('assets/environment/terrain/farm_soil_diff.jpg', 24, 24, true);
        this.furrowSoilNor = loadPBR('assets/environment/terrain/farm_soil_nor.jpg', 24, 24, false);
        this.furrowSoilRough = loadPBR('assets/environment/terrain/farm_soil_rough.jpg', 24, 24, false);

        this.forestGround = loadPBR('assets/environment/terrain/forest_ground_diff.jpg', 28, 26, true);
        this.forestGroundNor = loadPBR('assets/environment/terrain/forest_ground_nor.jpg', 28, 26, false);
        this.forestGroundRough = loadPBR('assets/environment/terrain/forest_ground_rough.jpg', 28, 26, false);

        this.corridorMud = loadPBR('assets/environment/terrain/corridor_mud_diff.jpg', 18, 6, true);
        this.corridorMudNor = loadPBR('assets/environment/terrain/corridor_mud_nor.jpg', 18, 6, false);
        this.corridorMudRough = loadPBR('assets/environment/terrain/corridor_mud_rough.jpg', 18, 6, false);"""

assert old_load_pbr in text, "old_load_pbr not found"
text = text.replace(old_load_pbr, new_load_pbr, 1)

# 2. Update elephant loading in app.js
old_elephant_loader = """          // Create dedicated child visual-model group for fixed axis & orientation correction
          const visualGroup = new THREE.Group();
          visualGroup.name = 'Elephant_Visual_Child_Root';
          // Fixed yaw axis correction: align loaded model's forward (+X head/trunk) with outer simulation root
          visualGroup.rotation.y = Math.PI;
          visualGroup.add(prodModel);
          threeObjects.elephantVisualGroup = visualGroup;"""

new_elephant_loader = """          // Create dedicated child visual-model group for fixed axis & orientation correction
          const visualGroup = new THREE.Group();
          visualGroup.name = 'Elephant_Visual_Child_Root';
          // Align model forward (+X trunk) with simulation heading, scaled to magnificent 1.25 life size
          visualGroup.rotation.y = 0;
          visualGroup.scale.set(1.25, 1.25, 1.25);
          visualGroup.add(prodModel);
          threeObjects.elephantVisualGroup = visualGroup;"""

assert old_elephant_loader in text, "old_elephant_loader not found"
text = text.replace(old_elephant_loader, new_elephant_loader, 1)

# 3. Enhance elephant material on load
old_mat_override = """          prodModel.traverse((child) => {
            if (child.isMesh) {
              child.castShadow = true;
              child.receiveShadow = true;
              if (child.material) {
                child.material.roughness = 0.85;
                child.material.metalness = 0.05;
              }
            }
          });"""

new_mat_override = """          prodModel.traverse((child) => {
            if (child.isMesh) {
              child.castShadow = true;
              child.receiveShadow = true;
              if (child.material) {
                child.material.color.setHex(0x605c56); // Warm leathery slate grey
                child.material.roughness = 0.72;
                child.material.metalness = 0.02;
              }
            }
          });"""

assert old_mat_override in text, "old_mat_override not found"
text = text.replace(old_mat_override, new_mat_override, 1)

with open(app_path, "w", encoding="utf-8") as f:
    f.write(text)

print("SUCCESS: Upgraded terrain textures, PBR encoding, and elephant presentation")

