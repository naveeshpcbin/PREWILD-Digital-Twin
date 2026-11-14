import bpy
import os

FBX_PATH = r"D:\Simulation For DT\prw-wild-digital-twin\assets\downloads\polyhaven\boulder_01_1k.fbx"
DIFF_PATH = r"D:\Simulation For DT\prw-wild-digital-twin\assets\downloads\polyhaven\boulder_01_diff_1k.jpg"
NOR_PATH = r"D:\Simulation For DT\prw-wild-digital-twin\assets\downloads\polyhaven\boulder_01_nor_dx_1k.jpg"
ROUGH_PATH = r"D:\Simulation For DT\prw-wild-digital-twin\assets\downloads\polyhaven\boulder_01_rough_1k.jpg"

OUT_PATHS = [
    r"D:\Simulation For DT\prw-wild-digital-twin\src\prw_wild\web\static\assets\environment\rocks\boulder_01.glb",
    r"D:\Simulation For DT\prw-wild-digital-twin\assets\environment\rocks\boulder_01.glb",
]

bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.fbx(filepath=FBX_PATH)

# Keep ONLY LOD0
lod0_obj = None
for o in list(bpy.data.objects):
    if o.name == 'boulder_01_LOD0':
        lod0_obj = o
    elif o.type == 'MESH':
        bpy.data.objects.remove(o, do_unlink=True)

if not lod0_obj:
    meshes = [o for o in bpy.data.objects if o.type == 'MESH']
    lod0_obj = meshes[0]

print(f"Kept single primary boulder mesh: {lod0_obj.name}")

# Create realistic PBR material
mat = bpy.data.materials.new(name="M_Boulder_Granite_PBR")
mat.use_nodes = True
nodes = mat.node_tree.nodes
links = mat.node_tree.links
nodes.clear()

node_output = nodes.new(type="ShaderNodeOutputMaterial")
node_bsdf = nodes.new(type="ShaderNodeBsdfPrincipled")
links.new(node_bsdf.outputs["BSDF"], node_output.inputs["Surface"])

# 1. Base color (diffuse)
if os.path.exists(DIFF_PATH):
    img_diff = bpy.data.images.load(DIFF_PATH)
    tex_diff = nodes.new(type="ShaderNodeTexImage")
    tex_diff.image = img_diff
    links.new(tex_diff.outputs["Color"], node_bsdf.inputs["Base Color"])

# 2. Roughness
if os.path.exists(ROUGH_PATH):
    img_rough = bpy.data.images.load(ROUGH_PATH)
    img_rough.colorspace_settings.name = 'Non-Color'
    tex_rough = nodes.new(type="ShaderNodeTexImage")
    tex_rough.image = img_rough
    links.new(tex_rough.outputs["Color"], node_bsdf.inputs["Roughness"])
else:
    node_bsdf.inputs["Roughness"].default_value = 0.85

# 3. Normal Map
if os.path.exists(NOR_PATH):
    img_nor = bpy.data.images.load(NOR_PATH)
    img_nor.colorspace_settings.name = 'Non-Color'
    tex_nor = nodes.new(type="ShaderNodeTexImage")
    tex_nor.image = img_nor
    node_normap = nodes.new(type="ShaderNodeNormalMap")
    node_normap.inputs["Strength"].default_value = 1.0
    links.new(tex_nor.outputs["Color"], node_normap.inputs["Color"])
    links.new(node_normap.outputs["Normal"], node_bsdf.inputs["Normal"])

node_bsdf.inputs["Metallic"].default_value = 0.0

lod0_obj.data.materials.clear()
lod0_obj.data.materials.append(mat)
lod0_obj.scale = (0.5, 0.5, 0.5)

bpy.context.view_layer.objects.active = lod0_obj
lod0_obj.select_set(True)
bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)

for out_p in OUT_PATHS:
    os.makedirs(os.path.dirname(out_p), exist_ok=True)
    bpy.ops.export_scene.gltf(
        filepath=out_p,
        export_format='GLB',
        use_selection=False,
        export_apply=True,
        export_materials='EXPORT',
        export_yup=True
    )
    print(f"Exported clean single-mesh boulder GLB: {out_p} ({os.path.getsize(out_p)/1024:.1f} KB)")
