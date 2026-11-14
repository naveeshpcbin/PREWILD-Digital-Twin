"""Patch server.py to expose PRW-Wild physical hardware control endpoints and integrate layer occupancy."""
from pathlib import Path

server_path = Path(r"D:\Simulation For DT\prw-wild-digital-twin\src\prw_wild\web\server.py")
content = server_path.read_text(encoding="utf-8")

# 1. Add imports
import_target = "from prw_wild.vision import ("
import_addition = """from prw_wild.hardware.control_service import (
    GLOBAL_HARDWARE_MANAGER,
    HardwareOperatingMode,
    LayerAction,
)
from prw_wild.vision import ("""
assert import_target in content, "import_target not found"
content = content.replace(import_target, import_addition, 1)

# 2. Add GET endpoint for /api/hardware/status
status_get_target = '        if path == "/api/hardware/wiring":'
status_get_addition = """        if path == "/api/hardware/status":
            self._send_json(GLOBAL_HARDWARE_MANAGER.get_status())
            return

        if path == "/api/hardware/wiring":"""
assert status_get_target in content, "status_get_target not found"
content = content.replace(status_get_target, status_get_addition, 1)

# 3. Add POST endpoints for /api/hardware/mode, /api/hardware/command, /api/hardware/emergency_stop
mode_post_target = '        if path == "/api/test-dispatch":'
mode_post_addition = """        if path == "/api/hardware/mode":
            mode_str = payload.get("mode", "SIMULATION_ONLY")
            res = GLOBAL_HARDWARE_MANAGER.set_mode(mode_str)
            self._send_json(res)
            return

        if path == "/api/hardware/command":
            layer = int(payload.get("layer", 1))
            action = payload.get("action", "OFF")
            res = GLOBAL_HARDWARE_MANAGER.send_manual_command(layer, action)
            self._send_json(res.to_dict())
            return

        if path == "/api/hardware/emergency_stop":
            results = GLOBAL_HARDWARE_MANAGER.emergency_all_off()
            self._send_json({
                "success": True,
                "action": "EMERGENCY_ALL_OFF",
                "results": [r.to_dict() for r in results]
            })
            return

        if path == "/api/test-dispatch":"""
assert mode_post_target in content, "mode_post_target not found"
content = content.replace(mode_post_target, mode_post_addition, 1)

# 4. Integrate layer occupancy in /api/ecosystem/step
step_target = """        if path == "/api/ecosystem/step":
            dt = float(payload.get("dt", 0.5))
            snapshots = GLOBAL_ECOSYSTEM.step(dt)
            self._send_json({
                "time_s": GLOBAL_ECOSYSTEM.time_s,
                "agents": snapshots,
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

step_replacement = """        if path == "/api/ecosystem/step":
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

assert step_target in content, "step_target not found"
content = content.replace(step_target, step_replacement, 1)

server_path.write_text(content, encoding="utf-8")
print("Successfully patched server.py with hardware endpoints and occupancy tracking!")

