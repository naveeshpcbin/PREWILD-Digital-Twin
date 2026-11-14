APP_JS = r"D:\Simulation For DT\prw-wild-digital-twin\src\prw_wild\web\static\app.js"

with open(APP_JS, "r", encoding="utf-8") as f:
    lines = f.readlines()

new_lines = []
skip = False
i = 0
while i < len(lines):
    line = lines[i]
    
    # 1. Clean buildFarmStructures: remove crude shedGroup and crop_field.glb
    if "function buildFarmStructures() {" in line:
        new_lines.append(line)
        new_lines.append("    // Production Watchtower Machan (High-Fidelity Timber Observation Platform)\n")
        new_lines.append("    if (window.THREE && typeof THREE.GLTFLoader === 'function') {\n")
        new_lines.append("      const loader = new THREE.GLTFLoader();\n")
        new_lines.append("      loader.load('assets/environment/farmland/watchtower_machan.glb', (gltf) => {\n")
        new_lines.append("        const machan = gltf.scene;\n")
        new_lines.append("        machan.name = 'Blender_Watchtower_Machan';\n")
        new_lines.append("        machan.position.set(118, getTerrainElevation(118, 102), 102);\n")
        new_lines.append("        machan.scale.set(1.15, 1.15, 1.15);\n")
        new_lines.append("        machan.traverse((c) => { if (c.isMesh) { c.castShadow = true; c.receiveShadow = true; } });\n")
        new_lines.append("        threeScene.add(machan);\n")
        new_lines.append("        console.log('[PRW-Wild] Loaded Blender Production Watchtower Machan GLB');\n")
        new_lines.append("      }, undefined, (e) => { console.warn('[PRW-Wild] Machan note:', e);\n")
        new_lines.append("      });\n")
        new_lines.append("    }\n")
        new_lines.append("  }\n")
        
        # skip until end of old buildFarmStructures
        while i < len(lines) and not ("function buildRouterModel()" in lines[i]):
            i += 1
        continue
        
    # 2. Duplicate pond basin in initMultiAnimalEcosystem
    if "// Production Carved Pond Basin GLB (Blender Production World)" in line:
        new_lines.append("    // Natural pond basin and water surface rendered once from Blender in buildContinuousTerrain.\n")
        # skip until end of that loader block
        while i < len(lines) and not ("// 2. Preload Species 3D GLB Models" in lines[i]):
            i += 1
        continue
        
    new_lines.append(line)
    i += 1

with open(APP_JS, "w", encoding="utf-8") as f:
    f.writelines(new_lines)

print("Final cleanup applied to app.js successfully!")

