import bpy
import os

fp = r"D:\Simulation For DT\prw-wild-digital-twin\src\prw_wild\web\static\assets\animals\asian_elephant_production.glb"

bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.gltf(filepath=fp)

# Remove any Icosphere or unwanted leftover objects
for o in list(bpy.data.objects):
    if "icosphere" in o.name.lower():
        print(f"Removing stray object: {o.name}")
        bpy.data.objects.remove(o, do_unlink=True)

# Find mesh object
mesh_obj = next((o for o in bpy.data.objects if o.type == 'MESH'), None)
arm_obj = next((o for o in bpy.data.objects if o.type == 'ARMATURE'), None)

if mesh_obj:
    print(f"Found elephant mesh: {mesh_obj.name}, dimensions: {mesh_obj.dimensions}")
    # Enhance PBR Material
    mat = bpy.data.materials.new(name="M_AsianElephant_PBR")
    mat.use_nodes = True
    bsdf = mat.node_tree.nodes.get("Principled BSDF")
    if bsdf:
        # Realistic elephant hide albedo: warm slate leathery grey
        bsdf.inputs['Base Color'].default_value = (0.28, 0.27, 0.26, 1.0)
        bsdf.inputs['Roughness'].default_value = 0.88
        bsdf.inputs['Metallic'].default_value = 0.02
    
    mesh_obj.data.materials.clear()
    mesh_obj.data.materials.append(mat)

# Select all remaining objects (Mesh + Armature)
bpy.ops.object.select_all(action='SELECT')
bpy.ops.export_scene.gltf(
    filepath=fp,
    export_format='GLB',
    use_selection=True,
    export_skins=True,
    export_animations=True,
    export_apply=True
)

# Also mirror to assets/animals/asian_elephant_production.glb and asian_elephant.glb
root_fp = r"D:\Simulation For DT\prw-wild-digital-twin\assets\animals\asian_elephant_production.glb"
import shutil
shutil.copy2(fp, root_fp)
shutil.copy2(fp, r"D:\Simulation For DT\prw-wild-digital-twin\src\prw_wild\web\static\assets\animals\asian_elephant.glb")
shutil.copy2(fp, r"D:\Simulation For DT\prw-wild-digital-twin\assets\animals\asian_elephant.glb")

print("SUCCESS: Cleaned and enhanced asian_elephant_production.glb")

