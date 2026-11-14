import bpy
import os

PROJECT_DIR = r"D:\Simulation For DT\prw-wild-digital-twin"
SRC_GLB = os.path.join(PROJECT_DIR, "assets", "animals", "elephant", "asian_elephant_production.glb")

ALBEDO_PNG = os.path.join(PROJECT_DIR, "src", "prw_wild", "web", "static", "assets", "animals", "elephant_albedo_realistic.png")
NORMAL_PNG = os.path.join(PROJECT_DIR, "src", "prw_wild", "web", "static", "assets", "animals", "elephant_normal_realistic.png")

TARGETS = [
    os.path.join(PROJECT_DIR, "src", "prw_wild", "web", "static", "assets", "animals", "asian_elephant_production.glb"),
    os.path.join(PROJECT_DIR, "src", "prw_wild", "web", "static", "assets", "animals", "asian_elephant_bull.glb"),
    os.path.join(PROJECT_DIR, "src", "prw_wild", "web", "static", "assets", "animals", "asian_elephant.glb"),
    os.path.join(PROJECT_DIR, "assets", "animals", "asian_elephant_production.glb"),
    os.path.join(PROJECT_DIR, "assets", "animals", "asian_elephant_bull.glb"),
    os.path.join(PROJECT_DIR, "assets", "animals", "asian_elephant.glb"),
]

bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.gltf(filepath=SRC_GLB)

# Remove any stray unskinned icosphere
for o in list(bpy.data.objects):
    if o.name == 'Icosphere' and o.type == 'MESH':
        print(f"Removing unskinned stray object: {o.name}")
        bpy.data.objects.remove(o, do_unlink=True)

# Build PBR Elephant Material with both Diffuse and Normal Map
mat = bpy.data.materials.get("Elephant_Mat")
if not mat:
    mat = bpy.data.materials.new(name="Elephant_Mat")

mat.use_nodes = True
nt = mat.node_tree
nt.nodes.clear()

out_node = nt.nodes.new(type="ShaderNodeOutputMaterial")
bsdf = nt.nodes.new(type="ShaderNodeBsdfPrincipled")
nt.links.new(bsdf.outputs["BSDF"], out_node.inputs["Surface"])

# Diffuse Base Color
if os.path.exists(ALBEDO_PNG):
    img_diff = bpy.data.images.load(ALBEDO_PNG)
    tex_diff = nt.nodes.new(type="ShaderNodeTexImage")
    tex_diff.image = img_diff
    nt.links.new(tex_diff.outputs["Color"], bsdf.inputs["Base Color"])

# Normal Map
if os.path.exists(NORMAL_PNG):
    img_nor = bpy.data.images.load(NORMAL_PNG)
    img_nor.colorspace_settings.name = 'Non-Color'
    tex_nor = nt.nodes.new(type="ShaderNodeTexImage")
    tex_nor.image = img_nor
    n_map = nt.nodes.new(type="ShaderNodeNormalMap")
    n_map.inputs["Strength"].default_value = 1.2
    nt.links.new(tex_nor.outputs["Color"], n_map.inputs["Color"])
    nt.links.new(n_map.outputs["Normal"], bsdf.inputs["Normal"])

bsdf.inputs["Roughness"].default_value = 0.72
bsdf.inputs["Metallic"].default_value = 0.0

# Ensure mesh uses this material
for o in bpy.data.objects:
    if o.type == 'MESH':
        o.data.materials.clear()
        o.data.materials.append(mat)
        print(f"Assigned Elephant_Mat with PBR normal map to {o.name}")

# Check animations
print(f"Actions present: {[a.name for a in bpy.data.actions]}")
armatures = [o for o in bpy.data.objects if o.type == 'ARMATURE']
print(f"Armatures present: {[a.name for a in armatures]}")

for target in TARGETS:
    os.makedirs(os.path.dirname(target), exist_ok=True)
    bpy.ops.export_scene.gltf(
        filepath=target,
        export_format='GLB',
        use_selection=False,
        export_apply=False,
        export_materials='EXPORT',
        export_yup=True,
        export_animations=True
    )
    print(f"Exported rigged & animated realistic Elephant GLB: {target} ({os.path.getsize(target)/1024:.1f} KB)")
