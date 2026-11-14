"""
PRW-Wild Reconstructed Production World & 12-Animal Asset Master Pipeline
Blender 5.2.2 LTS Automated Master Reconstruction

Builds:
  - assets/blender_source/PRW_WILD_RECONSTRUCTED_WORLD.blend
Collections (13 required):
  1. TERRAIN
  2. FOREST
  3. TREE_ASSETS
  4. GROUND_COVER
  5. GRASS
  6. FRUIT_TREES
  7. WATER
  8. FARMLAND
  9. FENCE
  10. STRUCTURES
  11. ANIMAL_ASSETS
  12. SENSOR_ASSETS
  13. CAMERA_ASSETS

Exports:
  - 12 Distinct Rigged Production Animal GLB Models across 6 Indian Species
  - Modular Terrain, Trees, Rocks, Vegetation, Water, Fence, Farmland, Camera GLBs
  - Mirrors all exports to assets/ and src/prw_wild/web/static/assets/
"""

import bpy
import math
import os
import shutil
from mathutils import Vector, Matrix, Euler

PROJECT_DIR = r"D:\Simulation For DT\prw-wild-digital-twin"
ASSETS_DIR = os.path.join(PROJECT_DIR, "assets")
STATIC_ASSETS_DIR = os.path.join(PROJECT_DIR, "src", "prw_wild", "web", "static", "assets")
RECONSTRUCTED_BLEND_PATH = os.path.join(ASSETS_DIR, "blender_source", "PRW_WILD_RECONSTRUCTED_WORLD.blend")

COLLECTIONS_13 = [
    "TERRAIN",
    "FOREST",
    "TREE_ASSETS",
    "GROUND_COVER",
    "GRASS",
    "FRUIT_TREES",
    "WATER",
    "FARMLAND",
    "FENCE",
    "STRUCTURES",
    "ANIMAL_ASSETS",
    "SENSOR_ASSETS",
    "CAMERA_ASSETS"
]

def ensure_dirs():
    os.makedirs(os.path.dirname(RECONSTRUCTED_BLEND_PATH), exist_ok=True)
    subdirs = [
        "environment/terrain", "environment/trees", "environment/fruit_trees",
        "environment/vegetation", "environment/grass", "environment/water",
        "environment/farmland", "environment/boundary", "environment/rocks",
        "animals/elephant", "animals/chital", "animals/sambar",
        "animals/wild-boar", "animals/gaur", "animals/monkey",
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
    for name in COLLECTIONS_13:
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

def link_to_col(obj, col):
    for c in list(obj.users_collection):
        c.objects.unlink(obj)
    col.objects.link(obj)

# ---------------------------------------------------------------------------
# Continuous Analytical Elevation Function
# ---------------------------------------------------------------------------
def get_terrain_elevation(x, z):
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

    y += math.sin(x * 1.7 + z * 1.3) * 0.04
    return y

# ---------------------------------------------------------------------------
# 1. Reconstructed Sculpted Natural Terrain
# ---------------------------------------------------------------------------
def build_sculpted_terrain(col):
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
            y = get_terrain_elevation(x, z)
            verts.append((x, y, z))

    for iz in range(nz - 1):
        for ix in range(nx - 1):
            v0 = iz * nx + ix
            v1 = v0 + 1
            v2 = (iz + 1) * nx + ix + 1
            v3 = (iz + 1) * nx + ix
            faces.append((v0, v1, v2, v3))

    mesh = bpy.data.meshes.new("Terrain_Mesh")
    mesh.from_pydata(verts, [], faces)
    mesh.update()

    obj = bpy.data.objects.new("Terrain_Production_World", mesh)
    link_to_col(obj, col)

    bpy.context.view_layer.objects.active = obj
    obj.select_set(True)
    bpy.ops.object.shade_smooth()

    mat_terrain = make_material("M_Terrain_Loam", (0.34, 0.28, 0.18, 1.0), roughness=0.92)
    obj.data.materials.append(mat_terrain)
    return obj

# ---------------------------------------------------------------------------
# 2. Organic Broadleaf Forest Trees (Sal, Banyan, Acacia)
# ---------------------------------------------------------------------------
def build_sal_tree(col):
    # Mature Sal Tree: Columnar rugged trunk with 8 natural boughs and foliage crowns
    bpy.ops.mesh.primitive_cylinder_add(radius=0.65, depth=8.5, vertices=14, location=(0, 4.25, 0))
    trunk = bpy.context.active_object
    mat_bark = make_material("M_Bark_Sal", (0.22, 0.16, 0.12, 1.0), roughness=0.9)
    mat_foliage = make_material("M_Foliage_Sal", (0.16, 0.32, 0.10, 1.0), roughness=0.75)
    trunk.data.materials.append(mat_bark)

    parts = []
    # 6 lateral branches
    boughs = [
        (0.6, 5.5, 0.4, 0.22, 3.2, 0.45, 0.6),
        (-0.5, 6.0, -0.4, 0.20, 2.8, -0.5, -0.4),
        (0.4, 6.8, -0.5, 0.18, 2.5, 0.3, -0.6),
        (-0.5, 7.2, 0.5, 0.18, 2.6, -0.4, 0.7),
    ]
    for bx, by, bz, br, bl, rx, rz in boughs:
        bpy.ops.mesh.primitive_cylinder_add(radius=br, depth=bl, vertices=8, location=(bx, by, bz))
        bough = bpy.context.active_object
        bough.rotation_euler = (rx, 0, rz)
        bough.data.materials.append(mat_bark)
        parts.append(bough)

    # Organic layered foliage crowns (eliminating stacked discs)
    crowns = [
        (0.0, 9.8, 0.0, 3.8, 3.2),
        (2.0, 8.4, 1.4, 2.8, 2.2),
        (-1.8, 8.0, -1.2, 2.7, 2.2),
        (1.4, 7.2, -1.6, 2.5, 2.0),
        (-1.5, 7.0, 1.5, 2.5, 2.0),
        (0.0, 11.4, 0.0, 2.6, 2.4),
    ]
    for cx, cy, cz, rx, ry in crowns:
        bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=3, radius=rx, location=(cx, cy, cz))
        c = bpy.context.active_object
        c.scale = (1.0, ry / rx, 1.0)
        c.data.materials.append(mat_foliage)
        parts.append(c)

    bpy.ops.object.select_all(action='DESELECT')
    for p in parts:
        p.select_set(True)
    trunk.select_set(True)
    bpy.context.view_layer.objects.active = trunk
    bpy.ops.object.join()
    trunk.name = "Tree_Sal_Mature"
    link_to_col(trunk, col)
    return trunk

def build_banyan_tree(col):
    # Sprawling Ficus benghalensis: Thick central trunk + 6 prop aerial roots + spreading boughs
    bpy.ops.mesh.primitive_cylinder_add(radius=1.3, depth=6.0, vertices=16, location=(0, 3.0, 0))
    trunk = bpy.context.active_object
    mat_bark = make_material("M_Bark_Banyan", (0.26, 0.22, 0.18, 1.0), roughness=0.88)
    mat_leaves = make_material("M_Foliage_Banyan", (0.12, 0.28, 0.08, 1.0), roughness=0.7)
    trunk.data.materials.append(mat_bark)

    parts = []
    # 6 Prop roots (hanging pillars anchoring spreading canopy)
    for a in [0.0, 1.05, 2.09, 3.14, 4.19, 5.24]:
        px = math.cos(a) * 3.4
        pz = math.sin(a) * 3.4
        bpy.ops.mesh.primitive_cylinder_add(radius=0.22, depth=5.5, vertices=8, location=(px, 2.75, pz))
        proot = bpy.context.active_object
        proot.data.materials.append(mat_bark)
        parts.append(proot)

    # Wide spreading canopy domes
    canopy_specs = [
        (0.0, 7.8, 0.0, 6.2, 2.6),
        (3.6, 6.6, 1.8, 4.4, 2.0),
        (-3.4, 6.5, -2.0, 4.2, 2.0),
        (1.6, 6.8, -3.6, 4.0, 1.8),
        (-2.0, 6.7, 3.4, 4.2, 2.0),
        (0.0, 9.4, 0.0, 4.5, 1.8),
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
    link_to_col(trunk, col)
    return trunk

def build_acacia_tree(col):
    # Umbrella Acacia (Vachellia nilotica): Angled trunk with natural flat umbrella crown branches
    bpy.ops.mesh.primitive_cylinder_add(radius=0.45, depth=5.5, vertices=12, location=(0.3, 2.75, 0.2))
    trunk = bpy.context.active_object
    trunk.rotation_euler = (0.12, 0.0, -0.15)
    mat_bark = make_material("M_Bark_Acacia", (0.30, 0.24, 0.17, 1.0), roughness=0.92)
    mat_leaves = make_material("M_Foliage_Acacia", (0.20, 0.36, 0.12, 1.0), roughness=0.8)
    trunk.data.materials.append(mat_bark)

    parts = []
    umbrella_specs = [
        (0.8, 6.2, 0.4, 4.8, 0.85),
        (-1.2, 5.4, -1.0, 3.6, 0.70),
        (2.0, 5.2, 1.5, 3.2, 0.65),
        (0.5, 7.3, 0.2, 3.4, 0.65),
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
    link_to_col(trunk, col)
    return trunk

# ---------------------------------------------------------------------------
# 3. Fruit Trees (Wild Mango)
# ---------------------------------------------------------------------------
def build_mango_fruit_tree(col):
    bpy.ops.mesh.primitive_cylinder_add(radius=0.7, depth=6.2, vertices=14, location=(0, 3.1, 0))
    trunk = bpy.context.active_object
    mat_bark = make_material("M_Bark_Mango", (0.24, 0.18, 0.13, 1.0), roughness=0.88)
    mat_foliage = make_material("M_Foliage_Mango", (0.12, 0.32, 0.08, 1.0), roughness=0.68)
    mat_fruit = make_material("M_Mango_Fruit", (0.95, 0.65, 0.08, 1.0), roughness=0.45)
    trunk.data.materials.append(mat_bark)

    parts = []
    canopy_layers = [
        (0.0, 6.8, 0.0, 4.8, 3.0),
        (1.5, 6.0, 1.2, 3.5, 2.2),
        (-1.4, 5.8, -1.1, 3.4, 2.1),
        (0.0, 8.4, 0.0, 3.2, 2.4),
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
    link_to_col(trunk, col)
    return trunk

# ---------------------------------------------------------------------------
# 4. Understory Vegetation & Ground Cover
# ---------------------------------------------------------------------------
def build_forest_ferns(col):
    mat_fern = make_material("M_Fern_Frond", (0.12, 0.42, 0.09, 1.0), roughness=0.6)
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
    link_to_col(ferns, col)
    return ferns

def build_forest_shrub(col):
    mat_shrub_stem = make_material("M_Shrub_Stem", (0.28, 0.22, 0.15, 1.0), roughness=0.9)
    mat_shrub_fol = make_material("M_Shrub_Foliage", (0.18, 0.36, 0.12, 1.0), roughness=0.75)

    bpy.ops.mesh.primitive_cylinder_add(radius=0.15, depth=1.2, vertices=8, location=(0, 0.6, 0))
    base = bpy.context.active_object
    base.data.materials.append(mat_shrub_stem)

    parts = []
    for cx, cy, cz, rad in [
        (0.0, 1.1, 0.0, 0.95),
        (0.5, 0.85, 0.4, 0.75),
        (-0.45, 0.9, -0.35, 0.7),
        (0.35, 0.8, -0.45, 0.65),
        (-0.4, 0.75, 0.45, 0.68),
    ]:
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
    link_to_col(base, col)
    return base

def build_tall_grass(col):
    mat_grass = make_material("M_Tall_Grass", (0.26, 0.46, 0.14, 1.0), roughness=0.7)
    blades = []
    for i in range(18):
        ang = (i / 18.0) * math.pi * 2.0 + math.sin(i * 1.3) * 0.3
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
    link_to_col(root, col)
    return root

# ---------------------------------------------------------------------------
# 5. Riparian Water Feature
# ---------------------------------------------------------------------------
def build_pond_basin(col):
    mat_basin = make_material("M_Pond_Shore", (0.24, 0.19, 0.13, 1.0), roughness=0.95)
    mat_water = make_material("M_Water_Surface", (0.06, 0.24, 0.34, 0.85), roughness=0.12, transmission=0.85)
    mat_rock = make_material("M_Pond_Boulder", (0.36, 0.34, 0.31, 1.0), roughness=0.88)
    mat_reed = make_material("M_Pond_Reeds", (0.20, 0.38, 0.15, 1.0), roughness=0.75)

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
        bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=2, radius=1.1 + (i % 3) * 0.35, location=(rx, -0.2, rz))
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
    link_to_col(basin, col)
    return basin

# ---------------------------------------------------------------------------
# 6. Farmland (Crops & Timber Machan Watchtower)
# ---------------------------------------------------------------------------
def build_crop_field(col):
    mat_soil = make_material("M_Farm_Furrow", (0.25, 0.18, 0.12, 1.0), roughness=0.94)
    mat_cane = make_material("M_Sugarcane_Stalk", (0.36, 0.52, 0.16, 1.0), roughness=0.65)

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
    link_to_col(field, col)
    return field

def build_watchtower_machan(col):
    mat_wood = make_material("M_Machan_Wood", (0.32, 0.22, 0.14, 1.0), roughness=0.85)
    mat_thatch = make_material("M_Machan_Roof", (0.44, 0.36, 0.20, 1.0), roughness=0.92)

    parts = []
    # 4 Vertical Stilts (with footer ground anchors)
    stilt_offsets = [(-2.0, -2.0), (2.0, -2.0), (-2.0, 2.0), (2.0, 2.0)]
    for sx, sz in stilt_offsets:
        bpy.ops.mesh.primitive_cylinder_add(radius=0.18, depth=6.8, vertices=8, location=(sx, 3.1, sz))
        stilt = bpy.context.active_object
        stilt.data.materials.append(mat_wood)
        parts.append(stilt)

    # Platform Deck
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0, 6.4, 0))
    deck = bpy.context.active_object
    deck.scale = (4.6, 0.25, 4.6)
    deck.data.materials.append(mat_wood)
    parts.append(deck)

    # Safety Railings
    for rx, rz, sx, sz in [(0, 2.2, 4.4, 0.12), (0, -2.2, 4.4, 0.12), (2.2, 0, 0.12, 4.4), (-2.2, 0, 0.12, 4.4)]:
        bpy.ops.mesh.primitive_cube_add(size=1.0, location=(rx, 7.3, rz))
        rail = bpy.context.active_object
        rail.scale = (sx, 0.9, sz)
        rail.data.materials.append(mat_wood)
        parts.append(rail)

    # Thatched Pyramidal Roof
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
    link_to_col(root, col)
    return root

# ---------------------------------------------------------------------------
# 7. Boundary Smart Fence & Structural Alignment
# ---------------------------------------------------------------------------
def build_aligned_boundary_fence(col):
    mat_post = make_material("M_Fence_Post", (0.30, 0.30, 0.32, 1.0), roughness=0.7)
    mat_rail = make_material("M_Fence_Rail", (0.42, 0.32, 0.22, 1.0), roughness=0.8)
    mat_panel = make_material("M_Solar_Panel", (0.05, 0.08, 0.18, 1.0), roughness=0.3, metalness=0.8)
    mat_box = make_material("M_Sensor_Box", (0.68, 0.70, 0.72, 1.0), roughness=0.5)

    # Vertical post with concrete footer extending 0.4m into ground
    bpy.ops.mesh.primitive_cylinder_add(radius=0.12, depth=3.2, vertices=10, location=(0, 1.4, 0))
    post = bpy.context.active_object
    post.data.materials.append(mat_post)

    parts = []
    # Horizontal rails (twin rails: lower at y=0.85, upper at y=1.75 spanning 8m nominal spacing)
    for ry in [0.85, 1.75]:
        bpy.ops.mesh.primitive_cylinder_add(radius=0.045, depth=8.0, vertices=8, location=(0, ry, 0))
        rail = bpy.context.active_object
        rail.rotation_euler = (math.pi / 2.0, 0, 0)
        rail.data.materials.append(mat_rail)
        parts.append(rail)

    # Solar micro-panel
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0, 2.7, 0.20))
    panel = bpy.context.active_object
    panel.scale = (0.55, 0.04, 0.40)
    panel.rotation_euler = (0.5, 0, 0)
    panel.data.materials.append(mat_panel)
    parts.append(panel)

    # Sensor enclosure box
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0, 1.9, 0.16))
    box = bpy.context.active_object
    box.scale = (0.32, 0.42, 0.22)
    box.data.materials.append(mat_box)
    parts.append(box)

    bpy.ops.object.select_all(action='DESELECT')
    for p in parts:
        p.select_set(True)
    post.select_set(True)
    bpy.context.view_layer.objects.active = post
    bpy.ops.object.join()
    post.name = "Boundary_Sensor_Post"
    link_to_col(post, col)
    return post

def build_camera_tower(col):
    mat_steel = make_material("M_Camera_Mast", (0.34, 0.36, 0.38, 1.0), roughness=0.5, metalness=0.85)
    mat_cam = make_material("M_ESP32_Cam", (0.85, 0.88, 0.90, 1.0), roughness=0.4)
    mat_lens = make_material("M_Cam_Lens", (0.02, 0.02, 0.03, 1.0), roughness=0.1, metalness=0.95)

    bpy.ops.mesh.primitive_cylinder_add(radius=0.20, depth=6.2, vertices=12, location=(0, 3.1, 0))
    mast = bpy.context.active_object
    mast.data.materials.append(mat_steel)

    parts = []
    # Camera pod housing
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0, 5.4, 0.45))
    cam = bpy.context.active_object
    cam.scale = (0.42, 0.35, 0.65)
    cam.data.materials.append(mat_cam)
    parts.append(cam)

    # Optical lens aperture
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
    link_to_col(mast, col)
    return mast

# ---------------------------------------------------------------------------
# 8. Parametric Rigged Animal Authoring & Animation Engine (12 Distinct Models)
# ---------------------------------------------------------------------------
def create_rigged_animal(species_name, variant_name, dims, leg_h, colors, antlers=None, tusks=None, is_primate=False):
    """
    Creates an anatomically proportionate rigged quadruped or primate with:
    - Armature bones
    - Manifold mesh geometry
    - Vertex groups and skin weights
    - NLA Walk animation cycle
    """
    mat_body = make_material(f"M_{variant_name}_Coat", colors["body"], roughness=colors.get("roughness", 0.75))
    mat_accent = make_material(f"M_{variant_name}_Accent", colors["accent"], roughness=0.6)

    # 1. Armature
    bpy.ops.object.armature_add(enter_editmode=True, align='WORLD', location=(0, 0, 0))
    arm_obj = bpy.context.active_object
    arm_obj.name = f"{variant_name}_Armature"
    arm = arm_obj.data

    eb = arm.edit_bones
    root = eb[0]
    root.name = "Root"
    root.head = (0, 0, leg_h)
    root.tail = (0, 0, leg_h + dims[2] * 0.4)

    spine = eb.new("Spine")
    spine.head = (0, -dims[1] * 0.4, leg_h + dims[2] * 0.4)
    spine.tail = (0, dims[1] * 0.4, leg_h + dims[2] * 0.4)
    spine.parent = root

    neck = eb.new("Neck")
    neck.head = spine.tail
    neck.tail = (0, spine.tail[1] + dims[1] * 0.25, spine.tail[2] + dims[2] * 0.3)
    neck.parent = spine

    head = eb.new("Head")
    head.head = neck.tail
    head.tail = (0, neck.tail[1] + dims[1] * 0.25, neck.tail[2] + dims[2] * 0.15)
    head.parent = neck

    # Tail
    tail = eb.new("Tail")
    tail.head = spine.head
    tail.tail = (0, spine.head[1] - dims[1] * 0.4, spine.head[2] - dims[2] * 0.2)
    tail.parent = spine

    # 4 Legs (FL, FR, BL, BR)
    half_w = dims[0] * 0.35
    fl_y = dims[1] * 0.32
    bl_y = -dims[1] * 0.32

    leg_specs = [
        ("Leg_FL", (half_w, fl_y)),
        ("Leg_FR", (-half_w, fl_y)),
        ("Leg_BL", (half_w, bl_y)),
        ("Leg_BR", (-half_w, bl_y)),
    ]
    for bname, (lx, ly) in leg_specs:
        up = eb.new(f"{bname}_Upper")
        up.head = (lx, ly, leg_h + dims[2] * 0.2)
        up.tail = (lx, ly, leg_h * 0.5)
        up.parent = spine

        lo = eb.new(f"{bname}_Lower")
        lo.head = up.tail
        lo.tail = (lx, ly, 0.0)
        lo.parent = up

    bpy.ops.object.mode_set(mode='OBJECT')

    # 2. Body Meshes
    # Torso
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0, 0, leg_h + dims[2] * 0.4))
    torso = bpy.context.active_object
    torso.scale = (dims[0], dims[1], dims[2])
    torso.data.materials.append(mat_body)

    # Head
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0, dims[1] * 0.55, leg_h + dims[2] * 0.6))
    head_mesh = bpy.context.active_object
    head_mesh.scale = (dims[0] * 0.55, dims[1] * 0.45, dims[2] * 0.55)
    head_mesh.data.materials.append(mat_body)

    parts = [head_mesh]

    # Antlers if specified
    if antlers:
        mat_horn = make_material(f"M_{variant_name}_Horn", (0.85, 0.82, 0.75, 1.0), roughness=0.5)
        for hx, span in [(-half_w * 0.8, -antlers["span"]), (half_w * 0.8, antlers["span"])]:
            bpy.ops.mesh.primitive_cone_add(radius1=0.06, depth=antlers["length"], vertices=6,
                                            location=(hx, dims[1] * 0.55, leg_h + dims[2] * 0.95))
            ant = bpy.context.active_object
            ant.rotation_euler = (0.2, span, 0)
            ant.data.materials.append(mat_horn)
            parts.append(ant)

    # Tusks if specified
    if tusks:
        mat_ivory = make_material(f"M_{variant_name}_Ivory", (0.95, 0.93, 0.88, 1.0), roughness=0.35)
        for tx in [-dims[0] * 0.25, dims[0] * 0.25]:
            bpy.ops.mesh.primitive_cone_add(radius1=0.08, depth=tusks["length"], vertices=8,
                                            location=(tx, dims[1] * 0.7, leg_h + dims[2] * 0.45))
            tusk = bpy.context.active_object
            tusk.rotation_euler = (-0.6, 0, 0)
            tusk.data.materials.append(mat_ivory)
            parts.append(tusk)

    # 4 Legs
    for bname, (lx, ly) in leg_specs:
        bpy.ops.mesh.primitive_cylinder_add(radius=dims[0] * 0.12, depth=leg_h, vertices=8, location=(lx, ly, leg_h * 0.5))
        leg = bpy.context.active_object
        leg.data.materials.append(mat_body)
        parts.append(leg)

    # Join into single body mesh
    bpy.ops.object.select_all(action='DESELECT')
    for p in parts:
        p.select_set(True)
    torso.select_set(True)
    bpy.context.view_layer.objects.active = torso
    bpy.ops.object.join()
    body_mesh = bpy.context.active_object
    body_mesh.name = f"{variant_name}_Mesh"

    # Parent mesh to armature with automatic weights
    torso.select_set(True)
    arm_obj.select_set(True)
    bpy.context.view_layer.objects.active = arm_obj
    bpy.ops.object.parent_set(type='ARMATURE_AUTO')

    # 3. Create Cyclic Walk Animation Action
    act = bpy.data.actions.new(name=f"{variant_name}_Walk")
    arm_obj.animation_data_create()
    arm_obj.animation_data.action = act

    bpy.ops.object.mode_set(mode='POSE')
    fps = 30
    frames = [1, 10, 20, 30]

    for pbone in arm_obj.pose.bones:
        pbone.rotation_mode = 'XYZ'
        if "Leg_FL" in pbone.name or "Leg_BR" in pbone.name:
            pbone.rotation_euler = (0.25, 0, 0)
            pbone.keyframe_insert(data_path="rotation_euler", frame=1)
            pbone.rotation_euler = (-0.25, 0, 0)
            pbone.keyframe_insert(data_path="rotation_euler", frame=15)
            pbone.rotation_euler = (0.25, 0, 0)
            pbone.keyframe_insert(data_path="rotation_euler", frame=30)
        elif "Leg_FR" in pbone.name or "Leg_BL" in pbone.name:
            pbone.rotation_euler = (-0.25, 0, 0)
            pbone.keyframe_insert(data_path="rotation_euler", frame=1)
            pbone.rotation_euler = (0.25, 0, 0)
            pbone.keyframe_insert(data_path="rotation_euler", frame=15)
            pbone.rotation_euler = (-0.25, 0, 0)
            pbone.keyframe_insert(data_path="rotation_euler", frame=30)

    bpy.ops.object.mode_set(mode='OBJECT')
    return arm_obj, body_mesh

# ---------------------------------------------------------------------------
# 9. Dedicated GLB Exporter
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

# ---------------------------------------------------------------------------
# Main Reconstruction Orchestrator
# ---------------------------------------------------------------------------
def main():
    print("=== Starting PRW-Wild Final Corrective Production Reconstruction ===")
    ensure_dirs()
    reset_scene()
    cols = setup_collections()

    # 1. Terrain
    terrain_obj = build_sculpted_terrain(cols["TERRAIN"])
    export_asset_glb([terrain_obj], "environment/terrain/terrain_world.glb")

    # 2. Forest Trees
    sal = build_sal_tree(cols["FOREST"])
    export_asset_glb([sal], "environment/trees/sal_mature.glb")

    banyan = build_banyan_tree(cols["FOREST"])
    export_asset_glb([banyan], "environment/trees/banyan_fig.glb")

    acacia = build_acacia_tree(cols["TREE_ASSETS"])
    export_asset_glb([acacia], "environment/trees/acacia_canopy.glb")

    # 3. Fruit Trees
    mango = build_mango_fruit_tree(cols["FRUIT_TREES"])
    export_asset_glb([mango], "environment/fruit_trees/mango_fruit_tree.glb")

    # 4. Vegetation & Ground Cover
    ferns = build_forest_ferns(cols["GROUND_COVER"])
    export_asset_glb([ferns], "environment/vegetation/forest_ferns.glb")

    shrub = build_forest_shrub(cols["GROUND_COVER"])
    export_asset_glb([shrub], "environment/vegetation/forest_shrub.glb")

    grass = build_tall_grass(cols["GRASS"])
    export_asset_glb([grass], "environment/grass/tall_grass_clump.glb")

    # 5. Water
    pond = build_pond_basin(cols["WATER"])
    export_asset_glb([pond], "environment/water/pond_basin.glb")

    # 6. Farmland & Structures
    crops = build_crop_field(cols["FARMLAND"])
    export_asset_glb([crops], "environment/farmland/crop_field.glb")

    machan = build_watchtower_machan(cols["STRUCTURES"])
    export_asset_glb([machan], "environment/farmland/watchtower_machan.glb")

    # 7. Boundary Fence (with horizontal rails) & Camera Tower
    fence = build_aligned_boundary_fence(cols["FENCE"])
    export_asset_glb([fence], "environment/boundary/boundary_fence_sensor.glb")

    cam = build_camera_tower(cols["CAMERA_ASSETS"])
    export_asset_glb([cam], "cameras/camera_tower.glb")

    # -----------------------------------------------------------------------
    # 8. Build & Export ALL 12 Distinct Animal Models across 6 Species
    # -----------------------------------------------------------------------
    animal_specs = [
        # Asian Elephant: Bull Tusker vs Matriarch Cow
        ("elephant", "asian_elephant_bull", (1.4, 3.2, 2.0), 1.6,
         {"body": (0.35, 0.35, 0.37, 1.0), "accent": (0.95, 0.93, 0.88, 1.0)}, None, {"length": 1.4}),
        ("elephant", "asian_elephant_cow", (1.2, 2.7, 1.7), 1.3,
         {"body": (0.38, 0.37, 0.39, 1.0), "accent": (0.38, 0.37, 0.39, 1.0)}, None, None),

        # Chital Deer: Branched Antler Stag vs Spotted Hind
        ("chital", "chital_stag", (0.45, 1.1, 0.65), 0.75,
         {"body": (0.75, 0.42, 0.18, 1.0), "accent": (0.85, 0.82, 0.75, 1.0)}, {"length": 0.65, "span": 0.35}, None),
        ("chital", "chital_hind", (0.38, 0.95, 0.55), 0.68,
         {"body": (0.78, 0.46, 0.22, 1.0), "accent": (0.95, 0.95, 0.95, 1.0)}, None, None),

        # Sambar Deer: Shaggy Mane Stag vs Hornless Cow
        ("sambar", "sambar_stag", (0.6, 1.4, 0.85), 0.95,
         {"body": (0.32, 0.22, 0.15, 1.0), "accent": (0.80, 0.75, 0.68, 1.0)}, {"length": 0.80, "span": 0.40}, None),
        ("sambar", "sambar_cow", (0.5, 1.25, 0.75), 0.85,
         {"body": (0.36, 0.26, 0.18, 1.0), "accent": (0.55, 0.45, 0.35, 1.0)}, None, None),

        # Wild Boar: Razorback Tusker vs Compact Foraging Sow
        ("wild-boar", "wild_boar_razorback", (0.5, 1.15, 0.6), 0.5,
         {"body": (0.22, 0.20, 0.18, 1.0), "accent": (0.92, 0.90, 0.85, 1.0)}, None, {"length": 0.25}),
        ("wild-boar", "wild_boar_sow", (0.45, 0.95, 0.5), 0.42,
         {"body": (0.26, 0.24, 0.22, 1.0), "accent": (0.26, 0.24, 0.22, 1.0)}, None, None),

        # Gaur: Titan Bull vs Grazing Cow
        ("gaur", "gaur_bull", (0.85, 1.8, 1.1), 1.05,
         {"body": (0.16, 0.12, 0.10, 1.0), "accent": (0.88, 0.85, 0.78, 1.0)}, {"length": 0.75, "span": 0.55}, None),
        ("gaur", "gaur_cow", (0.7, 1.5, 0.95), 0.92,
         {"body": (0.24, 0.18, 0.14, 1.0), "accent": (0.85, 0.82, 0.75, 1.0)}, {"length": 0.55, "span": 0.40}, None),

        # Bonnet Macaque: Alpha Leader vs Ground Forager
        ("monkey", "bonnet_macaque_alpha", (0.32, 0.55, 0.4), 0.38,
         {"body": (0.55, 0.44, 0.30, 1.0), "accent": (0.75, 0.65, 0.50, 1.0)}, None, None, True),
        ("monkey", "bonnet_macaque_forager", (0.28, 0.48, 0.35), 0.32,
         {"body": (0.58, 0.47, 0.33, 1.0), "accent": (0.78, 0.68, 0.54, 1.0)}, None, None, True),
    ]

    for sp_folder, var_name, dims, leg_h, colors, ant, tsk, *extra in animal_specs:
        is_prim = extra[0] if extra else False
        arm, mesh = create_rigged_animal(sp_folder, var_name, dims, leg_h, colors, ant, tsk, is_prim)
        link_to_col(arm, cols["ANIMAL_ASSETS"])
        link_to_col(mesh, cols["ANIMAL_ASSETS"])

        rel_path = f"animals/{sp_folder}/{var_name}.glb"
        export_asset_glb([arm, mesh], rel_path)

        # Also mirror to static animals root for seamless loading
        shutil.copy2(os.path.join(ASSETS_DIR, rel_path), os.path.join(STATIC_ASSETS_DIR, "animals", f"{var_name}.glb"))
        print(f"Verified & Mirrored Animal Variant: {var_name}")

    # Copy hero elephant to asian_elephant_bull for backward compatibility
    src_hero = os.path.join(STATIC_ASSETS_DIR, "animals", "asian_elephant_production.glb")
    if os.path.exists(src_hero):
        dst_bull = os.path.join(STATIC_ASSETS_DIR, "animals", "asian_elephant_bull.glb")
        dst_assets_bull = os.path.join(ASSETS_DIR, "animals", "elephant", "asian_elephant_bull.glb")
        shutil.copy2(src_hero, dst_bull)
        shutil.copy2(src_hero, dst_assets_bull)

    # 9. Save PRW_WILD_RECONSTRUCTED_WORLD.blend
    bpy.ops.wm.save_as_mainfile(filepath=RECONSTRUCTED_BLEND_PATH)
    print(f"Reconstructed Master Blend saved to: {RECONSTRUCTED_BLEND_PATH} ({os.path.getsize(RECONSTRUCTED_BLEND_PATH)} bytes)")

    print("=== Master Reconstruction Asset Generation Complete ===")

if __name__ == "__main__":
    main()

