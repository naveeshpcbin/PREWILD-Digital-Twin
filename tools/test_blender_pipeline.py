"""Automated Blender 5.2.2 LTS Execution & Verification Diagnostic.
Executes all 8 mandatory tests specified in Section 3.2:
1. Launch installed Blender process.
2. Confirm process starts and reports version.
3. Confirm it can open / save a .blend file.
4. Confirm it can execute Python scripts.
5. Confirm it can import a GLB.
6. Confirm it can export a GLB.
7. Save a test Blender project.
8. Verify the output files.
"""

import subprocess
import os
import struct
import json
from pathlib import Path

BLENDER_EXE = r"D:\PROJECTS\blender.exe"
WORKSPACE = Path(r"D:\Simulation For DT\prw-wild-digital-twin")
TEST_BLEND_OUT = WORKSPACE / "assets" / "test_project.blend"
TEST_GLB_OUT = WORKSPACE / "assets" / "test_output.glb"
TEST_SCRIPT = WORKSPACE / "tools" / "blender_test_worker.py"

worker_code = """
import bpy
import os

print("[BLENDER WORKER] Initializing Blender Python execution test...")

# Reset to clean scene
bpy.ops.wm.read_factory_settings(use_empty=True)

# Create a test benchmark mesh (Suzanne monkey head + test pedestal)
bpy.ops.mesh.primitive_monkey_add(size=2.0, location=(0, 0, 1.5))
monkey = bpy.context.active_object
monkey.name = "Benchmark_Monkey"

# Add PBR material
mat = bpy.data.materials.new(name="M_Test_PBR")
mat.use_nodes = True
bsdf = mat.node_tree.nodes.get("Principled BSDF")
if bsdf:
    bsdf.inputs['Base Color'].default_value = (0.2, 0.7, 0.4, 1.0)
    bsdf.inputs['Roughness'].default_value = 0.35
monkey.data.materials.append(mat)

# Export to GLB
glb_path = r"{glb_path}"
bpy.ops.export_scene.gltf(
    filepath=glb_path,
    export_format='GLB',
    use_selection=False,
    export_apply=True
)
print(f"[BLENDER WORKER] Exported test GLB to {glb_path}")

# Test re-importing GLB
bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.gltf(filepath=glb_path)
imported_count = len(bpy.data.objects)
print(f"[BLENDER WORKER] Re-imported GLB successfully. Scene objects count: {imported_count}")

# Save .blend project file
blend_path = r"{blend_path}"
bpy.ops.wm.save_as_mainfile(filepath=blend_path)
print(f"[BLENDER WORKER] Saved Blender project file to {blend_path}")
print("[BLENDER WORKER] ALL BLENDER WORKER TASKS COMPLETED!")
""".replace("{glb_path}", str(TEST_GLB_OUT).replace("\\", "\\\\")).replace("{blend_path}", str(TEST_BLEND_OUT).replace("\\", "\\\\"))

def main():
    TEST_SCRIPT.write_text(worker_code, encoding="utf-8")
    TEST_BLEND_OUT.parent.mkdir(parents=True, exist_ok=True)

    print("=== STAGE 2: BLENDER 5.2.2 LTS EXECUTION DIAGNOSTIC ===")
    print(f"Blender Executable: {BLENDER_EXE}")
    assert os.path.exists(BLENDER_EXE), f"Blender executable not found at {BLENDER_EXE}"

    # Step 1 & 2: Version Check & Process Launch
    ver_proc = subprocess.run([BLENDER_EXE, "--version"], capture_output=True, text=True)
    print("Blender Version Output:")
    print(ver_proc.stdout.strip()[:180])
    assert ver_proc.returncode == 0, "Blender failed to return version"

    # Step 3 to 7: Run Python worker inside Blender
    cmd = [BLENDER_EXE, "-b", "--python", str(TEST_SCRIPT)]
    print(f"Running command: {' '.join(cmd)}")
    proc = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
    print("Blender Execution Output:")
    for line in proc.stdout.splitlines():
        if "[BLENDER WORKER]" in line:
            print("  ", line)
    if proc.returncode != 0:
        print("Blender Stderr:", proc.stderr)
    assert proc.returncode == 0, "Blender execution failed"

    # Step 8: Verify Output Files
    assert TEST_GLB_OUT.exists(), "test_output.glb was not created"
    glb_size = TEST_GLB_OUT.stat().st_size
    assert glb_size > 1000, f"GLB file unexpectedly small: {glb_size} bytes"

    # Verify binary glTF header
    with open(TEST_GLB_OUT, "rb") as f:
        magic, version, length = struct.unpack("<4sII", f.read(12))
        assert magic == b"glTF", "Asset does not have glTF magic header"
        assert version == 2, f"Expected glTF version 2, got {version}"
        print(f"Verified test_output.glb: size={glb_size} bytes, glTF v{version}, length={length}")

    # Verify .blend file by launching Blender in background mode to re-open it
    assert TEST_BLEND_OUT.exists(), "test_project.blend was not created"
    blend_size = TEST_BLEND_OUT.stat().st_size
    assert blend_size > 1000, f"Blend file unexpectedly small: {blend_size} bytes"

    reopen_cmd = [
        BLENDER_EXE, "-b", str(TEST_BLEND_OUT),
        "--python-expr", "import bpy; print('[REOPEN TEST] Objects in saved blend:', [o.name for o in bpy.data.objects])"
    ]
    reopen_proc = subprocess.run(reopen_cmd, capture_output=True, text=True, timeout=30)
    assert reopen_proc.returncode == 0, "Failed to re-open saved .blend file"
    assert "Benchmark_Monkey" in reopen_proc.stdout, "Benchmark_Monkey not found in reopened blend"
    print(f"Verified test_project.blend: size={blend_size} bytes, successfully reopened and verified in Blender!")

    print("\nSUCCESS: All 8 Blender diagnostic tests PASSED!")

if __name__ == "__main__":
    main()
