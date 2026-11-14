import bpy
import math
import os

PROJECT_DIR = r"D:\Simulation For DT\prw-wild-digital-twin"
DOWNLOAD_DIR = os.path.join(PROJECT_DIR, "assets", "downloads", "polyhaven")

BARK_DIFF = os.path.join(DOWNLOAD_DIR, "bark_brown_01_diff_1k.jpg")
BARK_NOR = os.path.join(DOWNLOAD_DIR, "bark_brown_01_nor_gl_1k.jpg")
BARK_ROUGH = os.path.join(DOWNLOAD_DIR, "bark_brown_01_rough_1k.jpg")

LEAF_DIFF = os.path.join(DOWNLOAD_DIR, "forest_leaves_02_diff_1k.jpg")
LEAF_NOR = os.path.join(DOWNLOAD_DIR, "forest_leaves_02_nor_gl_1k.jpg")
LEAF_ROUGH = os.path.join(DOWNLOAD_DIR, "forest_leaves_02_rough_1k.jpg")

STATIC_TREES = os.path.join(PROJECT_DIR, "src", "prw_wild", "web", "static", "assets", "environment", "trees")
ASSETS_TREES = os.path.join(PROJECT_DIR, "assets", "environment", "trees")
STATIC_FRUIT = os.path.join(PROJECT_DIR, "src", "prw_wild", "web", "static", "assets", "environment", "fruit_trees")
ASSETS_FRUIT = os.path.join(PROJECT_DIR, "assets", "environment", "fruit_trees")

def clear_scene():
    bpy.ops.wm.read_factory_settings(use_empty=True)

def create_pbr_material(name, diff_path, nor_path, rough_path, base_color_fallback=(0.2, 0.2, 0.2, 1.0)):
    mat = bpy.data.materials.new(name=name)
    mat.use_nodes = True
    nt = mat.node_tree
    nt.nodes.clear()
    
    out_node = nt.nodes.new(type="ShaderNodeOutputMaterial")
    bsdf = nt.nodes.new(type="ShaderNodeBsdfPrincipled")
    nt.links.new(bsdf.outputs["BSDF"], out_node.inputs["Surface"])
    
    if os.path.exists(diff_path):
        tex_diff = nt.nodes.new(type="ShaderNodeTexImage")
        tex_diff.image = bpy.data.images.load(diff_path)
        nt.links.new(tex_diff.outputs["Color"], bsdf.inputs["Base Color"])
    else:
        bsdf.inputs["Base Color"].default_value = base_color_fallback
        
    if os.path.exists(rough_path):
        tex_rough = nt.nodes.new(type="ShaderNodeTexImage")
        img_r = bpy.data.images.load(rough_path)
        img_r.colorspace_settings.name = 'Non-Color'
        tex_rough.image = img_r
        nt.links.new(tex_rough.outputs["Color"], bsdf.inputs["Roughness"])
    else:
        bsdf.inputs["Roughness"].default_value = 0.85
        
    if os.path.exists(nor_path):
        tex_nor = nt.nodes.new(type="ShaderNodeTexImage")
        img_n = bpy.data.images.load(nor_path)
        img_n.colorspace_settings.name = 'Non-Color'
        tex_nor.image = img_n
        node_map = nt.nodes.new(type="ShaderNodeNormalMap")
        node_map.inputs["Strength"].default_value = 1.0
        nt.links.new(tex_nor.outputs["Color"], node_map.inputs["Color"])
        nt.links.new(node_map.outputs["Normal"], bsdf.inputs["Normal"])
        
    bsdf.inputs["Metallic"].default_value = 0.0
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
    
    # UV Smart Project in EDIT mode
    bpy.ops.object.mode_set(mode='EDIT')
    bpy.ops.mesh.select_all(action='SELECT')
    bpy.ops.uv.smart_project(angle_limit=66.0, island_margin=0.02)
    bpy.ops.object.mode_set(mode='OBJECT')
    return curve_obj

def add_organic_foliage_clump(location, scale, mat, name="Foliage"):
    bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=3, radius=1.0, location=location)
    obj = bpy.context.active_object
    obj.name = name
    obj.scale = scale
    
    tex = bpy.data.textures.new(name=f"{name}_Noise", type='CLOUDS')
    tex.noise_scale = 0.45
    tex.noise_depth = 2
    
    disp = obj.modifiers.new(name="Displace", type='DISPLACE')
    disp.texture = tex
    disp.strength = 0.22
    bpy.ops.object.modifier_apply(modifier="Displace")
    
    obj.data.materials.append(mat)
    
    bpy.context.view_layer.objects.active = obj
    obj.select_set(True)
    bpy.ops.object.mode_set(mode='EDIT')
    bpy.ops.mesh.select_all(action='SELECT')
    bpy.ops.uv.smart_project(angle_limit=66.0, island_margin=0.02)
    bpy.ops.object.mode_set(mode='OBJECT')
    return obj

def export_tree(name, static_dir, assets_dir):
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.transform_apply(location=False, rotation=True, scale=True)
    
    for d in [static_dir, assets_dir]:
        os.makedirs(d, exist_ok=True)
        fp = os.path.join(d, f"{name}.glb")
        bpy.ops.export_scene.gltf(
            filepath=fp,
            export_format='GLB',
            use_selection=False,
            export_apply=True,
            export_materials='EXPORT',
            export_yup=True
        )
        print(f"Exported PBR Tree GLB: {fp} ({os.path.getsize(fp)/1024:.1f} KB)")

# =========================================================================
# 1. ACACIA CANOPY TREE
# =========================================================================
print("=== Rebuilding Acacia Canopy Tree with Poly Haven PBR Textures ===")
clear_scene()
mat_bark = create_pbr_material("M_Bark_Acacia_PBR", BARK_DIFF, BARK_NOR, BARK_ROUGH)
mat_leaves = create_pbr_material("M_Foliage_Acacia_PBR", LEAF_DIFF, LEAF_NOR, LEAF_ROUGH)

a_pts = [(0.0, 0.0, 0.0), (0.4, 0.2, 1.8), (0.9, 0.5, 3.4), (1.5, 0.9, 5.0)]
a_radii = [0.65, 0.52, 0.42, 0.35]
create_curved_branch(a_pts, a_radii, mat_bark, "Acacia_Trunk")

# Spreading horizontal branches
b1_pts = [(1.5, 0.9, 5.0), (2.8, 1.8, 5.8), (4.2, 2.5, 6.2)]
create_curved_branch(b1_pts, [0.35, 0.25, 0.15], mat_bark, "Acacia_Branch_N")

b2_pts = [(1.5, 0.9, 5.0), (0.2, -0.6, 5.6), (-1.2, -1.8, 6.0)]
create_curved_branch(b2_pts, [0.35, 0.25, 0.15], mat_bark, "Acacia_Branch_S")

b3_pts = [(1.5, 0.9, 5.0), (2.2, -0.4, 5.7), (3.2, -1.5, 6.1)]
create_curved_branch(b3_pts, [0.32, 0.22, 0.14], mat_bark, "Acacia_Branch_E")

b4_pts = [(1.5, 0.9, 5.0), (0.6, 2.1, 5.7), (-0.4, 3.0, 6.1)]
create_curved_branch(b4_pts, [0.32, 0.22, 0.14], mat_bark, "Acacia_Branch_W")

# Broad umbrella canopy clumps
add_organic_foliage_clump((1.8, 0.9, 6.4), (4.2, 4.2, 1.1), mat_leaves, "Acacia_Canopy_Center")
add_organic_foliage_clump((4.2, 2.5, 6.6), (2.8, 2.8, 0.9), mat_leaves, "Acacia_Canopy_North")
add_organic_foliage_clump((-1.2, -1.8, 6.4), (2.6, 2.6, 0.85), mat_leaves, "Acacia_Canopy_South")
add_organic_foliage_clump((3.2, -1.5, 6.5), (2.5, 2.5, 0.85), mat_leaves, "Acacia_Canopy_East")
add_organic_foliage_clump((-0.4, 3.0, 6.5), (2.5, 2.5, 0.85), mat_leaves, "Acacia_Canopy_West")
export_tree("acacia_canopy", STATIC_TREES, ASSETS_TREES)

# =========================================================================
# 2. BANYAN FIG TREE
# =========================================================================
print("=== Rebuilding Banyan Fig Tree with Poly Haven PBR Textures ===")
clear_scene()
mat_bark = create_pbr_material("M_Bark_Banyan_PBR", BARK_DIFF, BARK_NOR, BARK_ROUGH)
mat_leaves = create_pbr_material("M_Foliage_Banyan_PBR", LEAF_DIFF, LEAF_NOR, LEAF_ROUGH)

trunk_pts = [(0.0, 0.0, 0.0), (0.2, -0.1, 1.5), (0.1, 0.2, 3.0), (0.0, 0.0, 4.5)]
create_curved_branch(trunk_pts, [1.3, 1.1, 0.95, 0.8], mat_bark, "Banyan_Central_Trunk")

# Massive lateral boughs
bb1_pts = [(0.0, 0.0, 4.0), (2.2, 1.4, 4.8), (4.5, 2.2, 5.2), (6.5, 2.8, 5.0)]
create_curved_branch(bb1_pts, [0.7, 0.55, 0.42, 0.3], mat_bark, "Banyan_Bough_East")

bb2_pts = [(0.0, 0.0, 4.0), (-2.0, -1.2, 4.7), (-4.2, -2.0, 5.0), (-6.0, -2.5, 4.8)]
create_curved_branch(bb2_pts, [0.68, 0.52, 0.4, 0.28], mat_bark, "Banyan_Bough_West")

bb3_pts = [(0.0, 0.0, 4.0), (1.2, -2.4, 4.6), (2.0, -4.5, 4.9)]
create_curved_branch(bb3_pts, [0.6, 0.45, 0.32], mat_bark, "Banyan_Bough_South")

bb4_pts = [(0.0, 0.0, 4.0), (-1.2, 2.2, 4.6), (-2.2, 4.2, 5.0)]
create_curved_branch(bb4_pts, [0.6, 0.45, 0.32], mat_bark, "Banyan_Bough_North")

# Aerial prop roots descending to soil
p1_pts = [(4.5, 2.2, 5.2), (4.4, 2.1, 2.5), (4.3, 2.0, 0.0)]
create_curved_branch(p1_pts, [0.22, 0.24, 0.28], mat_bark, "Prop_Root_E1")

p2_pts = [(-4.2, -2.0, 5.0), (-4.1, -1.9, 2.5), (-4.0, -1.8, 0.0)]
create_curved_branch(p2_pts, [0.2, 0.22, 0.26], mat_bark, "Prop_Root_W1")

p3_pts = [(2.0, -4.5, 4.9), (2.0, -4.4, 2.4), (2.0, -4.3, 0.0)]
create_curved_branch(p3_pts, [0.18, 0.2, 0.24], mat_bark, "Prop_Root_S1")

# Sprawling dense foliage
add_organic_foliage_clump((0.0, 0.0, 6.2), (5.5, 5.5, 2.4), mat_leaves, "Banyan_Canopy_Center")
add_organic_foliage_clump((5.5, 2.5, 5.8), (4.0, 3.8, 2.0), mat_leaves, "Banyan_Canopy_East")
add_organic_foliage_clump((-5.2, -2.2, 5.6), (3.8, 3.6, 1.9), mat_leaves, "Banyan_Canopy_West")
add_organic_foliage_clump((1.8, -4.0, 5.6), (3.5, 3.5, 1.8), mat_leaves, "Banyan_Canopy_South")
add_organic_foliage_clump((-2.0, 3.8, 5.6), (3.5, 3.5, 1.8), mat_leaves, "Banyan_Canopy_North")
export_tree("banyan_fig", STATIC_TREES, ASSETS_TREES)

# =========================================================================
# 3. SAL MATURE FOREST TREE
# =========================================================================
print("=== Rebuilding Sal Mature Tree with Poly Haven PBR Textures ===")
clear_scene()
mat_bark = create_pbr_material("M_Bark_Sal_PBR", BARK_DIFF, BARK_NOR, BARK_ROUGH)
mat_leaves = create_pbr_material("M_Foliage_Sal_PBR", LEAF_DIFF, LEAF_NOR, LEAF_ROUGH)

s_pts = [(0.0, 0.0, 0.0), (0.1, 0.05, 3.0), (-0.05, 0.1, 6.0), (0.05, -0.05, 9.0), (0.0, 0.0, 11.5)]
create_curved_branch(s_pts, [0.95, 0.78, 0.62, 0.48, 0.35], mat_bark, "Sal_Trunk")

# Buttress flaring
for deg in [0, 90, 180, 270]:
    rad = math.radians(deg)
    bx = math.cos(rad) * 1.4
    by = math.sin(rad) * 1.4
    b_pts = [(0.0, 0.0, 1.8), (bx * 0.6, by * 0.6, 0.6), (bx, by, 0.0)]
    create_curved_branch(b_pts, [0.45, 0.35, 0.15], mat_bark, f"Sal_Buttress_{deg}")

# High canopy boughs
sb1 = [(0.05, -0.05, 9.0), (1.4, 0.8, 10.4), (2.4, 1.2, 11.2)]
create_curved_branch(sb1, [0.35, 0.25, 0.16], mat_bark, "Sal_Bough_E")
sb2 = [(0.05, -0.05, 9.0), (-1.3, -0.7, 10.3), (-2.2, -1.1, 11.0)]
create_curved_branch(sb2, [0.35, 0.25, 0.16], mat_bark, "Sal_Bough_W")

# Multi-tiered vertical crown
add_organic_foliage_clump((0.0, 0.0, 13.0), (2.8, 2.8, 3.2), mat_leaves, "Sal_Apex_Crown")
add_organic_foliage_clump((1.8, 1.0, 11.6), (2.5, 2.4, 2.5), mat_leaves, "Sal_Mid_Crown_E")
add_organic_foliage_clump((-1.7, -0.9, 11.4), (2.4, 2.5, 2.4), mat_leaves, "Sal_Mid_Crown_W")
add_organic_foliage_clump((0.0, 0.0, 10.0), (3.4, 3.4, 2.6), mat_leaves, "Sal_Lower_Crown")
export_tree("sal_mature", STATIC_TREES, ASSETS_TREES)

# =========================================================================
# 4. WILD MANGO FRUIT TREE
# =========================================================================
print("=== Rebuilding Wild Mango Fruit Tree with Poly Haven PBR Textures ===")
clear_scene()
mat_bark = create_pbr_material("M_Bark_Mango_PBR", BARK_DIFF, BARK_NOR, BARK_ROUGH)
mat_leaves = create_pbr_material("M_Foliage_Mango_PBR", LEAF_DIFF, LEAF_NOR, LEAF_ROUGH)

m_pts = [(0.0, 0.0, 0.0), (-0.2, 0.1, 1.2), (-0.3, 0.2, 2.5)]
create_curved_branch(m_pts, [0.75, 0.65, 0.55], mat_bark, "Mango_Trunk")

# Low spreading branches
mb1 = [(-0.3, 0.2, 2.5), (1.2, 0.8, 3.6), (2.5, 1.4, 4.2)]
create_curved_branch(mb1, [0.45, 0.32, 0.22], mat_bark, "Mango_Branch_1")
mb2 = [(-0.3, 0.2, 2.5), (-1.5, -0.8, 3.4), (-2.8, -1.2, 4.0)]
create_curved_branch(mb2, [0.42, 0.3, 0.2], mat_bark, "Mango_Branch_2")
mb3 = [(-0.3, 0.2, 2.5), (0.2, -1.6, 3.5), (0.5, -2.8, 4.1)]
create_curved_branch(mb3, [0.42, 0.3, 0.2], mat_bark, "Mango_Branch_3")

# Dense rounded dome canopy
add_organic_foliage_clump((0.0, 0.0, 5.2), (4.6, 4.6, 2.8), mat_leaves, "Mango_Dome_Center")
add_organic_foliage_clump((2.0, 1.2, 4.6), (3.0, 3.0, 2.2), mat_leaves, "Mango_Dome_East")
add_organic_foliage_clump((-2.2, -1.0, 4.5), (3.0, 3.0, 2.2), mat_leaves, "Mango_Dome_West")
add_organic_foliage_clump((0.4, -2.2, 4.5), (2.8, 2.8, 2.0), mat_leaves, "Mango_Dome_South")

# Mango fruits
mat_fruit = bpy.data.materials.new(name="M_Mango_Fruit_PBR")
mat_fruit.use_nodes = True
bf = mat_fruit.node_tree.nodes.get("Principled BSDF")
if bf:
    bf.inputs["Base Color"].default_value = (0.95, 0.65, 0.12, 1.0)
    bf.inputs["Roughness"].default_value = 0.35

fruit_positions = [
    (1.5, 1.0, 3.5), (2.2, 1.4, 3.2), (-1.2, -0.8, 3.2),
    (-2.0, -1.0, 3.0), (0.3, -1.8, 3.3), (0.5, -2.4, 3.1),
    (1.0, -1.2, 3.6), (-1.5, 1.2, 3.4)
]
for i, fp in enumerate(fruit_positions):
    bpy.ops.mesh.primitive_uv_sphere_add(segments=8, ring_count=8, radius=0.22, location=fp)
    f_obj = bpy.context.active_object
    f_obj.name = f"Mango_Fruit_{i}"
    f_obj.scale = (1.0, 0.8, 1.4)
    f_obj.data.materials.append(mat_fruit)

export_tree("mango_fruit_tree", STATIC_FRUIT, ASSETS_FRUIT)
print("=== All 4 Core Trees Rebuilt with Genuine Poly Haven PBR Materials! ===")
