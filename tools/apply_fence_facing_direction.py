import os

app_js_path = r'D:\Simulation For DT\prw-wild-digital-twin\src\prw_wild\web\static\app.js'
with open(app_js_path, 'r', encoding='utf-8') as f:
    content = f.read()

# 1. Update modelForwardAxis to (-1, 0, 0) so the elephant's face, tusks, and trunk face fence & sensors
target1 = 'modelForwardAxis: new THREE.Vector3(1, 0, 0),'
replacement1 = 'modelForwardAxis: new THREE.Vector3(-1, 0, 0),'
assert target1 in content, "Could not find modelForwardAxis"
content = content.replace(target1, replacement1, 1)

# 2. Update heading formula for legacy scalar sync
target2 = 'elephantLastValidHeading = Math.atan2(-this.lastValidDirection.z, this.lastValidDirection.x);'
replacement2 = 'elephantLastValidHeading = Math.atan2(this.lastValidDirection.z, -this.lastValidDirection.x);'
assert target2 in content, "Could not find elephantLastValidHeading formula"
content = content.replace(target2, replacement2)

# 3. Update fallbackGroup.rotation.y to Math.PI so the fallback model aligns with GLB local -X forward axis
target3 = 'fallbackGroup.rotation.y = 0;'
replacement3 = 'fallbackGroup.rotation.y = Math.PI;'
if target3 in content:
    content = content.replace(target3, replacement3, 1)

with open(app_js_path, 'w', encoding='utf-8') as f:
    f.write(content)

print("SUCCESS: Updated app.js so elephant face points towards fence and sensors!")

