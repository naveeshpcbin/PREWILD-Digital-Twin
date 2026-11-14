import bpy
import os
import shutil

PROJECT_DIR = r"D:\Simulation For DT\prw-wild-digital-twin"
STATIC_ANIM_DIR = os.path.join(PROJECT_DIR, "src", "prw_wild", "web", "static", "assets", "animals")
ASSET_ANIM_DIR = os.path.join(PROJECT_DIR, "assets", "animals")

targets = [STATIC_ANIM_DIR, ASSET_ANIM_DIR]

print("=== Starting Complete Asset Cleaning ===")

for tdir in targets:
    if not os.path.exists(tdir):
        continue
    for fn in sorted(os.listdir(tdir)):
        if not fn.endswith(".glb"):
            continue
        fp = os.path.join(tdir, fn)
        bpy.ops.wm.read_factory_settings(use_empty=True)
        try:
            bpy.ops.import_scene.gltf(filepath=fp)
        except Exception as e:
            print(f"Error importing {fn}: {e}")
            continue

        removed = []
        for o in list(bpy.data.objects):
            name_lower = o.name.lower()
            if any(junk in name_lower for junk in ["icosphere", "cube", "camera", "light"]) or o.type in ["CAMERA", "LIGHT"]:
                removed.append(o.name)
                bpy.data.objects.remove(o, do_unlink=True)

        # Ensure materials are vibrant and visible
        for mat in bpy.data.materials:
            if mat.name.lower() in ["dots stroke", "material"]:
                continue
            if mat.use_nodes:
                bsdf = mat.node_tree.nodes.get("Principled BSDF")
                if bsdf:
                    # If this is elephant, ensure base color is nice and bright so texture is clear
                    if "elephant" in fn.lower():
                        bsdf.inputs["Roughness"].default_value = 0.65
                        bsdf.inputs["Base Color"].default_value = (1.0, 1.0, 1.0, 1.0)

        # Select all remaining objects and export cleanly
        bpy.ops.object.select_all(action='SELECT')
        bpy.ops.export_scene.gltf(
            filepath=fp,
            export_format='GLB',
            use_selection=True,
            export_skins=True,
            export_animations=True,
            export_apply=False
        )
        print(f"Cleaned {fn}: removed {removed}")

print("=== All animal GLBs cleaned successfully ===")

