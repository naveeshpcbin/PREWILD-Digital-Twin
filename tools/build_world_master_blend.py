"""
PRW-Wild Master Blender World & 16-Collection Production Pipeline
Author: PRW-Wild Autonomous Engineering Team
Blender: 5.2.2 LTS (D:\\PROJECTS\\blender.exe)
Creates:
  - assets/blender_source/PRW_WILD_WORLD_MASTER.blend
  - assets/blender_source/PRW_WILD_PRODUCTION_WORLD.blend
Collections (16 required):
  1. WORLD_TERRAIN
  2. WORLD_FOREST
  3. WORLD_VEGETATION
  4. WORLD_GROUND_COVER
  5. WORLD_RESOURCES
  6. WORLD_WATER
  7. WORLD_FARMLAND
  8. WORLD_BOUNDARY
  9. ANIMALS_ASIAN_ELEPHANT
  10. ANIMALS_CHITAL
  11. ANIMALS_SAMBAR
  12. ANIMALS_WILD_BOAR
  13. ANIMALS_GAUR
  14. ANIMALS_MONKEY
  15. SENSING_INFRASTRUCTURE
  16. SURVEILLANCE_CAMERAS
Also exports and mirrors all production GLB models into assets/ and web/static/assets/.
"""

import bpy
import math
import os
import shutil
from mathutils import Vector, Matrix, Euler

PROJECT_DIR = r"D:\Simulation For DT\prw-wild-digital-twin"
ASSETS_DIR = os.path.join(PROJECT_DIR, "assets")
STATIC_ASSETS_DIR = os.path.join(PROJECT_DIR, "src", "prw_wild", "web", "static", "assets")
MASTER_BLEND_PATH = os.path.join(ASSETS_DIR, "blender_source", "PRW_WILD_WORLD_MASTER.blend")
PROD_BLEND_PATH = os.path.join(ASSETS_DIR, "blender_source", "PRW_WILD_PRODUCTION_WORLD.blend")

COLLECTIONS_16 = [
    "WORLD_TERRAIN",
    "WORLD_FOREST",
    "WORLD_VEGETATION",
    "WORLD_GROUND_COVER",
    "WORLD_RESOURCES",
    "WORLD_WATER",
    "WORLD_FARMLAND",
    "WORLD_BOUNDARY",
    "ANIMALS_ASIAN_ELEPHANT",
    "ANIMALS_CHITAL",
    "ANIMALS_SAMBAR",
    "ANIMALS_WILD_BOAR",
    "ANIMALS_GAUR",
    "ANIMALS_MONKEY",
    "SENSING_INFRASTRUCTURE",
    "SURVEILLANCE_CAMERAS",
]

LEGACY_COMPAT_COLLECTIONS = [
    "ENV_TERRAIN", "ENV_FOREST", "ENV_VEGETATION", "ENV_GRASS", "ENV_FRUIT_TREES",
    "ENV_WATER", "ENV_FARMLAND", "ENV_BOUNDARY", "SPECIES_ELEPHANT", "SPECIES_DEER",
    "SPECIES_WILD_BOAR", "SPECIES_GAUR", "SPECIES_MONKEY", "SENSOR_ASSETS", "CAMERA_ASSETS"
]

def ensure_dirs():
    os.makedirs(os.path.dirname(MASTER_BLEND_PATH), exist_ok=True)
    subdirs = [
        "environment/terrain", "environment/trees", "environment/fruit_trees",
        "environment/vegetation", "environment/grass", "environment/water",
        "environment/farmland", "environment/boundary", "environment/shrubs",
        "animals/elephant", "animals/deer", "animals/boar", "animals/gaur", "animals/monkey",
        "cameras", "sensors", "hardware"
    ]
    for d in subdirs:
        os.makedirs(os.path.join(ASSETS_DIR, d), exist_ok=True)
        os.makedirs(os.path.join(STATIC_ASSETS_DIR, d), exist_ok=True)

def reset_scene():
    bpy.ops.wm.read_factory_settings(use_empty=True)
    for c in list(bpy.data.collections):
        bpy.data.collections.remove(c)

def setup_collections():
    cols = {}
    root = bpy.context.scene.collection
    for name in COLLECTIONS_16 + LEGACY_COMPAT_COLLECTIONS:
        c = bpy.data.collections.new(name)
        root.children.link(c)
        cols[name] = c
    return cols

def make_material(name, color_rgba, roughness=0.8, metalness=0.0, transmission=0.0):
    mat = bpy.data.materials.new(name=name)
    mat.use_nodes = True
    nodes = mat.node_tree.nodes
    bsdf = nodes.get("Principled BSDF")
    if bsdf:
        bsdf.inputs["Base Color"].default_value = color_rgba
        bsdf.inputs["Roughness"].default_value = roughness
        bsdf.inputs["Metallic"].default_value = metalness
        if "Transmission Weight" in bsdf.inputs:
            bsdf.inputs["Transmission Weight"].default_value = transmission
        elif "Transmission" in bsdf.inputs:
            bsdf.inputs["Transmission"].default_value = transmission
    return mat

def link_to_col(obj, col, also_cols=None):
    for c in list(obj.users_collection):
        c.objects.unlink(obj)
    col.objects.link(obj)
    if also_cols:
        for extra in also_cols:
            if obj.name not in extra.objects:
                extra.objects.link(obj)

# ---------------------------------------------------------------------------
# 1. Sculpted Natural Terrain
# ---------------------------------------------------------------------------
def build_sculpted_terrain(col, also_col=None):
    nx, nz = 120, 120
    x_min, x_max = -25.0, 225.0
    z_min, z_max = -30.0, 230.0
    dx = (x_max - x_min) / (nx - 1)
    dz = (z_max - z_min) / (nz - 1)

    verts = []
    faces = []

    for iz in range(nz):
        z = z_min + iz * dz
        for ix in range(nx):
            x = x_min + ix * dx
            base_elev = (100.0 - x) * 0.015 if x < 100 else -(x - 100.0) * 0.005

            if x < 100:
                hills = (
                    math.sin(x * 0.065 + 1.2) * math.cos(z * 0.055) * 1.8 +
                    math.sin(x * 0.12 - 0.5) * math.cos(z * 0.11 + 0.8) * 0.75 +
                    math.sin(x * 0.22) * math.sin(z * 0.19) * 0.35
                )
                west_ridge = max(0.0, (40.0 - x) * 0.08)
                y = base_elev + hills + west_ridge
            else:
                ter_idx = math.floor((x - 100.0) / 28.0)
                ter_rem = (x - 100.0) % 28.0
                farm_grade = -ter_idx * 0.35 - (ter_rem / 28.0) * 0.08
                furrows = math.sin(z * 1.1) * 0.06
                y = farm_grade + furrows

            corr_dist_z = abs(z - (100.0 + math.sin(x * 0.05) * 6.0))
            if corr_dist_z < 22.0 and x < 105:
                corr_factor = (1.0 - (corr_dist_z / 22.0)) ** 2
                y -= corr_factor * 2.2

            dist_p1 = math.hypot(x - 75.0, z - 140.0)
            if dist_p1 < 22.0:
                depth1 = (1.0 - (dist_p1 / 22.0)) ** 1.8
                y -= depth1 * 2.4

            dist_p2 = math.hypot(x - 45.0, z - 60.0)
            if dist_p2 < 18.0:
                depth2 = (1.0 - (dist_p2 / 18.0)) ** 1.8
                y -= depth2 * 2.1

            micro = (math.sin(x * 1.7 + z * 1.3) * 0.04)
            y += micro
            verts.append((x, y, z))

    for iz in range(nz - 1):
        for ix in range(nx - 1):
            v0 = iz * nx + ix
            v1 = v0 + 1
            v2 = (iz + 1) * nx + ix + 1
            v3 = (iz + 1) * nx + ix
            faces.append((v0, v1, v2, v3))

    mesh = bpy.data.meshes.new("Terrain_World_Mesh")
    mesh.from_pydata(verts, [], faces)
    mesh.update()

    obj = bpy.data.objects.new("Terrain_Production_World", mesh)
    link_to_col(obj, col, [also_col] if also_col else None)

    bpy.context.view_layer.objects.active = obj
    obj.select_set(True)
    bpy.ops.object.shade_smooth()

    mat_terrain = make_material("M_Terrain_Natural", (0.28, 0.32, 0.18, 1.0), roughness=0.92)
    obj.data.materials.append(mat_terrain)
    return obj

# ---------------------------------------------------------------------------
# 2. Forest Trees (Sal, Banyan, Acacia)
# ---------------------------------------------------------------------------
def build_sal_tree(col, also_col=None):
    bpy.ops.mesh.primitive_cylinder_add(radius=0.65, depth=8.5, vertices=12, location=(0, 4.25, 0))
    trunk = bpy.context.active_object
    trunk.name = "Tree_Sal_Trunk"

    mat_bark = make_material("M_Bark_Sal", (0.22, 0.16, 0.12, 1.0), roughness=0.9)
    mat_foliage = make_material("M_Foliage_Sal", (0.12, 0.30, 0.08, 1.0), roughness=0.75)
    trunk.data.materials.append(mat_bark)

    foliage_objs = []
    clump_specs = [
        (0.0, 9.8, 0.0, 3.8, 3.2),
        (1.8, 8.2, 1.2, 2.8, 2.4),
        (-1.6, 7.6, -1.0, 2.7, 2.3),
        (1.2, 6.8, -1.5, 2.4, 2.0),
        (-1.4, 6.5, 1.4, 2.5, 2.1),
        (0.0, 11.2, 0.0, 2.6, 2.6),
    ]
    for cx, cy, cz, rx, ry in clump_specs:
        bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=3, radius=rx, location=(cx, cy, cz))
        clump = bpy.context.active_object
        clump.scale = (1.0, ry / rx, 1.0)
        clump.data.materials.append(mat_foliage)
        foliage_objs.append(clump)

    bpy.ops.object.select_all(action='DESELECT')
    for o in foliage_objs:
        o.select_set(True)
    trunk.select_set(True)
    bpy.context.view_layer.objects.active = trunk
    bpy.ops.object.join()
    trunk.name = "Tree_Sal_Mature"
    link_to_col(trunk, col, [also_col] if also_col else None)
    return trunk

def build_banyan_tree(col, also_col=None):
    bpy.ops.mesh.primitive_cylinder_add(radius=1.2, depth=6.0, vertices=14, location=(0, 3.0, 0))
    trunk = bpy.context.active_object
    trunk.name = "Tree_Banyan_Trunk"

    mat_bark = make_material("M_Bark_Banyan", (0.26, 0.22, 0.18, 1.0), roughness=0.88)
    mat_leaves = make_material("M_Foliage_Banyan", (0.09, 0.26, 0.07, 1.0), roughness=0.7)
    trunk.data.materials.append(mat_bark)

    parts = []
    prop_angles = [0.0, 1.05, 2.09, 3.14, 4.19, 5.24]
    for a in prop_angles:
        px = math.cos(a) * 3.4
        pz = math.sin(a) * 3.4
        bpy.ops.mesh.primitive_cylinder_add(radius=0.22, depth=5.5, vertices=8, location=(px, 2.75, pz))
        proot = bpy.context.active_object
        proot.data.materials.append(mat_bark)
        parts.append(proot)

    canopy_specs = [
        (0.0, 7.8, 0.0, 6.2, 2.8),
        (3.5, 6.5, 1.8, 4.4, 2.2),
        (-3.2, 6.4, -2.1, 4.2, 2.2),
        (1.5, 6.6, -3.6, 4.0, 2.0),
        (-2.0, 6.7, 3.4, 4.3, 2.2),
        (0.0, 9.4, 0.0, 4.5, 2.0),
    ]
    for cx, cy, cz, rx, ry in canopy_specs:
        bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=3, radius=rx, location=(cx, cy, cz))
        dome = bpy.context.active_object
        dome.scale = (1.0, ry / rx, 1.0)
        dome.data.materials.append(mat_leaves)
        parts.append(dome)

    bpy.ops.object.select_all(action='DESELECT')
    for p in parts:
        p.select_set(True)
    trunk.select_set(True)
    bpy.context.view_layer.objects.active = trunk
    bpy.ops.object.join()
    trunk.name = "Tree_Banyan_Sprawling"
    link_to_col(trunk, col, [also_col] if also_col else None)
    return trunk

def build_acacia_tree(col, also_col=None):
    bpy.ops.mesh.primitive_cylinder_add(radius=0.45, depth=5.5, vertices=10, location=(0.4, 2.75, 0.2))
    trunk = bpy.context.active_object
    trunk.rotation_euler = (0.12, 0.0, -0.15)
    trunk.name = "Tree_Acacia_Trunk"

    mat_bark = make_material("M_Bark_Acacia", (0.30, 0.24, 0.17, 1.0), roughness=0.92)
    mat_leaves = make_material("M_Foliage_Acacia", (0.16, 0.35, 0.10, 1.0), roughness=0.8)
    trunk.data.materials.append(mat_bark)

    parts = []
    umbrella_specs = [
        (0.8, 6.2, 0.4, 4.8, 0.9),
        (-1.2, 5.4, -1.0, 3.6, 0.75),
        (2.0, 5.2, 1.5, 3.2, 0.7),
        (0.5, 7.3, 0.2, 3.4, 0.7),
    ]
    for cx, cy, cz, r, h in umbrella_specs:
        bpy.ops.mesh.primitive_cylinder_add(radius=r, depth=h, vertices=16, location=(cx, cy, cz))
        can = bpy.context.active_object
        can.data.materials.append(mat_leaves)
        parts.append(can)

    bpy.ops.object.select_all(action='DESELECT')
    for p in parts:
        p.select_set(True)
    trunk.select_set(True)
    bpy.context.view_layer.objects.active = trunk
    bpy.ops.object.join()
    trunk.name = "Tree_Acacia_Canopy"
    link_to_col(trunk, col, [also_col] if also_col else None)
    return trunk

# ---------------------------------------------------------------------------
# 3. Resources (Wild Mango Tree with Fruit)
# ---------------------------------------------------------------------------
def build_mango_fruit_tree(col, also_col=None):
    bpy.ops.mesh.primitive_cylinder_add(radius=0.7, depth=6.2, vertices=12, location=(0, 3.1, 0))
    trunk = bpy.context.active_object
    trunk.name = "Tree_Mango_Trunk"

    mat_bark = make_material("M_Bark_Mango", (0.24, 0.18, 0.13, 1.0), roughness=0.88)
    mat_foliage = make_material("M_Foliage_Mango", (0.08, 0.28, 0.06, 1.0), roughness=0.68)
    mat_fruit = make_material("M_Mango_Fruit", (0.95, 0.65, 0.08, 1.0), roughness=0.45)
    trunk.data.materials.append(mat_bark)

    parts = []
    canopy_layers = [
        (0.0, 6.8, 0.0, 4.8, 3.2),
        (1.5, 6.0, 1.2, 3.5, 2.4),
        (-1.4, 5.8, -1.1, 3.4, 2.3),
        (0.0, 8.4, 0.0, 3.2, 2.6),
    ]
    for cx, cy, cz, rx, ry in canopy_layers:
        bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=3, radius=rx, location=(cx, cy, cz))
        dome = bpy.context.active_object
        dome.scale = (1.0, ry / rx, 1.0)
        dome.data.materials.append(mat_foliage)
        parts.append(dome)

    # 18 Hanging mango fruits
    for i in range(18):
        ang = (i / 18.0) * math.pi * 2.0
        rad = 2.4 + math.sin(i * 1.7) * 0.9
        fx = math.cos(ang) * rad
        fz = math.sin(ang) * rad
        fy = 4.2 + (i % 3) * 0.45
        bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=2, radius=0.22, location=(fx, fy, fz))
        fruit = bpy.context.active_object
        fruit.scale = (0.75, 1.15, 0.85)
        fruit.data.materials.append(mat_fruit)
        parts.append(fruit)

    bpy.ops.object.select_all(action='DESELECT')
    for p in parts:
        p.select_set(True)
    trunk.select_set(True)
    bpy.context.view_layer.objects.active = trunk
    bpy.ops.object.join()
    trunk.name = "Tree_Wild_Mango"
    link_to_col(trunk, col, [also_col] if also_col else None)
    return trunk

# ---------------------------------------------------------------------------
# 4. Vegetation & Ground Cover
# ---------------------------------------------------------------------------
def build_forest_ferns(col, also_col=None):
    # Cluster of arched 3D fronds
    mat_fern = make_material("M_Fern_Frond", (0.10, 0.42, 0.08, 1.0), roughness=0.6)
    fronds = []
    for i in range(16):
        ang = (i / 16.0) * math.pi * 2.0
        tilt = 0.55 + (i % 3) * 0.12
        bpy.ops.mesh.primitive_cone_add(radius1=0.28, radius2=0.02, depth=2.2, vertices=8, location=(0, 0.9, 0))
        frond = bpy.context.active_object
        frond.rotation_euler = (tilt, 0.0, ang)
        frond.location = (math.cos(ang) * 0.35, 0.3, math.sin(ang) * 0.35)
        frond.data.materials.append(mat_fern)
        fronds.append(frond)

    bpy.ops.object.select_all(action='DESELECT')
    for f in fronds:
        f.select_set(True)
    bpy.context.view_layer.objects.active = fronds[0]
    bpy.ops.object.join()
    ferns = bpy.context.active_object
    ferns.name = "Forest_Fern_Clump"
    link_to_col(ferns, col, [also_col] if also_col else None)
    return ferns

def build_forest_shrub(col, also_col=None):
    mat_shrub_stem = make_material("M_Shrub_Stem", (0.28, 0.22, 0.15, 1.0), roughness=0.9)
    mat_shrub_fol = make_material("M_Shrub_Foliage", (0.14, 0.32, 0.10, 1.0), roughness=0.75)

    bpy.ops.mesh.primitive_cylinder_add(radius=0.15, depth=1.2, vertices=8, location=(0, 0.6, 0))
    base = bpy.context.active_object
    base.data.materials.append(mat_shrub_stem)

    parts = []
    clump_coords = [
        (0.0, 1.1, 0.0, 0.95),
        (0.5, 0.85, 0.4, 0.75),
        (-0.45, 0.9, -0.35, 0.7),
        (0.35, 0.8, -0.45, 0.65),
        (-0.4, 0.75, 0.45, 0.68),
    ]
    for cx, cy, cz, rad in clump_coords:
        bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=2, radius=rad, location=(cx, cy, cz))
        c = bpy.context.active_object
        c.data.materials.append(mat_shrub_fol)
        parts.append(c)

    bpy.ops.object.select_all(action='DESELECT')
    for p in parts:
        p.select_set(True)
    base.select_set(True)
    bpy.context.view_layer.objects.active = base
    bpy.ops.object.join()
    base.name = "Forest_Shrub_Lantana"
    link_to_col(base, col, [also_col] if also_col else None)
    return base

def build_tall_grass(col, also_col=None):
    mat_grass = make_material("M_Tall_Grass", (0.22, 0.42, 0.12, 1.0), roughness=0.7)
    blades = []
    num_blades = 18
    for i in range(num_blades):
        ang = (i / num_blades) * math.pi * 2.0 + math.sin(i * 1.3) * 0.3
        h = 0.85 + (i % 5) * 0.12
        lean = 0.25 + (i % 3) * 0.08
        bx = math.cos(ang) * (0.15 + (i % 4) * 0.05)
        bz = math.sin(ang) * (0.15 + (i % 4) * 0.05)
        bpy.ops.mesh.primitive_cylinder_add(radius=0.04, depth=h, vertices=6, location=(bx, h * 0.5, bz))
        b = bpy.context.active_object
        b.rotation_euler = (lean * math.sin(ang), 0, lean * math.cos(ang))
        b.data.materials.append(mat_grass)
        blades.append(b)

    root = blades[0]
    bpy.ops.object.select_all(action='DESELECT')
    for b in blades:
        b.select_set(True)
    bpy.context.view_layer.objects.active = root
    bpy.ops.object.join()
    root.name = "Tall_Grass_Tuft"
    link_to_col(root, col, [also_col] if also_col else None)
    return root

# ---------------------------------------------------------------------------
# 5. Riparian Water Feature
# ---------------------------------------------------------------------------
def build_pond_basin(col, also_col=None):
    mat_basin = make_material("M_Pond_Shore", (0.22, 0.18, 0.12, 1.0), roughness=0.95)
    mat_water = make_material("M_Water_Surface", (0.05, 0.22, 0.32, 0.85), roughness=0.15, transmission=0.8)
    mat_rock = make_material("M_Pond_Boulder", (0.35, 0.33, 0.30, 1.0), roughness=0.88)
    mat_reed = make_material("M_Pond_Reeds", (0.18, 0.36, 0.14, 1.0), roughness=0.75)

    bpy.ops.mesh.primitive_cylinder_add(radius=18.0, depth=3.2, vertices=32, location=(0, -1.6, 0))
    basin = bpy.context.active_object
    basin.data.materials.append(mat_basin)

    parts = []
    bpy.ops.mesh.primitive_cylinder_add(radius=17.5, depth=0.15, vertices=32, location=(0, -0.6, 0))
    water = bpy.context.active_object
    water.data.materials.append(mat_water)
    parts.append(water)

    # 12 Shoreline boulders
    for i in range(12):
        ang = (i / 12.0) * math.pi * 2.0
        dist = 16.5 + math.sin(i * 2.1) * 1.5
        rx = math.cos(ang) * dist
        rz = math.sin(ang) * dist
        scale_r = 1.1 + (i % 3) * 0.35
        bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=2, radius=scale_r, location=(rx, -0.2, rz))
        b = bpy.context.active_object
        b.scale = (1.2, 0.7, 0.9)
        b.data.materials.append(mat_rock)
        parts.append(b)

    # 8 Cattail reed clusters
    for i in range(8):
        ang = (i / 8.0) * math.pi * 2.0 + 0.35
        dist = 14.5 + math.sin(i * 1.7) * 1.2
        rx = math.cos(ang) * dist
        rz = math.sin(ang) * dist
        bpy.ops.mesh.primitive_cylinder_add(radius=0.15, depth=2.4, vertices=6, location=(rx, 0.6, rz))
        reed = bpy.context.active_object
        reed.data.materials.append(mat_reed)
        parts.append(reed)

    bpy.ops.object.select_all(action='DESELECT')
    for p in parts:
        p.select_set(True)
    basin.select_set(True)
    bpy.context.view_layer.objects.active = basin
    bpy.ops.object.join()
    basin.name = "Pond_Basin_Carved"
    link_to_col(basin, col, [also_col] if also_col else None)
    return basin

# ---------------------------------------------------------------------------
# 6. Farmland (Crops & Machan Watchtower)
# ---------------------------------------------------------------------------
def build_crop_field(col, also_col=None):
    mat_soil = make_material("M_Farm_Furrow", (0.24, 0.17, 0.11, 1.0), roughness=0.94)
    mat_cane = make_material("M_Sugarcane_Stalk", (0.35, 0.48, 0.14, 1.0), roughness=0.65)

    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0, -0.15, 0))
    field = bpy.context.active_object
    field.scale = (32.0, 0.3, 32.0)
    field.data.materials.append(mat_soil)

    stalks = []
    for r in range(5):
        fz = -12.0 + r * 6.0
        for c in range(8):
            fx = -14.0 + c * 4.0
            bpy.ops.mesh.primitive_cylinder_add(radius=0.18, depth=2.6, vertices=6, location=(fx, 1.2, fz))
            cane = bpy.context.active_object
            cane.data.materials.append(mat_cane)
            stalks.append(cane)

    bpy.ops.object.select_all(action='DESELECT')
    for s in stalks:
        s.select_set(True)
    field.select_set(True)
    bpy.context.view_layer.objects.active = field
    bpy.ops.object.join()
    field.name = "Farmland_Crop_Parcels"
    link_to_col(field, col, [also_col] if also_col else None)
    return field

def build_watchtower_machan(col, also_col=None):
    mat_wood = make_material("M_Machan_Wood", (0.30, 0.20, 0.12, 1.0), roughness=0.85)
    mat_thatch = make_material("M_Machan_Roof", (0.42, 0.35, 0.18, 1.0), roughness=0.92)

    parts = []
    stilt_offsets = [(-2.0, -2.0), (2.0, -2.0), (-2.0, 2.0), (2.0, 2.0)]
    for sx, sz in stilt_offsets:
        bpy.ops.mesh.primitive_cylinder_add(radius=0.18, depth=6.5, vertices=8, location=(sx, 3.25, sz))
        stilt = bpy.context.active_object
        stilt.data.materials.append(mat_wood)
        parts.append(stilt)

    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0, 6.4, 0))
    deck = bpy.context.active_object
    deck.scale = (4.6, 0.25, 4.6)
    deck.data.materials.append(mat_wood)
    parts.append(deck)

    bpy.ops.mesh.primitive_cone_add(radius1=3.4, depth=1.6, vertices=4, location=(0, 8.8, 0))
    roof = bpy.context.active_object
    roof.rotation_euler = (0, math.pi / 4.0, 0)
    roof.data.materials.append(mat_thatch)
    parts.append(roof)

    root = parts[0]
    bpy.ops.object.select_all(action='DESELECT')
    for p in parts:
        p.select_set(True)
    bpy.context.view_layer.objects.active = root
    bpy.ops.object.join()
    root.name = "Watchtower_Machan"
    link_to_col(root, col, [also_col] if also_col else None)
    return root

# ---------------------------------------------------------------------------
# 7. Boundary Fence Post & Camera Tower
# ---------------------------------------------------------------------------
def build_boundary_post(col, also_col=None):
    mat_post = make_material("M_Fence_Post", (0.28, 0.28, 0.30, 1.0), roughness=0.7)
    mat_panel = make_material("M_Solar_Panel", (0.05, 0.08, 0.18, 1.0), roughness=0.3, metalness=0.8)
    mat_box = make_material("M_Sensor_Box", (0.68, 0.70, 0.72, 1.0), roughness=0.5)

    bpy.ops.mesh.primitive_cylinder_add(radius=0.12, depth=3.2, vertices=10, location=(0, 1.6, 0))
    post = bpy.context.active_object
    post.data.materials.append(mat_post)

    parts = []
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0, 2.8, 0.22))
    panel = bpy.context.active_object
    panel.scale = (0.55, 0.04, 0.40)
    panel.rotation_euler = (0.5, 0, 0)
    panel.data.materials.append(mat_panel)
    parts.append(panel)

    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0, 2.0, 0.18))
    box = bpy.context.active_object
    box.scale = (0.35, 0.45, 0.25)
    box.data.materials.append(mat_box)
    parts.append(box)

    bpy.ops.object.select_all(action='DESELECT')
    for p in parts:
        p.select_set(True)
    post.select_set(True)
    bpy.context.view_layer.objects.active = post
    bpy.ops.object.join()
    post.name = "Boundary_Sensor_Post"
    link_to_col(post, col, [also_col] if also_col else None)
    return post

def build_camera_tower(col, also_col=None):
    mat_steel = make_material("M_Camera_Mast", (0.32, 0.34, 0.36, 1.0), roughness=0.5, metalness=0.85)
    mat_cam = make_material("M_ESP32_Cam", (0.85, 0.88, 0.90, 1.0), roughness=0.4)
    mat_lens = make_material("M_Cam_Lens", (0.02, 0.02, 0.03, 1.0), roughness=0.1, metalness=0.95)

    bpy.ops.mesh.primitive_cylinder_add(radius=0.22, depth=6.2, vertices=12, location=(0, 3.1, 0))
    mast = bpy.context.active_object
    mast.data.materials.append(mat_steel)

    parts = []
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0, 5.4, 0.45))
    cam = bpy.context.active_object
    cam.scale = (0.42, 0.35, 0.65)
    cam.data.materials.append(mat_cam)
    parts.append(cam)

    bpy.ops.mesh.primitive_cylinder_add(radius=0.10, depth=0.18, vertices=12, location=(0, 5.4, 0.68))
    lens = bpy.context.active_object
    lens.rotation_euler = (math.pi / 2.0, 0, 0)
    lens.data.materials.append(mat_lens)
    parts.append(lens)

    bpy.ops.object.select_all(action='DESELECT')
    for p in parts:
        p.select_set(True)
    mast.select_set(True)
    bpy.context.view_layer.objects.active = mast
    bpy.ops.object.join()
    mast.name = "Camera_Mast_ESP32"
    link_to_col(mast, col, [also_col] if also_col else None)
    return mast

# ---------------------------------------------------------------------------
# 8. Animal Species (Import & Link All 6 Production Animals into 6 Dedicated Collections)
# ---------------------------------------------------------------------------
def import_and_organize_animals(cols):
    species_map = {
        "ANIMALS_ASIAN_ELEPHANT": ("asian_elephant_production.glb", "Elephant_Production_Asset", "SPECIES_ELEPHANT"),
        "ANIMALS_CHITAL": ("chital_deer.glb", "Chital_Deer_Production_Asset", "SPECIES_DEER"),
        "ANIMALS_SAMBAR": ("sambar_deer.glb", "Sambar_Deer_Production_Asset", "SPECIES_DEER"),
        "ANIMALS_WILD_BOAR": ("wild_boar.glb", "Wild_Boar_Production_Asset", "SPECIES_WILD_BOAR"),
        "ANIMALS_GAUR": ("gaur_bison.glb", "Gaur_Bison_Production_Asset", "SPECIES_GAUR"),
        "ANIMALS_MONKEY": ("bonnet_macaque.glb", "Bonnet_Macaque_Production_Asset", "SPECIES_MONKEY"),
    }

    imported_species = {}
    for col_name, (fname, asset_name, leg_col) in species_map.items():
        col = cols[col_name]
        src_path = os.path.join(STATIC_ASSETS_DIR, "animals", fname)
        if os.path.exists(src_path):
            before_objs = set(bpy.data.objects)
            bpy.ops.import_scene.gltf(filepath=src_path)
            new_objs = list(set(bpy.data.objects) - before_objs)
            leg = cols.get(leg_col)
            for o in new_objs:
                link_to_col(o, col, [leg] if leg else None)
            print(f"Imported {fname} ({len(new_objs)} objects) into {col_name}")
            imported_species[asset_name] = new_objs

    return imported_species

# ---------------------------------------------------------------------------
# 9. Hardware & Sensor Models for SENSING_INFRASTRUCTURE
# ---------------------------------------------------------------------------
def import_sensing_infrastructure(col, leg_col=None):
    hw_files = [
        "esp32_s3_devkitc1_v1_1.glb",
        "sw420_vibration.glb",
        "hc_sr501_pir.glb",
        "inmp441_microphone.glb",
        "esp32_cam_ov2640.glb"
    ]
    for fname in hw_files:
        p = os.path.join(STATIC_ASSETS_DIR, "hardware", fname)
        if os.path.exists(p):
            before_objs = set(bpy.data.objects)
            bpy.ops.import_scene.gltf(filepath=p)
            new_objs = list(set(bpy.data.objects) - before_objs)
            for o in new_objs:
                link_to_col(o, col, [leg_col] if leg_col else None)
            print(f"Imported sensor {fname} into SENSING_INFRASTRUCTURE")

# ---------------------------------------------------------------------------
# 10. Dedicated GLB Exporter
# ---------------------------------------------------------------------------
def export_asset_glb(objs, rel_out_path):
    out_assets = os.path.join(ASSETS_DIR, rel_out_path)
    out_static = os.path.join(STATIC_ASSETS_DIR, rel_out_path)
    os.makedirs(os.path.dirname(out_assets), exist_ok=True)
    os.makedirs(os.path.dirname(out_static), exist_ok=True)

    bpy.ops.object.select_all(action='DESELECT')
    for o in objs:
        if o:
            o.select_set(True)
            bpy.context.view_layer.objects.active = o

    bpy.ops.export_scene.gltf(
        filepath=out_assets,
        export_format='GLB',
        use_selection=True,
        export_apply=True,
        export_animations=True,
        export_skins=True,
        export_morph=True
    )
    shutil.copy2(out_assets, out_static)
    print(f"Exported: {rel_out_path} ({os.path.getsize(out_assets)} bytes)")

def sync_all_assets_to_root_assets():
    # Ensure assets/animals has all animal files from static
    for fname in ["asian_elephant_production.glb", "chital_deer.glb", "sambar_deer.glb", "wild_boar.glb", "gaur_bison.glb", "bonnet_macaque.glb"]:
        src = os.path.join(STATIC_ASSETS_DIR, "animals", fname)
        if os.path.exists(src):
            dst = os.path.join(ASSETS_DIR, "animals", fname)
            shutil.copy2(src, dst)
            # also copy to specific subdirs
            submap = {
                "asian_elephant_production.glb": "elephant",
                "chital_deer.glb": "deer",
                "sambar_deer.glb": "deer",
                "wild_boar.glb": "boar",
                "gaur_bison.glb": "gaur",
                "bonnet_macaque.glb": "monkey"
            }
            if fname in submap:
                s_dst = os.path.join(ASSETS_DIR, "animals", submap[fname], fname)
                shutil.copy2(src, s_dst)
    # Ensure hardware files copied to assets/hardware
    hw_dir = os.path.join(STATIC_ASSETS_DIR, "hardware")
    if os.path.exists(hw_dir):
        for f in os.listdir(hw_dir):
            if f.endswith(".glb"):
                shutil.copy2(os.path.join(hw_dir, f), os.path.join(ASSETS_DIR, "hardware", f))

def main():
    print("=== Starting PRW-Wild 16-Collection Blender World Master Generation ===")
    ensure_dirs()
    reset_scene()
    cols = setup_collections()

    # 1. Sculpted Natural Terrain
    terrain_obj = build_sculpted_terrain(cols["WORLD_TERRAIN"], cols["ENV_TERRAIN"])
    export_asset_glb([terrain_obj], "environment/terrain/terrain_world.glb")

    # 2. Forest Trees
    sal_tree = build_sal_tree(cols["WORLD_FOREST"], cols["ENV_FOREST"])
    export_asset_glb([sal_tree], "environment/trees/sal_mature.glb")

    banyan_tree = build_banyan_tree(cols["WORLD_FOREST"], cols["ENV_FOREST"])
    export_asset_glb([banyan_tree], "environment/trees/banyan_fig.glb")

    acacia_tree = build_acacia_tree(cols["WORLD_FOREST"], cols["ENV_FOREST"])
    export_asset_glb([acacia_tree], "environment/trees/acacia_canopy.glb")

    # 3. Resources (Fruit Trees)
    mango_tree = build_mango_fruit_tree(cols["WORLD_RESOURCES"], cols["ENV_FRUIT_TREES"])
    export_asset_glb([mango_tree], "environment/fruit_trees/mango_fruit_tree.glb")

    # 4. Vegetation & Ground Cover
    ferns = build_forest_ferns(cols["WORLD_VEGETATION"], cols["ENV_VEGETATION"])
    export_asset_glb([ferns], "environment/vegetation/forest_ferns.glb")

    shrub = build_forest_shrub(cols["WORLD_VEGETATION"], cols["ENV_VEGETATION"])
    export_asset_glb([shrub], "environment/vegetation/forest_shrub.glb")

    grass = build_tall_grass(cols["WORLD_GROUND_COVER"], cols["ENV_GRASS"])
    export_asset_glb([grass], "environment/grass/tall_grass_clump.glb")

    # 5. Water Features
    pond = build_pond_basin(cols["WORLD_WATER"], cols["ENV_WATER"])
    export_asset_glb([pond], "environment/water/pond_basin.glb")

    # 6. Farmland
    crops = build_crop_field(cols["WORLD_FARMLAND"], cols["ENV_FARMLAND"])
    export_asset_glb([crops], "environment/farmland/crop_field.glb")

    machan = build_watchtower_machan(cols["WORLD_FARMLAND"], cols["ENV_FARMLAND"])
    export_asset_glb([machan], "environment/farmland/watchtower_machan.glb")

    # 7. Boundary
    fence_post = build_boundary_post(cols["WORLD_BOUNDARY"], cols["ENV_BOUNDARY"])
    export_asset_glb([fence_post], "environment/boundary/boundary_fence_sensor.glb")

    # 8. Surveillance Cameras
    cam_mast = build_camera_tower(cols["SURVEILLANCE_CAMERAS"], cols["CAMERA_ASSETS"])
    export_asset_glb([cam_mast], "cameras/camera_tower.glb")

    # 9. Hardware & Sensor Models for SENSING_INFRASTRUCTURE
    import_sensing_infrastructure(cols["SENSING_INFRASTRUCTURE"], cols["SENSOR_ASSETS"])

    # 10. Animal Species (6 Dedicated Collections: ANIMALS_ASIAN_ELEPHANT, ANIMALS_CHITAL, etc.)
    import_and_organize_animals(cols)

    # 11. Sync and verify all assets in assets/ hierarchy
    sync_all_assets_to_root_assets()

    # 12. Save PRW_WILD_WORLD_MASTER.blend
    bpy.ops.wm.save_as_mainfile(filepath=MASTER_BLEND_PATH)
    print(f"Master 16-Collection scene saved to: {MASTER_BLEND_PATH} ({os.path.getsize(MASTER_BLEND_PATH)} bytes)")

    # 13. Also update PRW_WILD_PRODUCTION_WORLD.blend for backward compatibility
    shutil.copy2(MASTER_BLEND_PATH, PROD_BLEND_PATH)
    print(f"Production scene mirrored to: {PROD_BLEND_PATH}")

    print("=== Master Blender World Production Run Complete ===")

if __name__ == "__main__":
    main()
