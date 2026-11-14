import bpy
import os

POLY_DIR = r"D:\Simulation For DT\prw-wild-digital-twin\assets\downloads\polyhaven"
FBX_PATH = os.path.join(POLY_DIR, "quiver_tree_01_1k.fbx")

TRUNK_DIFF = os.path.join(POLY_DIR, "quiver_tree_01_trunk_diff_1k.jpg")
TRUNK_NOR = os.path.join(POLY_DIR, "quiver_tree_01_trunk_nor_gl_1k.jpg")
TRUNK_ROUGH = os.path.join(POLY_DIR, "quiver_tree_01_trunk_rough_1k.jpg")

LEAF_DIFF = os.path.join(POLY_DIR, "quiver_tree_01_leaf_diff_1k.jpg")
LEAF_NOR = os.path.join(POLY_DIR, "quiver_tree_01_leaf_nor_gl_1k.jpg")
LEAF_ROUGH = os.path.join(POLY_DIR, "quiver_tree_01_leaf_rough_1k.jpg")

OUT_PATHS = [
    r"D:\Simulation For DT\prw-wild-digital-twin\src\prw_wild\web\static\assets\environment\trees\quiver_tree.glb",
    r"D:\Simulation For DT\prw-wild-digital-twin\assets\environment\trees\quiver_tree.glb",
]

bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.fbx(filepath=FBX_PATH)

# Check imported objects
mesh_objs = [o for o in bpy.data.objects if o.type == 'MESH']
print("Imported mesh objects:", [o.name for o in mesh_objs])

# Create trunk material
mat_trunk = bpy.data.materials.new(name="M_Quiver_Trunk")
mat_trunk.use_nodes = True
nt = mat_trunk.node_tree
nt.nodes.clear()
out_node = nt.nodes.new(type="ShaderNodeOutputMaterial")
bsdf_trunk = nt.nodes.new(type="ShaderNodeBsdfPrincipled")
nt.links.new(bsdf_trunk.outputs["BSDF"], out_node.inputs["Surface"])

if os.path.exists(TRUNK_DIFF):
    t_diff = nt.nodes.new(type="ShaderNodeTexImage")
    t_diff.image = bpy.data.images.load(TRUNK_DIFF)
    nt.links.new(t_diff.outputs["Color"], bsdf_trunk.inputs["Base Color"])

if os.path.exists(TRUNK_ROUGH):
    t_rough = nt.nodes.new(type="ShaderNodeTexImage")
    img = bpy.data.images.load(TRUNK_ROUGH)
    img.colorspace_settings.name = 'Non-Color'
    t_rough.image = img
    nt.links.new(t_rough.outputs["Color"], bsdf_trunk.inputs["Roughness"])
else:
    bsdf_trunk.inputs["Roughness"].default_value = 0.85

if os.path.exists(TRUNK_NOR):
    t_nor = nt.nodes.new(type="ShaderNodeTexImage")
    img_n = bpy.data.images.load(TRUNK_NOR)
    img_n.colorspace_settings.name = 'Non-Color'
    t_nor.image = img_n
    n_map = nt.nodes.new(type="ShaderNodeNormalMap")
    nt.links.new(t_nor.outputs["Color"], n_map.inputs["Color"])
    nt.links.new(n_map.outputs["Normal"], bsdf_trunk.inputs["Normal"])

# Create leaf material
mat_leaf = bpy.data.materials.new(name="M_Quiver_Leaf")
mat_leaf.use_nodes = True
nl = mat_leaf.node_tree
nl.nodes.clear()
out_node_l = nl.nodes.new(type="ShaderNodeOutputMaterial")
bsdf_leaf = nl.nodes.new(type="ShaderNodeBsdfPrincipled")
nl.links.new(bsdf_leaf.outputs["BSDF"], out_node_l.inputs["Surface"])

if os.path.exists(LEAF_DIFF):
    l_diff = nl.nodes.new(type="ShaderNodeTexImage")
    l_diff.image = bpy.data.images.load(LEAF_DIFF)
    nl.links.new(l_diff.outputs["Color"], bsdf_leaf.inputs["Base Color"])

if os.path.exists(LEAF_ROUGH):
    l_rough = nl.nodes.new(type="ShaderNodeTexImage")
    img_lr = bpy.data.images.load(LEAF_ROUGH)
    img_lr.colorspace_settings.name = 'Non-Color'
    l_rough.image = img_lr
    nl.links.new(l_rough.outputs["Color"], bsdf_leaf.inputs["Roughness"])
else:
    bsdf_leaf.inputs["Roughness"].default_value = 0.65

if os.path.exists(LEAF_NOR):
    l_nor = nl.nodes.new(type="ShaderNodeTexImage")
    img_ln = bpy.data.images.load(LEAF_NOR)
    img_ln.colorspace_settings.name = 'Non-Color'
    l_nor.image = img_ln
    nl_map = nl.nodes.new(type="ShaderNodeNormalMap")
    nl.links.new(l_nor.outputs["Color"], nl_map.inputs["Color"])
    nl.links.new(nl_map.outputs["Normal"], bsdf_leaf.inputs["Normal"])

# Inspect material slots on quiver_tree_01_LOD0
tree_obj = mesh_objs[0]
print(f"Tree object {tree_obj.name} has {len(tree_obj.material_slots)} slots: {[s.name for s in tree_obj.material_slots]}")

# Typically slot 0 is trunk/bark and slot 1 is leaves
for i, slot in enumerate(tree_obj.material_slots):
    sname = slot.name.lower() if slot.name else ""
    if 'leaf' in sname or 'leaves' in sname or i == 1:
        slot.material = mat_leaf
    else:
        slot.material = mat_trunk

# If no slots, assign trunk
if len(tree_obj.material_slots) == 0:
    tree_obj.data.materials.append(mat_trunk)

# Apply transform
bpy.ops.object.select_all(action='SELECT')
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
    print(f"Exported quiver tree GLB: {out_p} ({os.path.getsize(out_p)/1024:.1f} KB)")
