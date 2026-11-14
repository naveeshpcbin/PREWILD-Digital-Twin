import bpy
import os

assets_dir = r"D:\Simulation For DT\prw-wild-digital-twin\src\prw_wild\web\static\assets\environment"
for root, dirs, files in os.walk(assets_dir):
    for f in files:
        if f.endswith('.glb'):
            path = os.path.join(root, f)
            bpy.ops.wm.read_factory_settings(use_empty=True)
            bpy.ops.import_scene.gltf(filepath=path)
            print(f"\n==========================================")
            print(f"FILE: {f} ({os.path.getsize(path)} bytes)")
            for obj in bpy.data.objects:
                loc = [round(v, 2) for v in obj.location]
                dim = [round(v, 2) for v in obj.dimensions]
                mats = [m.name for m in obj.data.materials] if hasattr(obj.data, 'materials') else []
                poly_count = len(obj.data.polygons) if hasattr(obj.data, 'polygons') else 0
                print(f"  Obj: {obj.name} | type: {obj.type} | loc: {loc} | dim: {dim} | polys: {poly_count} | mats: {mats}")

