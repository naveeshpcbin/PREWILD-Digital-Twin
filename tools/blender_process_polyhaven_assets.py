import bpy
import mathutils
import os

PROJECT_DIR = r"D:\Simulation For DT\prw-wild-digital-twin"
DOWNLOADS_DIR = os.path.join(PROJECT_DIR, "assets", "downloads", "polyhaven")
STATIC_ENV = os.path.join(PROJECT_DIR, "src", "prw_wild", "web", "static", "assets", "environment")
ASSETS_ENV = os.path.join(PROJECT_DIR, "assets", "environment")

def clear_scene():
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete()

def export_glb(filepath):
    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    bpy.ops.export_scene.gltf(
        filepath=filepath,
        export_format='GLB',
        use_selection=False,
        export_apply=True,
        export_materials='EXPORT',
        export_yup=True
    )
    print(f"[Blender] Exported GLB: {filepath} ({os.path.getsize(filepath)/1024:.1f} KB)")

# =========================================================================
# 1. PROCESS BOULDER_01 (Clean Ground Scanned Rock, No Floating Proxies)
# =========================================================================
print("=== 1. Processing Boulder 01 ===")
clear_scene()
boulder_src = os.path.join(STATIC_ENV, "rocks", "boulder_01.glb")
if os.path.exists(boulder_src):
    bpy.ops.import_scene.gltf(filepath=boulder_src)
    # Remove all rock_PROXY_5m objects and extra LODs, keep boulder_01_LOD1 or LOD0
    keep_obj = None
    to_delete = []
    for o in bpy.data.objects:
        if o.name in ['boulder_01_LOD1', 'boulder_01_LOD0'] and keep_obj is None:
            keep_obj = o
        else:
            to_delete.append(o)
    for o in to_delete:
        bpy.data.objects.remove(o, do_unlink=True)
    
    if keep_obj:
        keep_obj.name = "Rock_Boulder_Granite"
        # Center origin at the base
        bpy.context.view_layer.objects.active = keep_obj
        keep_obj.select_set(True)
        # Recalculate bounds so bottom is at Z=0
        bbox = [keep_obj.matrix_world @ mathutils.Vector(corner) for corner in keep_obj.bound_box]
        min_z = min(v.z for v in bbox)
        keep_obj.location.z -= min_z
        bpy.ops.object.transform_apply(location=True, rotation=False, scale=False)
        
        # Export clean boulder
        target_static = os.path.join(STATIC_ENV, "rocks", "boulder_01.glb")
        export_glb(target_static)
        target_assets = os.path.join(ASSETS_ENV, "rocks", "boulder_01.glb")
        export_glb(target_assets)

# =========================================================================
# 2. PROCESS WILD ROOIBOS BUSH & SHRUBS (Genuine Poly Haven PBR Shrub)
# =========================================================================
print("=== 2. Processing Shrubs ===")
clear_scene()
bush_fbx = os.path.join(DOWNLOADS_DIR, "wild_rooibos_bush_1k.fbx")
if os.path.exists(bush_fbx):
    bpy.ops.import_scene.fbx(filepath=bush_fbx)
    # Join the bush parts into one cohesive shrub object
    bpy.ops.object.select_all(action='SELECT')
    active_bush = bpy.data.objects[0]
    bpy.context.view_layer.objects.active = active_bush
    bpy.ops.object.join()
    active_bush.name = "Forest_Shrub_Rooibos"
    
    # Setup PBR textures if available
    diff_tex = os.path.join(DOWNLOADS_DIR, "wild_rooibos_bush_Diffuse_1k.jpg")
    nor_tex = os.path.join(DOWNLOADS_DIR, "wild_rooibos_bush_nor_gl_1k.jpg")
    rough_tex = os.path.join(DOWNLOADS_DIR, "wild_rooibos_bush_Rough_1k.jpg")
    
    for mat in active_bush.data.materials:
        mat.use_nodes = True
        nodes = mat.node_tree.nodes
        links = mat.node_tree.links
        bsdf = nodes.get("Principled BSDF")
        if bsdf:
            if os.path.exists(diff_tex):
                tex_node = nodes.new("ShaderNodeTexImage")
                tex_node.image = bpy.data.images.load(diff_tex)
                links.new(tex_node.outputs["Color"], bsdf.inputs["Base Color"])
            if os.path.exists(rough_tex):
                r_node = nodes.new("ShaderNodeTexImage")
                r_node.image = bpy.data.images.load(rough_tex)
                links.new(r_node.outputs["Color"], bsdf.inputs["Roughness"])
            if os.path.exists(nor_tex):
                n_node = nodes.new("ShaderNodeTexImage")
                n_node.image = bpy.data.images.load(nor_tex)
                n_node.image.colorspace_settings.name = 'Non-Color'
                norm_map = nodes.new("ShaderNodeNormalMap")
                links.new(n_node.outputs["Color"], norm_map.inputs["Color"])
                links.new(norm_map.outputs["Normal"], bsdf.inputs["Normal"])
    
    # Scale appropriately for natural forest bush (approx 1.8m wide, 1.4m high)
    active_bush.scale = (1.5, 1.5, 1.5)
    bpy.ops.object.transform_apply(scale=True)
    
    # Export to forest_shrub.glb and shrub_01.glb
    export_glb(os.path.join(STATIC_ENV, "vegetation", "forest_shrub.glb"))
    export_glb(os.path.join(ASSETS_ENV, "vegetation", "forest_shrub.glb"))
    export_glb(os.path.join(STATIC_ENV, "vegetation", "shrub_01.glb"))

# =========================================================================
# 3. PROCESS FERN 02 (Genuine Poly Haven Forest Fern)
# =========================================================================
print("=== 3. Processing Ferns ===")
clear_scene()
fern_src = os.path.join(STATIC_ENV, "vegetation", "fern_02.glb")
if os.path.exists(fern_src):
    bpy.ops.import_scene.gltf(filepath=fern_src)
    bpy.ops.object.select_all(action='SELECT')
    if bpy.data.objects:
        active_fern = bpy.data.objects[0]
        bpy.context.view_layer.objects.active = active_fern
        bpy.ops.object.join()
        active_fern.name = "Forest_Fern_Frond_Cluster"
        active_fern.scale = (1.8, 1.8, 1.8)
        bpy.ops.object.transform_apply(scale=True)
        export_glb(os.path.join(STATIC_ENV, "vegetation", "forest_ferns.glb"))
        export_glb(os.path.join(ASSETS_ENV, "vegetation", "forest_ferns.glb"))

# =========================================================================
# 4. PROCESS TALL GRASS (Clean Poly Haven Grass Clump)
# =========================================================================
print("=== 4. Processing Grass ===")
clear_scene()
grass_src = os.path.join(STATIC_ENV, "vegetation", "grass_medium_01.glb")
if os.path.exists(grass_src):
    bpy.ops.import_scene.gltf(filepath=grass_src)
    # Remove any proxy sphere
    to_delete = [o for o in bpy.data.objects if 'sphere' in o.name.lower() or o.name == 'grass_medium_01_geometry_nodes']
    for o in to_delete:
        bpy.data.objects.remove(o, do_unlink=True)
    
    # Select remaining grass planes and join
    bpy.ops.object.select_all(action='SELECT')
    if bpy.data.objects:
        active_grass = bpy.data.objects[0]
        bpy.context.view_layer.objects.active = active_grass
        bpy.ops.object.join()
        active_grass.name = "Tall_Grass_Tuft_Natural"
        active_grass.scale = (2.2, 2.2, 2.2)
        bpy.ops.object.transform_apply(scale=True)
        export_glb(os.path.join(STATIC_ENV, "grass", "tall_grass_clump.glb"))
        export_glb(os.path.join(ASSETS_ENV, "grass", "tall_grass_clump.glb"))

# =========================================================================
# 5. RE-AUTHOR POND BASIN (Eliminate ALL Floating Spheres!)
# =========================================================================
print("=== 5. Processing Pond Basin ===")
clear_scene()
# Create smooth organic water rim and ground-clamped shoreline boulders
# 1. Gentle natural shoreline depression rim
bpy.ops.mesh.primitive_cylinder_add(radius=16.0, depth=0.8, vertices=32, location=(0, 0, -0.4))
basin = bpy.context.active_object
basin.name = "Pond_Natural_Basin"

mat_shore = bpy.data.materials.new(name="M_Pond_Shore_Natural")
mat_shore.use_nodes = True
bsdf = mat_shore.node_tree.nodes.get("Principled BSDF")
if bsdf:
    bsdf.inputs["Base Color"].default_value = (0.28, 0.22, 0.16, 1.0)
    bsdf.inputs["Roughness"].default_value = 0.92
basin.data.materials.append(mat_shore)

# 2. Reflective specular water disc at water level (Z = 0)
bpy.ops.mesh.primitive_cylinder_add(radius=15.2, depth=0.05, vertices=32, location=(0, 0, -0.05))
water = bpy.context.active_object
water.name = "Pond_Water_Surface"

mat_water = bpy.data.materials.new(name="M_Water_Specular")
mat_water.use_nodes = True
wbsdf = mat_water.node_tree.nodes.get("Principled BSDF")
if wbsdf:
    wbsdf.inputs["Base Color"].default_value = (0.04, 0.18, 0.28, 0.85)
    wbsdf.inputs["Roughness"].default_value = 0.08
    wbsdf.inputs["Metallic"].default_value = 0.15
    if "Transmission Weight" in wbsdf.inputs:
        wbsdf.inputs["Transmission Weight"].default_value = 0.75
    elif "Transmission" in wbsdf.inputs:
        wbsdf.inputs["Transmission"].default_value = 0.75
water.data.materials.append(mat_water)

# 3. Ground-level shoreline boulders firmly resting at water boundary (Z = 0, NOT Z = 16.5m in the sky!)
boulders = []
mat_boulder = bpy.data.materials.new(name="M_Pond_Shore_Boulder")
mat_boulder.use_nodes = True
bbsdf = mat_boulder.node_tree.nodes.get("Principled BSDF")
if bbsdf:
    bbsdf.inputs["Base Color"].default_value = (0.35, 0.36, 0.38, 1.0)
    bbsdf.inputs["Roughness"].default_value = 0.85

import math
for i in range(8):
    ang = (i / 8.0) * math.pi * 2.0
    bx = math.cos(ang) * 14.8
    by = math.sin(ang) * 14.8
    # Z coordinate is resting on the shore rim at Z = -0.1 to 0.1
    bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=2, radius=0.85 + (i % 3) * 0.3, location=(bx, by, 0.0))
    b_obj = bpy.context.active_object
    b_obj.data.materials.append(mat_boulder)
    boulders.append(b_obj)

# Join all pond components into clean single asset
bpy.ops.object.select_all(action='SELECT')
active_pond = basin
bpy.context.view_layer.objects.active = active_pond
bpy.ops.object.join()
active_pond.name = "Pond_Basin_Natural"

export_glb(os.path.join(STATIC_ENV, "water", "pond_basin.glb"))
export_glb(os.path.join(ASSETS_ENV, "water", "pond_basin.glb"))

print("=== ALL ASSETS PROCESSED SUCCESSFULLY IN BLENDER! ===")
