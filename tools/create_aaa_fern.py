import bpy
import math
import random
import os

PROJECT_DIR = r"D:\Simulation For DT\prw-wild-digital-twin"
STATIC_VEG = os.path.join(PROJECT_DIR, "src", "prw_wild", "web", "static", "assets", "environment", "vegetation")
ASSETS_VEG = os.path.join(PROJECT_DIR, "assets", "environment", "vegetation")

bpy.ops.wm.read_factory_settings(use_empty=True)

# Fern Frond Material
mat = bpy.data.materials.new(name="M_ForestFern_PBR")
mat.use_nodes = True
bsdf = mat.node_tree.nodes.get("Principled BSDF")
if bsdf:
    # Deep lush emerald forest green
    bsdf.inputs["Base Color"].default_value = (0.12, 0.32, 0.08, 1.0)
    bsdf.inputs["Roughness"].default_value = 0.50
    if "Subsurface Weight" in bsdf.inputs:
        bsdf.inputs["Subsurface Weight"].default_value = 0.25
    elif "Subsurface" in bsdf.inputs:
        bsdf.inputs["Subsurface"].default_value = 0.25

# Generate 3D Fern with 10 radiating arched fronds
mesh = bpy.data.meshes.new("Forest_Fern_Frond_Cluster")
verts = []
faces = []

random.seed(99)
num_fronds = 10

for f in range(num_fronds):
    angle = (f / num_fronds) * math.pi * 2 + random.uniform(-0.1, 0.1)
    length = random.uniform(1.2, 1.8)
    lean = random.uniform(0.7, 1.1)
    
    # Frond stem rachis with 8 segments
    segs = 8
    base_idx = len(verts)
    
    for s in range(segs + 1):
        t = s / segs
        # Arching curve: rises then droops gracefully towards tips
        z = length * math.sin(t * math.pi * 0.7) * 0.65
        r = t * length * lean
        x = math.cos(angle) * r
        y = math.sin(angle) * r
        
        # Leaflet width along frond (widest in middle, tapering at both ends)
        w = math.sin(t * math.pi) * 0.38 + 0.04
        nx = -math.sin(angle) * w
        ny = math.cos(angle) * w
        
        verts.append((x - nx, y - ny, z))
        verts.append((x + nx, y + ny, z))
        
        if s > 0:
            p0 = base_idx + (s - 1) * 2
            p1 = p0 + 1
            p2 = base_idx + s * 2
            p3 = p2 + 1
            faces.append((p0, p1, p3, p2))

mesh.from_pydata(verts, [], faces)
mesh.update()

obj = bpy.data.objects.new("Forest_Fern_Frond_Cluster", mesh)
bpy.context.collection.objects.link(obj)
obj.data.materials.append(mat)

# Export clean GLB
os.makedirs(STATIC_VEG, exist_ok=True)
os.makedirs(ASSETS_VEG, exist_ok=True)

out_static = os.path.join(STATIC_VEG, "forest_ferns.glb")
out_assets = os.path.join(ASSETS_VEG, "forest_ferns.glb")

bpy.ops.export_scene.gltf(
    filepath=out_static,
    export_format='GLB',
    use_selection=False,
    export_apply=True,
    export_materials='EXPORT',
    export_yup=True
)
bpy.ops.export_scene.gltf(
    filepath=out_assets,
    export_format='GLB',
    use_selection=False,
    export_apply=True,
    export_materials='EXPORT',
    export_yup=True
)

print(f"Successfully generated AAA 3D Fern Cluster GLB! ({len(verts)} verts, {len(faces)} faces)")

