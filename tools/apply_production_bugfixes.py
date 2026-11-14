import os
import re

PROJECT_DIR = r"D:\Simulation For DT\prw-wild-digital-twin"
SERVER_PY = os.path.join(PROJECT_DIR, "src", "prw_wild", "web", "server.py")
APP_JS = os.path.join(PROJECT_DIR, "src", "prw_wild", "web", "static", "app.js")

# 1. PATCH SERVER.PY
with open(SERVER_PY, "r", encoding="utf-8") as f:
    server_content = f.read()

# Add ECOSYSTEM_LOCK if not present
if "ECOSYSTEM_LOCK = threading.RLock()" not in server_content:
    server_content = server_content.replace(
        "GLOBAL_ECOSYSTEM = PopulationEcosystem(population_size=75, seed=42)",
        "ECOSYSTEM_LOCK = threading.RLock()\nGLOBAL_ECOSYSTEM = PopulationEcosystem(population_size=75, seed=42)"
    )

# Safe ecosystem step with lock and try...except
old_step_block = """        if path == "/api/ecosystem/step":
            dt = float(payload.get("dt", 0.5))
            snapshots = GLOBAL_ECOSYSTEM.step(dt)

            # Three-layer detection occupancy:
            # Layer 1: [45.0, 70.0), Layer 2: [70.0, 85.0), Layer 3: >= 85.0
            layer_counts = {1: 0, 2: 0, 3: 0}
            for a in GLOBAL_ECOSYSTEM.agents:
                px = a.position.x
                if 45.0 <= px < 70.0:
                    layer_counts[1] += 1
                elif 70.0 <= px < 85.0:
                    layer_counts[2] += 1
                elif px >= 85.0:
                    layer_counts[3] += 1

            hw_events = GLOBAL_HARDWARE_MANAGER.process_simulation_occupancy(layer_counts)

            self._send_json({
                "time_s": GLOBAL_ECOSYSTEM.time_s,
                "agents": snapshots,
                "layer_counts": layer_counts,
                "hardware_events": [e.to_dict() for e in hw_events],
                "hardware_status": GLOBAL_HARDWARE_MANAGER.get_status(),
                "resources": [
                    {
                        "patch_id": r.patch_id,
                        "resource_type": r.resource_type,
                        "current_amount": round(r.current_amount, 1),
                        "max_capacity": r.max_capacity,
                    }
                    for r in GLOBAL_ECOSYSTEM.resources
                ]
            })
            return"""

new_step_block = """        if path == "/api/ecosystem/step":
            try:
                dt = float(payload.get("dt", 0.5))
                with ECOSYSTEM_LOCK:
                    snapshots = GLOBAL_ECOSYSTEM.step(dt)
                    layer_counts = {1: 0, 2: 0, 3: 0}
                    for a in GLOBAL_ECOSYSTEM.agents:
                        px = a.position.x
                        if 45.0 <= px < 70.0:
                            layer_counts[1] += 1
                        elif 70.0 <= px < 85.0:
                            layer_counts[2] += 1
                        elif px >= 85.0:
                            layer_counts[3] += 1

                    hw_events = GLOBAL_HARDWARE_MANAGER.process_simulation_occupancy(layer_counts)
                    cur_time = GLOBAL_ECOSYSTEM.time_s
                    resources = [
                        {
                            "patch_id": r.patch_id,
                            "resource_type": r.resource_type,
                            "current_amount": round(r.current_amount, 1),
                            "max_capacity": r.max_capacity,
                        }
                        for r in GLOBAL_ECOSYSTEM.resources
                    ]

                self._send_json({
                    "time_s": cur_time,
                    "agents": snapshots,
                    "layer_counts": layer_counts,
                    "hardware_events": [e.to_dict() for e in hw_events],
                    "hardware_status": GLOBAL_HARDWARE_MANAGER.get_status(),
                    "resources": resources
                })
            except Exception as e:
                import traceback
                print(f"[PRW-Wild Server] Ecosystem step error: {e}")
                self._send_json({
                    "time_s": 0.0,
                    "agents": [],
                    "layer_counts": {1: 0, 2: 0, 3: 0},
                    "hardware_events": [],
                    "hardware_status": GLOBAL_HARDWARE_MANAGER.get_status(),
                    "resources": [],
                    "warning": str(e)
                })
            return"""

# Normalize line endings before replace
server_content = server_content.replace("\r\n", "\n")
old_step_block_norm = old_step_block.replace("\r\n", "\n")
new_step_block_norm = new_step_block.replace("\r\n", "\n")

if old_step_block_norm in server_content:
    server_content = server_content.replace(old_step_block_norm, new_step_block_norm)
    print("[Server] Successfully patched /api/ecosystem/step with RLock and fault tolerance.")
else:
    print("[Server] Warning: old_step_block not found directly in server.py")

# Lock ecosystem reset & inject
server_content = server_content.replace(
    "GLOBAL_ECOSYSTEM = PopulationEcosystem(population_size=pop_sz, seed=seed)",
    "with ECOSYSTEM_LOCK:\n                GLOBAL_ECOSYSTEM = PopulationEcosystem(population_size=pop_sz, seed=seed)"
)
server_content = server_content.replace(
    "ok = GLOBAL_ECOSYSTEM.inject_event(aid, intent)",
    "with ECOSYSTEM_LOCK:\n                ok = GLOBAL_ECOSYSTEM.inject_event(aid, intent)"
)

# Safe seed parsing in /api/run
server_content = server_content.replace(
    'seed = payload.get("seed")',
    'raw_seed = payload.get("seed")\n            seed = int(raw_seed) if raw_seed is not None and str(raw_seed).lstrip("-").isdigit() else None'
)

with open(SERVER_PY, "w", encoding="utf-8") as f:
    f.write(server_content)
print("[Server] Patched server.py successfully.")


# 2. PATCH APP.JS
with open(APP_JS, "r", encoding="utf-8") as f:
    app_content = f.read()
app_content = app_content.replace("\r\n", "\n")

# A. Elephant visual orientation: prodModel.rotation.y = Math.PI / 2
app_content = app_content.replace(
    "prodModel.rotation.y = -Math.PI / 2;",
    "prodModel.rotation.y = Math.PI / 2;"
)
print("[App] Patched prodModel.rotation.y = Math.PI / 2 (aligning head to standard -Z forward).")

# B. Elephant forward heading in syncThreeScene
old_heading_sync = """      const speed = Math.hypot(animal.vx, animal.vy);
      if (speed > 0.05) {
        // True forward heading: Math.atan2(vx, vz) where vz is animal.vy in 2D simulation
        const targetHeading = Math.atan2(animal.vx, animal.vy);"""

new_heading_sync = """      const speed = Math.hypot(animal.vx, animal.vy);
      if (speed > 0.05) {
        // True forward heading: for model facing standard -Z, forward heading is Math.atan2(-vx, -vy)
        const targetHeading = Math.atan2(-animal.vx, -animal.vy);"""

if old_heading_sync in app_content:
    app_content = app_content.replace(old_heading_sync, new_heading_sync)
    print("[App] Patched syncThreeScene targetHeading to Math.atan2(-animal.vx, -animal.vy).")
else:
    print("[App] Warning: old_heading_sync not found directly.")

# C. Initial heading calculation in loadScenario and reset
app_content = app_content.replace(
    "elephantLastValidHeading = -Math.atan2(initialAnimal.vy, initialAnimal.vx);",
    "elephantLastValidHeading = Math.atan2(-initialAnimal.vx, -initialAnimal.vy);"
)
print("[App] Patched elephantLastValidHeading initial formulas.")

# D. Multi-Animal forward heading
app_content = app_content.replace(
    "targetHeading: -agent.heading_rad,",
    "targetHeading: Math.atan2(-agent.velocity.x, -agent.velocity.y),"
)
app_content = app_content.replace(
    "item.targetHeading = Math.atan2(a.velocity.x, a.velocity.y);",
    "item.targetHeading = Math.atan2(-a.velocity.x, -a.velocity.y);"
)
print("[App] Patched multi-animal heading formulas.")

# E. Multi-animal elephant bull alignment
app_content = app_content.replace(
    "modelMesh = tmpl.scene.clone(true);",
    """modelMesh = tmpl.scene.clone(true);
        if (vKey === 'asian_elephant_bull' || vKey === 'asian_elephant') {
          modelMesh.rotation.y = Math.PI / 2;
        }"""
)
app_content = app_content.replace(
    "const newMesh = tmpl.scene.clone(true);\n        item.group.add(newMesh);",
    """const newMesh = tmpl.scene.clone(true);
        if (key === 'asian_elephant_bull' || key === 'asian_elephant') {
          newMesh.rotation.y = Math.PI / 2;
        }
        item.group.add(newMesh);"""
)

# F. Procedural animal fallback head orientation
app_content = app_content.replace(
    "head.position.set(0, 1.2, 0.8);",
    "head.position.set(0, 1.2, -0.8);"
)

# G. Fix orbitControls -> threeControls in focusAnimalCamera
app_content = app_content.replace(
    "if (orbitControls && threeCamera) {\n      orbitControls.target.set(targetPos.x, targetPos.y + 1.5, targetPos.z);\n      threeCamera.position.set(targetPos.x - 12, targetPos.y + 8, targetPos.z + 14);\n      orbitControls.update();",
    "if (threeControls && threeCamera) {\n      threeControls.target.set(targetPos.x, targetPos.y + 1.5, targetPos.z);\n      threeCamera.position.set(targetPos.x - 12, targetPos.y + 8, targetPos.z + 14);\n      threeControls.update();"
)
print("[App] Fixed orbitControls -> threeControls in focusAnimalCamera.")

# H. Fix tall grass alpha billboard cutout rendering
old_grass_traverse = """              inst.traverse(c => { if (c.isMesh) { c.receiveShadow = true; } });"""
new_grass_traverse = """              inst.traverse(c => {
                if (c.isMesh) {
                  c.receiveShadow = true;
                  if (c.material) {
                    c.material.transparent = true;
                    c.material.alphaTest = 0.5;
                    c.material.depthWrite = true;
                    c.material.side = THREE.DoubleSide;
                  }
                }
              });"""
if old_grass_traverse in app_content:
    app_content = app_content.replace(old_grass_traverse, new_grass_traverse)
    print("[App] Patched tall grass alphaTest and depthWrite.")

# I. Null-guards for ecosystem backend stepping
app_content = app_content.replace(
    "multiAnimalPopulation = data.agents || [];",
    "multiAnimalPopulation = Array.isArray(data.agents) ? data.agents : [];"
)
app_content = app_content.replace(
    "if (!listEl || !multiAnimalPopulation) return;",
    "if (!listEl || !Array.isArray(multiAnimalPopulation)) return;"
)

with open(APP_JS, "w", encoding="utf-8") as f:
    f.write(app_content)
print("[App] Patched app.js successfully.")

