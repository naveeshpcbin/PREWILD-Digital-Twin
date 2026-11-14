import bpy
import math
import random
import os

PROJECT_DIR = r"D:\Simulation For DT\prw-wild-digital-twin"
STATIC_GRASS = os.path.join(PROJECT_DIR, "src", "prw_wild", "web", "static", "assets", "environment", "grass")
ASSETS_GRASS = os.path.join(PROJECT_DIR, "assets", "environment", "grass")

bpy.ops.wm.read_factory_settings(use_empty=True)

# Create Grass Material
mat = bpy.data.materials.new(name="M_TallGrass_PBR")
mat.use_nodes = True
bsdf = mat.node_tree.nodes.get("Principled BSDF")
if bsdf:
    # Rich natural savanna/forest green
    bsdf.inputs["Base Color"].default_value = (0.16, 0.38, 0.08, 1.0)
    bsdf.inputs["Roughness"].default_value = 0.55
    if "Subsurface Weight" in bsdf.inputs:
        bsdf.inputs["Subsurface Weight"].default_value = 0.2
    elif "Subsurface" in bsdf.inputs:
        bsdf.inputs["Subsurface"].default_value = 0.2

# Generate realistic 3D grass blades clump
blades_mesh = bpy.data.meshes.new("Tall_Grass_Tuft_Natural")
verts = []
faces = []

random.seed(42)
num_blades = 28
radius_spread = 0.45

for b in range(num_blades):
    # Base position
    angle = (b / num_blades) * math.pi * 2 + random.uniform(-0.15, 0.15)
    dist = random.uniform(0.05, radius_spread)
    bx = math.cos(angle) * dist
    by = math.sin(angle) * dist
    
    # Height of blade: 0.8m to 1.5m
    height = random.uniform(0.85, 1.45)
    width = random.uniform(0.04, 0.07)
    
    # Lean outward
    lean_dist = dist * 1.8 + random.uniform(0.2, 0.45)
    lx = math.cos(angle) * lean_dist
    ly = math.sin(angle) * lean_dist
    
    # 4 segments per blade for smooth curvature
    base_idx = len(verts)
    segs = 4
    for s in range(segs + 1):
        t = s / segs
        # Quadratic curve for natural droop
        cz = height * (1.0 - (1.0 - t)**2)
        cx = bx + (lx - bx) * (t**1.8)
        cy = by + (ly - by) * (t**1.8)
        
        # Blade width tapers to tip
        w = width * (1.0 - t * 0.95)
        # Normal perpendicular to blade direction
        nx = -math.sin(angle) * w * 0.5
        ny = math.cos(angle) * w * 0.5
        
        verts.append((cx - nx, cy - ny, cz))
        verts.append((cx + nx, cy + ny, cz))
        
        if s > 0:
            p0 = base_idx + (s - 1) * 2
            p1 = p0 + 1
            p2 = base_idx + s * 2
            p3 = p2 + 1
            faces.append((p0, p1, p3, p2))

blades_mesh.from_pydata(verts, [], faces)
blades_mesh.update()

# Recalculate normals
obj = bpy.data.objects.new("Tall_Grass_Tuft_Natural", blades_mesh)
bpy.context.collection.objects.link(obj)
obj.data.materials.append(mat)

# Export clean glb
os.makedirs(STATIC_GRASS, exist_ok=True)
os.makedirs(ASSETS_GRASS, exist_ok=True)

out_static = os.path.join(STATIC_GRASS, "tall_grass_clump.glb")
out_assets = os.path.join(ASSETS_GRASS, "tall_grass_clump.glb")

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

print(f"Successfully generated AAA 3D Grass Clump GLB! ({len(verts)} verts, {len(faces)} faces)")

