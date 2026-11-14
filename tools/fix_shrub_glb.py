import bpy
import os

PROJECT_DIR = r"D:\Simulation For DT\prw-wild-digital-twin"
DOWNLOADS_DIR = os.path.join(PROJECT_DIR, "assets", "downloads", "polyhaven")
STATIC_VEG = os.path.join(PROJECT_DIR, "src", "prw_wild", "web", "static", "assets", "environment", "vegetation")
ASSETS_VEG = os.path.join(PROJECT_DIR, "assets", "environment", "vegetation")

bpy.ops.wm.read_factory_settings(use_empty=True)

bush_fbx = os.path.join(DOWNLOADS_DIR, "wild_rooibos_bush_1k.fbx")
diff_tex = os.path.join(DOWNLOADS_DIR, "wild_rooibos_bush_Diffuse_1k.jpg")
nor_tex = os.path.join(DOWNLOADS_DIR, "wild_rooibos_bush_nor_gl_1k.jpg")
rough_tex = os.path.join(DOWNLOADS_DIR, "wild_rooibos_bush_Rough_1k.jpg")

bpy.ops.import_scene.fbx(filepath=bush_fbx)

# Join all parts
bpy.ops.object.select_all(action='SELECT')
active_bush = bpy.data.objects[0]
bpy.context.view_layer.objects.active = active_bush
bpy.ops.object.join()
active_bush.name = "Forest_Shrub_Rooibos"

# Setup one unified clean PBR material for the shrub
mat = bpy.data.materials.new(name="M_Rooibos_Bush_PBR")
mat.use_nodes = True
nodes = mat.node_tree.nodes
links = mat.node_tree.links
bsdf = nodes.get("Principled BSDF")

# Clear existing materials on the object and assign the single clean one
active_bush.data.materials.clear()
active_bush.data.materials.append(mat)

if os.path.exists(diff_tex):
    tex_node = nodes.new("ShaderNodeTexImage")
    tex_node.image = bpy.data.images.load(diff_tex)
    links.new(tex_node.outputs["Color"], bsdf.inputs["Base Color"])
    # If image has alpha or if mask
    bsdf.inputs["Base Color"].default_value = (0.22, 0.45, 0.12, 1.0)
    mat.blend_method = 'OPAQUE'

if os.path.exists(rough_tex):
    r_node = nodes.new("ShaderNodeTexImage")
    r_node.image = bpy.data.images.load(rough_tex)
    links.new(r_node.outputs["Color"], bsdf.inputs["Roughness"])
else:
    bsdf.inputs["Roughness"].default_value = 0.75

if os.path.exists(nor_tex):
    n_node = nodes.new("ShaderNodeTexImage")
    n_node.image = bpy.data.images.load(nor_tex)
    n_node.image.colorspace_settings.name = 'Non-Color'
    norm_map = nodes.new("ShaderNodeNormalMap")
    links.new(n_node.outputs["Color"], norm_map.inputs["Color"])
    links.new(norm_map.outputs["Normal"], bsdf.inputs["Normal"])

active_bush.scale = (1.4, 1.4, 1.4)
bpy.ops.object.transform_apply(scale=True)

# Export clean glbs
out1 = os.path.join(STATIC_VEG, "forest_shrub.glb")
out2 = os.path.join(STATIC_VEG, "shrub_01.glb")
out3 = os.path.join(ASSETS_VEG, "forest_shrub.glb")

bpy.ops.export_scene.gltf(filepath=out1, export_format='GLB', use_selection=False, export_apply=True, export_materials='EXPORT', export_yup=True)
bpy.ops.export_scene.gltf(filepath=out2, export_format='GLB', use_selection=False, export_apply=True, export_materials='EXPORT', export_yup=True)
bpy.ops.export_scene.gltf(filepath=out3, export_format='GLB', use_selection=False, export_apply=True, export_materials='EXPORT', export_yup=True)

print("Successfully exported clean, textured Forest Shrub GLB!")

