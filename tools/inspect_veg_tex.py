import bpy
import os

for f in ['forest_shrub.glb', 'forest_ferns.glb', 'shrub_01.glb', 'boulder_01.glb']:
    p = os.path.join(r"D:\Simulation For DT\prw-wild-digital-twin\src\prw_wild\web\static\assets\environment", 
                     'vegetation' if 'forest' in f else ('rocks' if 'boulder' in f else 'vegetation'), f)
    if not os.path.exists(p):
        p = os.path.join(r"D:\Simulation For DT\prw-wild-digital-twin\src\prw_wild\web\static\assets\environment\vegetation", f)
    if os.path.exists(p):
        bpy.ops.wm.read_factory_settings(use_empty=True)
        bpy.ops.import_scene.gltf(filepath=p)
        print(f"\nAsset: {f}")
        for img in bpy.data.images:
            print(f"  Image: {img.name}, size={img.size}, channels={img.channels}")

