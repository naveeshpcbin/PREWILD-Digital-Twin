import bpy
import os

anim_dirs = [
    r"D:\Simulation For DT\prw-wild-digital-twin\src\prw_wild\web\static\assets\animals",
    r"D:\Simulation For DT\prw-wild-digital-twin\assets\animals"
]

print("=== Starting Batch Removal of Stray Icospheres from Animal GLBs ===")

for target_dir in anim_dirs:
    if not os.path.exists(target_dir):
        continue
    print(f"\nProcessing directory: {target_dir}")
    for fn in sorted(os.listdir(target_dir)):
        if not fn.endswith('.glb'):
            continue
        fp = os.path.join(target_dir, fn)
        bpy.ops.wm.read_factory_settings(use_empty=True)
        try:
            bpy.ops.import_scene.gltf(filepath=fp)
        except Exception as e:
            print(f"  [ERROR] {fn}: Failed to import: {e}")
            continue
        
        removed = 0
        for o in list(bpy.data.objects):
            if "icosphere" in o.name.lower():
                bpy.data.objects.remove(o, do_unlink=True)
                removed += 1
                
        if removed > 0:
            bpy.ops.object.select_all(action='SELECT')
            bpy.ops.export_scene.gltf(
                filepath=fp,
                export_format='GLB',
                use_selection=True,
                export_skins=True,
                export_animations=True,
                export_apply=True
            )
            print(f"  [FIXED] {fn}: Removed {removed} stray icosphere(s)")
        else:
            print(f"  [CLEAN] {fn}: No stray objects found")

print("\n=== Batch Cleaning Complete ===")

