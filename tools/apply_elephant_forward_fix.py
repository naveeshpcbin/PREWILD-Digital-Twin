import os

app_js_path = r'D:\Simulation For DT\prw-wild-digital-twin\src\prw_wild\web\static\app.js'
with open(app_js_path, 'r', encoding='utf-8') as f:
    content = f.read()

# 1. Fallback group rotation
target1 = 'fallbackGroup.rotation.y = Math.PI / 2;'
replacement1 = 'fallbackGroup.rotation.y = 0;'
assert target1 in content, f"Missing: {target1}"
content = content.replace(target1, replacement1, 1)

# 2. Production model rotation in visualGroup
target2 = 'prodModel.rotation.y = -Math.PI / 2;\r\n          visualGroup.rotation.y = 0;'
if target2 not in content:
    target2 = 'prodModel.rotation.y = -Math.PI / 2;\n          visualGroup.rotation.y = 0;'
assert target2 in content, f"Missing: target2"
replacement2 = target2.replace('prodModel.rotation.y = -Math.PI / 2;', 'prodModel.rotation.y = 0;')
content = content.replace(target2, replacement2, 1)

# 3. Heading in syncThreeScene
target3 = 'const targetHeading = Math.atan2(-animal.vx, -animal.vy);'
replacement3 = 'const targetHeading = Math.atan2(-animal.vy, animal.vx);'
assert target3 in content, f"Missing: {target3}"
content = content.replace(target3, replacement3, 1)

# 4. Heading reset in runSimulation & btnReset
target4 = 'elephantLastValidHeading = Math.atan2(-initialAnimal.vx, -initialAnimal.vy);'
replacement4 = 'elephantLastValidHeading = Math.atan2(-initialAnimal.vy, initialAnimal.vx);'
c4 = content.count(target4)
assert c4 >= 2, f"Expected at least 2 occurrences of {target4}, found {c4}"
content = content.replace(target4, replacement4)

# 5. Multi-animal Mode F initial rotation
target5 = 'rootGroup.rotation.y = Math.atan2(agent.velocity.x, agent.velocity.y);'
replacement5 = 'rootGroup.rotation.y = Math.atan2(-agent.velocity.x, -agent.velocity.y);'
if target5 in content:
    content = content.replace(target5, replacement5, 1)

# 6. Mode F elephant orientation
target6 = "if (vKey === 'asian_elephant_bull' || vKey === 'asian_elephant') {\r\n          modelMesh.rotation.y = Math.PI / 2;\r\n        }"
if target6 not in content:
    target6 = "if (vKey === 'asian_elephant_bull' || vKey === 'asian_elephant') {\n          modelMesh.rotation.y = Math.PI / 2;\n        }"
if target6 in content:
    replacement6 = "if (vKey === 'asian_elephant_bull' || vKey === 'asian_elephant' || vKey === 'asian_elephant_cow') {\n          modelMesh.rotation.y = -Math.PI / 2;\n        }".replace('\n', '\r\n' if '\r\n' in target6 else '\n')
    content = content.replace(target6, replacement6, 1)

target7 = "if (key === 'asian_elephant_bull' || key === 'asian_elephant') {\r\n          newMesh.rotation.y = Math.PI / 2;\r\n        }"
if target7 not in content:
    target7 = "if (key === 'asian_elephant_bull' || key === 'asian_elephant') {\n          newMesh.rotation.y = Math.PI / 2;\n        }"
if target7 in content:
    replacement7 = "if (key === 'asian_elephant_bull' || key === 'asian_elephant' || key === 'asian_elephant_cow') {\n          newMesh.rotation.y = -Math.PI / 2;\n        }".replace('\n', '\r\n' if '\r\n' in target7 else '\n')
    content = content.replace(target7, replacement7, 1)

with open(app_js_path, 'w', encoding='utf-8') as f:
    f.write(content)

print("SUCCESS: app.js updated with proven forward elephant locomotion physics!")

