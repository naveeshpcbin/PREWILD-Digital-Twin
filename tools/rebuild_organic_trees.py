import bpy
import math
import os

PROJECT_DIR = r"D:\Simulation For DT\prw-wild-digital-twin"
STATIC_TREES = os.path.join(PROJECT_DIR, "src", "prw_wild", "web", "static", "assets", "environment", "trees")
ASSETS_TREES = os.path.join(PROJECT_DIR, "assets", "environment", "trees")
STATIC_FRUIT = os.path.join(PROJECT_DIR, "src", "prw_wild", "web", "static", "assets", "environment", "fruit_trees")
ASSETS_FRUIT = os.path.join(PROJECT_DIR, "assets", "environment", "fruit_trees")

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
    print(f"[Blender] Exported Tree GLB: {filepath} ({os.path.getsize(filepath)/1024:.1f} KB)")

def make_pbr_material(name, base_color, roughness=0.85):
    mat = bpy.data.materials.new(name=name)
    mat.use_nodes = True
    bsdf = mat.node_tree.nodes.get("Principled BSDF")
    if bsdf:
        bsdf.inputs["Base Color"].default_value = base_color
        bsdf.inputs["Roughness"].default_value = roughness
        if "Subsurface Weight" in bsdf.inputs:
            bsdf.inputs["Subsurface Weight"].default_value = 0.20
        elif "Subsurface" in bsdf.inputs:
            bsdf.inputs["Subsurface"].default_value = 0.20
    return mat

def create_curved_branch(points, radii, mat, name="Branch"):
    curve_data = bpy.data.curves.new(name=f"{name}_Curve", type='CURVE')
    curve_data.dimensions = '3D'
    curve_data.fill_mode = 'FULL'
    curve_data.bevel_depth = 1.0
    curve_data.bevel_resolution = 4
    
    spline = curve_data.splines.new('BEZIER')
    spline.bezier_points.add(len(points) - 1)
    
    for i, (pt, rad) in enumerate(zip(points, radii)):
        bp = spline.bezier_points[i]
        bp.co = pt
        bp.radius = rad
        bp.handle_left_type = 'AUTO'
        bp.handle_right_type = 'AUTO'
        
    curve_obj = bpy.data.objects.new(name, curve_data)
    bpy.context.collection.objects.link(curve_obj)
    
    bpy.context.view_layer.objects.active = curve_obj
    curve_obj.select_set(True)
    bpy.ops.object.convert(target='MESH')
    curve_obj.data.materials.append(mat)
    return curve_obj

def add_organic_foliage_clump(location, scale, mat, name="Foliage"):
    # Create icosphere
    bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=3, radius=1.0, location=location)
    obj = bpy.context.active_object
    obj.name = name
    obj.scale = scale
    
    # Add displace modifier for organic leaf clusters
    tex = bpy.data.textures.new(name=f"{name}_Noise", type='CLOUDS')
    tex.noise_scale = 0.45
    tex.noise_depth = 2
    
    disp = obj.modifiers.new(name="Displace", type='DISPLACE')
    disp.texture = tex
    disp.strength = 0.22
    
    # Apply modifier
    bpy.ops.object.modifier_apply(modifier="Displace")
    obj.data.materials.append(mat)
    return obj

# =========================================================================
# 1. ACACIA CANOPY TREE (Umbrella Crown with Displaced Foliage Clumps)
# =========================================================================
print("=== Rebuilding Acacia Canopy Tree ===")
clear_scene()

mat_acacia_bark = make_pbr_material("M_Bark_Acacia_AAA", (0.34, 0.26, 0.18, 1.0), roughness=0.92)
mat_acacia_leaves = make_pbr_material("M_Foliage_Acacia_AAA", (0.19, 0.38, 0.12, 1.0), roughness=0.65)

acacia_parts = []
a_pts = [(0.0, 0.0, 0.0), (0.4, 0.2, 1.8), (0.9, 0.5, 3.4), (1.5, 0.9, 5.0)]
a_radii = [0.65, 0.52, 0.42, 0.35]
acacia_parts.append(create_curved_branch(a_pts, a_radii, mat_acacia_bark, "Acacia_Trunk"))

acacia_branches = [
    ([(1.5, 0.9, 5.0), (2.8, 1.8, 6.2), (4.2, 2.6, 7.0)], [0.30, 0.22, 0.14]),
    ([(1.5, 0.9, 5.0), (0.2, 2.0, 6.1), (-1.2, 3.0, 6.9)], [0.28, 0.20, 0.14]),
    ([(1.5, 0.9, 5.0), (2.6, -0.4, 6.0), (3.8, -1.6, 6.8)], [0.28, 0.20, 0.14]),
    ([(1.5, 0.9, 5.0), (-0.4, -0.2, 5.9), (-2.2, -1.2, 6.7)], [0.26, 0.18, 0.13])
]
for i, (pts, rads) in enumerate(acacia_branches):
    acacia_parts.append(create_curved_branch(pts, rads, mat_acacia_bark, f"Acacia_Bough_{i}"))

acacia_foliage_specs = [
    ((1.8, 1.1, 7.6), (4.2, 4.0, 1.4)),
    ((4.0, 2.4, 7.4), (3.6, 3.4, 1.3)),
    ((-1.0, 2.8, 7.3), (3.5, 3.3, 1.3)),
    ((3.6, -1.4, 7.2), (3.4, 3.2, 1.2)),
    ((-2.0, -1.0, 7.1), (3.3, 3.1, 1.2)),
    ((2.2, 0.4, 8.2), (3.0, 2.8, 1.1))
]
for i, (pos, scale) in enumerate(acacia_foliage_specs):
    add_organic_foliage_clump(pos, scale, mat_acacia_leaves, f"Acacia_Foliage_{i}")

bpy.ops.object.select_all(action='SELECT')
active_acacia = acacia_parts[0]
bpy.context.view_layer.objects.active = active_acacia
bpy.ops.object.join()
active_acacia.name = "Tree_Acacia_Canopy"

export_glb(os.path.join(STATIC_TREES, "acacia_canopy.glb"))
export_glb(os.path.join(ASSETS_TREES, "acacia_canopy.glb"))

# =========================================================================
# 2. SAL MATURE TREE (Grand Timber Tree with Columnar Crown)
# =========================================================================
print("=== Rebuilding Sal Mature Tree ===")
clear_scene()

mat_sal_bark = make_pbr_material("M_Bark_Sal_AAA", (0.26, 0.18, 0.13, 1.0), roughness=0.92)
mat_sal_leaves = make_pbr_material("M_Foliage_Sal_AAA", (0.14, 0.32, 0.09, 1.0), roughness=0.68)

sal_parts = []
trunk_pts = [(0.0, 0.0, 0.0), (0.05, -0.05, 2.5), (-0.08, 0.06, 5.0), (0.04, 0.12, 7.5), (0.0, 0.08, 9.2)]
trunk_radii = [0.95, 0.72, 0.58, 0.46, 0.35]
sal_parts.append(create_curved_branch(trunk_pts, trunk_radii, mat_sal_bark, "Sal_Trunk"))

root_angles = [0.4, 1.9, 3.5, 5.1]
for i, ang in enumerate(root_angles):
    rx = math.cos(ang) * 1.6
    ry = math.sin(ang) * 1.6
    root_pts = [(0.0, 0.0, 1.2), (rx * 0.5, ry * 0.5, 0.4), (rx, ry, 0.0)]
    sal_parts.append(create_curved_branch(root_pts, [0.45, 0.32, 0.18], mat_sal_bark, f"Sal_Root_{i}"))

branch_specs = [
    ([(0.0, 0.06, 6.2), (1.4, 0.8, 7.8), (2.8, 1.6, 9.4)], [0.38, 0.26, 0.16]),
    ([(0.0, -0.05, 6.8), (-1.6, -0.9, 8.2), (-3.0, -1.8, 9.6)], [0.36, 0.24, 0.15]),
    ([(0.04, 0.10, 7.4), (-1.2, 1.5, 8.8), (-2.2, 2.8, 10.2)], [0.34, 0.22, 0.14]),
    ([(-0.06, 0.08, 7.8), (1.5, -1.2, 9.1), (2.9, -2.4, 10.5)], [0.32, 0.20, 0.14]),
    ([(0.0, 0.08, 9.0), (0.4, 0.3, 10.4), (0.8, 0.6, 11.8)], [0.30, 0.18, 0.12])
]
for i, (pts, rads) in enumerate(branch_specs):
    sal_parts.append(create_curved_branch(pts, rads, mat_sal_bark, f"Sal_Bough_{i}"))

sal_foliage_specs = [
    ((0.0, 0.4, 11.5), (3.6, 3.6, 2.6)),
    ((2.6, 1.5, 9.6), (3.2, 3.0, 2.4)),
    ((-2.8, -1.6, 9.8), (3.1, 2.9, 2.3)),
    ((-2.0, 2.6, 10.4), (2.9, 2.8, 2.2)),
    ((2.7, -2.2, 10.6), (3.0, 2.9, 2.3)),
    ((0.7, 0.5, 12.6), (2.6, 2.5, 2.1)),
    ((1.2, 0.8, 8.6), (2.4, 2.2, 2.0)),
    ((-1.1, -0.7, 8.8), (2.3, 2.3, 1.9))
]
for i, (pos, scale) in enumerate(sal_foliage_specs):
    add_organic_foliage_clump(pos, scale, mat_sal_leaves, f"Sal_Foliage_{i}")

bpy.ops.object.select_all(action='SELECT')
active_sal = sal_parts[0]
bpy.context.view_layer.objects.active = active_sal
bpy.ops.object.join()
active_sal.name = "Tree_Sal_Mature"

export_glb(os.path.join(STATIC_TREES, "sal_mature.glb"))
export_glb(os.path.join(ASSETS_TREES, "sal_mature.glb"))

# =========================================================================
# 3. BANYAN FIG TREE (Sprawling Canopy with Aerial Prop Roots)
# =========================================================================
print("=== Rebuilding Banyan Fig Tree ===")
clear_scene()

mat_banyan_bark = make_pbr_material("M_Bark_Banyan_AAA", (0.30, 0.23, 0.18, 1.0), roughness=0.90)
mat_banyan_leaves = make_pbr_material("M_Foliage_Banyan_AAA", (0.12, 0.30, 0.08, 1.0), roughness=0.66)

banyan_parts = []
b_pts = [(0.0, 0.0, 0.0), (0.1, 0.05, 1.8), (-0.1, 0.1, 3.6), (0.0, 0.15, 5.5)]
b_radii = [1.5, 1.15, 0.95, 0.8]
banyan_parts.append(create_curved_branch(b_pts, b_radii, mat_banyan_bark, "Banyan_Trunk"))

lateral_specs = [
    ([(0.0, 0.1, 4.2), (2.8, 0.6, 5.2), (5.8, 1.2, 5.8)], [0.65, 0.45, 0.3]),
    ([(0.0, 0.1, 4.4), (-2.6, 1.2, 5.3), (-5.6, 2.4, 5.9)], [0.65, 0.45, 0.3]),
    ([(0.0, 0.1, 4.0), (1.4, -2.6, 5.0), (2.8, -5.5, 5.6)], [0.62, 0.42, 0.28]),
    ([(0.0, 0.1, 4.3), (-1.6, -2.4, 5.1), (-3.2, -5.2, 5.7)], [0.62, 0.42, 0.28]),
    ([(0.0, 0.15, 4.6), (3.6, -1.8, 5.4), (7.0, -3.2, 6.0)], [0.60, 0.40, 0.26]),
    ([(0.0, 0.15, 4.5), (-3.4, -1.6, 5.3), (-6.8, -3.0, 5.8)], [0.60, 0.40, 0.26])
]
for i, (pts, rads) in enumerate(lateral_specs):
    banyan_parts.append(create_curved_branch(pts, rads, mat_banyan_bark, f"Banyan_Bough_{i}"))

prop_positions = [(4.5, 0.9, 5.4), (-4.4, 1.8, 5.5), (2.2, -4.2, 5.2), (-2.5, -4.0, 5.3), (5.5, -2.5, 5.6), (-5.3, -2.3, 5.4)]
for i, (px, py, pz) in enumerate(prop_positions):
    pts = [(px, py, pz), (px + 0.1, py - 0.05, pz * 0.5), (px + 0.15, py, 0.0)]
    rads = [0.22, 0.20, 0.25]
    banyan_parts.append(create_curved_branch(pts, rads, mat_banyan_bark, f"Banyan_PropRoot_{i}"))

banyan_foliage_specs = [
    ((0.0, 0.2, 7.2), (5.2, 5.0, 2.6)),
    ((4.8, 1.0, 6.6), (4.5, 4.2, 2.4)),
    ((-4.6, 1.8, 6.7), (4.4, 4.3, 2.4)),
    ((2.4, -4.5, 6.4), (4.2, 4.0, 2.3)),
    ((-2.6, -4.4, 6.5), (4.3, 4.1, 2.3)),
    ((5.8, -2.6, 6.8), (4.6, 4.4, 2.4)),
    ((-5.6, -2.4, 6.6), (4.5, 4.2, 2.4)),
    ((0.0, 0.0, 8.5), (4.0, 3.8, 2.2))
]
for i, (pos, scale) in enumerate(banyan_foliage_specs):
    add_organic_foliage_clump(pos, scale, mat_banyan_leaves, f"Banyan_Foliage_{i}")

bpy.ops.object.select_all(action='SELECT')
active_banyan = banyan_parts[0]
bpy.context.view_layer.objects.active = active_banyan
bpy.ops.object.join()
active_banyan.name = "Tree_Banyan_Sprawling"

export_glb(os.path.join(STATIC_TREES, "banyan_fig.glb"))
export_glb(os.path.join(ASSETS_TREES, "banyan_fig.glb"))

# =========================================================================
# 4. WILD MANGO TREE (Dense Rounded Dome with Golden Mango Fruit Accents)
# =========================================================================
print("=== Rebuilding Wild Mango Tree ===")
clear_scene()

mat_mango_bark = make_pbr_material("M_Bark_Mango_AAA", (0.28, 0.20, 0.15, 1.0), roughness=0.88)
mat_mango_leaves = make_pbr_material("M_Foliage_Mango_AAA", (0.11, 0.30, 0.07, 1.0), roughness=0.64)
mat_mango_fruit = make_pbr_material("M_Fruit_Mango_AAA", (0.95, 0.65, 0.08, 1.0), roughness=0.35)

mango_parts = []
m_pts = [(0.0, 0.0, 0.0), (0.05, -0.05, 1.5), (-0.05, 0.08, 3.0), (0.0, 0.05, 4.6)]
m_radii = [0.85, 0.68, 0.54, 0.42]
mango_parts.append(create_curved_branch(m_pts, m_radii, mat_mango_bark, "Mango_Trunk"))

m_branches = [
    ([(0.0, 0.05, 3.8), (1.6, 1.2, 5.2), (2.8, 2.0, 6.2)], [0.35, 0.25, 0.16]),
    ([(0.0, 0.05, 3.9), (-1.5, 1.4, 5.3), (-2.6, 2.2, 6.3)], [0.34, 0.24, 0.15]),
    ([(0.0, 0.05, 3.7), (1.4, -1.5, 5.1), (2.5, -2.4, 6.1)], [0.34, 0.24, 0.15]),
    ([(0.0, 0.05, 3.8), (-1.6, -1.3, 5.2), (-2.7, -2.1, 6.2)], [0.33, 0.23, 0.15])
]
for i, (pts, rads) in enumerate(m_branches):
    mango_parts.append(create_curved_branch(pts, rads, mat_mango_bark, f"Mango_Bough_{i}"))

mango_foliage_specs = [
    ((0.0, 0.0, 7.0), (4.5, 4.4, 3.2)),
    ((2.2, 1.6, 6.4), (3.4, 3.2, 2.4)),
    ((-2.0, 1.8, 6.5), (3.3, 3.1, 2.3)),
    ((1.8, -1.8, 6.3), (3.3, 3.2, 2.3)),
    ((-2.1, -1.6, 6.4), (3.4, 3.1, 2.4)),
    ((0.0, 0.0, 8.8), (3.2, 3.1, 2.2))
]
for i, (pos, scale) in enumerate(mango_foliage_specs):
    add_organic_foliage_clump(pos, scale, mat_mango_leaves, f"Mango_Foliage_{i}")

# 12 Hanging mango fruits
for i in range(12):
    ang = (i / 12.0) * math.pi * 2.0
    r = 2.4 + (i % 3) * 0.5
    fx = math.cos(ang) * r
    fy = math.sin(ang) * r
    fz = 5.2 + (i % 4) * 0.4
    bpy.ops.mesh.primitive_uv_sphere_add(radius=0.18, location=(fx, fy, fz))
    fr_obj = bpy.context.active_object
    fr_obj.scale = (0.9, 0.9, 1.3)
    fr_obj.data.materials.append(mat_mango_fruit)

bpy.ops.object.select_all(action='SELECT')
active_mango = mango_parts[0]
bpy.context.view_layer.objects.active = active_mango
bpy.ops.object.join()
active_mango.name = "Tree_Wild_Mango"

export_glb(os.path.join(STATIC_FRUIT, "mango_fruit_tree.glb"))
export_glb(os.path.join(ASSETS_FRUIT, "mango_fruit_tree.glb"))

print("=== ALL 4 TREE GLBS REBUILT WITH ORGANIC DISPLACED FOLIAGE CLUMPS! ===")

