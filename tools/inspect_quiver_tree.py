import bpy
import os

PROJECT_DIR = r"D:\Simulation For DT\prw-wild-digital-twin"
fbx_p = os.path.join(PROJECT_DIR, "assets", "downloads", "polyhaven", "quiver_tree_01_1k.fbx")

bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.fbx(filepath=fbx_p)

print("Objects in quiver_tree_01_1k.fbx:")
for o in bpy.data.objects:
    print(f"  {o.name} ({o.type}), bounds={[round(v, 2) for v in o.dimensions]}")
    if hasattr(o.data, 'materials'):
        print(f"    mats: {[m.name for m in o.data.materials]}")

