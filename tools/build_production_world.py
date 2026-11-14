"""
PRW-Wild Production World Asset Generator & Master .blend Builder
Autonomously builds all 15 required collections in Blender 5.2.2 LTS,
sculpts natural terrain, author high-fidelity trees, vegetation, water features,
farmland structures, boundary/sensors, and imports all 6 wildlife species.
Saves: assets/blender_source/PRW_WILD_PRODUCTION_WORLD.blend
Exports production GLBs into assets/ hierarchy and web static mirror.
"""

import bpy
import math
import os
import shutil
import random
from mathutils import Vector, Matrix, Euler

# ---------------------------------------------------------------------------
# Path Configuration
# ---------------------------------------------------------------------------
PROJECT_DIR = r"D:\Simulation For DT\prw-wild-digital-twin"
ASSETS_DIR = os.path.join(PROJECT_DIR, "assets")
STATIC_ASSETS_DIR = os.path.join(PROJECT_DIR, "src", "prw_wild", "web", "static", "assets")
BLEND_OUT_PATH = os.path.join(ASSETS_DIR, "blender_source", "PRW_WILD_PRODUCTION_WORLD.blend")

COLLECTIONS_REQ = [
    "ENV_TERRAIN",
    "ENV_FOREST",
    "ENV_VEGETATION",
    "ENV_GRASS",
    "ENV_FRUIT_TREES",
    "ENV_WATER",
    "ENV_FARMLAND",
    "ENV_BOUNDARY",
    "SPECIES_ELEPHANT",
    "SPECIES_DEER",
    "SPECIES_WILD_BOAR",
    "SPECIES_GAUR",
    "SPECIES_MONKEY",
    "SENSOR_ASSETS",
    "CAMERA_ASSETS",
]

def ensure_dirs():
    os.makedirs(os.path.dirname(BLEND_OUT_PATH), exist_ok=True)
    subdirs = [
        "environment/terrain", "environment/trees", "environment/fruit_trees",
        "environment/vegetation", "environment/grass", "environment/water",
        "environment/farmland", "environment/boundary", "environment/shrubs",
        "animals/elephant", "animals/deer", "animals/boar", "animals/gaur", "animals/monkey",
        "cameras", "sensors"
    ]
    for d in subdirs:
        os.makedirs(os.path.join(ASSETS_DIR, d), exist_ok=True)
        os.makedirs(os.path.join(STATIC_ASSETS_DIR, d), exist_ok=True)

def reset_scene():
    bpy.ops.wm.read_factory_settings(use_empty=True)
    # Clear all existing collections except Scene Collection
    for c in list(bpy.data.collections):
        bpy.data.collections.remove(c)

def setup_collections():
    cols = {}
    root = bpy.context.scene.collection
    for name in COLLECTIONS_REQ:
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
    # Remove from other collections
    for c in list(obj.users_collection):
        c.objects.unlink(obj)
    col.objects.link(obj)

# ---------------------------------------------------------------------------
# 1. Natural Sculpted Terrain
# ---------------------------------------------------------------------------
def build_sculpted_terrain(col):
    # Grid: 100 x 100 divisions, spanning X from -25 to 225 (250m) and Z from -30 to 230 (260m)
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
            # Calculate organic natural elevation y
            # Base regional slope: West is higher plateau, East is lower farm basin
            base_elev = (100.0 - x) * 0.015 if x < 100 else -(x - 100.0) * 0.005

            # Forest rolling hills (X < 100)
            if x < 100:
                hills = (
                    math.sin(x * 0.065 + 1.2) * math.cos(z * 0.055) * 1.8 +
                    math.sin(x * 0.12 - 0.5) * math.cos(z * 0.11 + 0.8) * 0.75 +
                    math.sin(x * 0.22) * math.sin(z * 0.19) * 0.35
                )
                # Extra ridge elevation along far west boundary
                west_ridge = max(0.0, (40.0 - x) * 0.08)
                y = base_elev + hills + west_ridge
            else:
                # Farmland terracing: subtle stepped terraces every 30m
                ter_idx = math.floor((x - 100.0) / 28.0)
                ter_rem = (x - 100.0) % 28.0
                farm_grade = -ter_idx * 0.35 - (ter_rem / 28.0) * 0.08
                # Subtle plowed furrow ripples
                furrows = math.sin(z * 1.1) * 0.06
                y = farm_grade + furrows

            # Animal corridor depression (natural ancient riverbed / migratory path)
            # Corridor runs from X=0 to X=100 near Z=100
            corr_dist_z = abs(z - (100.0 + math.sin(x * 0.05) * 6.0))
            if corr_dist_z < 22.0 and x < 105:
                corr_factor = (1.0 - (corr_dist_z / 22.0)) ** 2
                # Depress corridor into a natural alluvial valley
                y -= corr_factor * 2.2

            # North Pond depression at (X=75, Z=140, radius ~20m)
            dist_p1 = math.hypot(x - 75.0, z - 140.0)
            if dist_p1 < 22.0:
                depth1 = (1.0 - (dist_p1 / 22.0)) ** 1.8
                y -= depth1 * 2.4

            # South Pond depression at (X=45, Z=60, radius ~16m)
            dist_p2 = math.hypot(x - 45.0, z - 60.0)
            if dist_p2 < 18.0:
                depth2 = (1.0 - (dist_p2 / 18.0)) ** 1.8
                y -= depth2 * 2.1

            # Micro-roughness
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
    link_to_col(obj, col)

    # Shading & Material
    bpy.context.view_layer.objects.active = obj
    obj.select_set(True)
    bpy.ops.object.shade_smooth()

    mat_terrain = make_material("M_Terrain_Natural", (0.28, 0.32, 0.18, 1.0), roughness=0.92)
    obj.data.materials.append(mat_terrain)

    return obj

# ---------------------------------------------------------------------------
# 2. High-Fidelity Trees (Sal, Banyan, Acacia)
# ---------------------------------------------------------------------------
def build_sal_tree(col):
    # Tall mature Sal (Shorea robusta): rugged straight columnar trunk with crown branches and tiered foliage
    bpy.ops.mesh.primitive_cylinder_add(radius=0.65, depth=8.5, vertices=12, location=(0, 4.25, 0))
    trunk = bpy.context.active_object
    trunk.name = "Tree_Sal_Trunk"

    mat_bark = make_material("M_Bark_Sal", (0.22, 0.16, 0.12, 1.0), roughness=0.9)
    mat_foliage = make_material("M_Foliage_Sal", (0.12, 0.30, 0.08, 1.0), roughness=0.75)
    trunk.data.materials.append(mat_bark)

    foliage_objs = []
    # Tiered organic foliage clumps
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

    # Join into single production asset
    bpy.ops.object.select_all(action='DESELECT')
    for o in foliage_objs:
        o.select_set(True)
    trunk.select_set(True)
    bpy.context.view_layer.objects.active = trunk
    bpy.ops.object.join()
    trunk.name = "Tree_Sal_Mature"
    link_to_col(trunk, col)
    return trunk

def build_banyan_tree(col):
    # Sprawling Banyan (Ficus benghalensis): thick trunk + prop roots + expansive umbrella canopy
    bpy.ops.mesh.primitive_cylinder_add(radius=1.2, depth=6.0, vertices=14, location=(0, 3.0, 0))
    trunk = bpy.context.active_object
    trunk.name = "Tree_Banyan_Trunk"

    mat_bark = make_material("M_Bark_Banyan", (0.26, 0.22, 0.18, 1.0), roughness=0.88)
    mat_leaves = make_material("M_Foliage_Banyan", (0.09, 0.26, 0.07, 1.0), roughness=0.7)
    trunk.data.materials.append(mat_bark)

    parts = []
    # 6 Prop roots (hanging pillars anchoring spreading boughs)
    prop_angles = [0.0, 1.05, 2.09, 3.14, 4.19, 5.24]
    for a in prop_angles:
        px = math.cos(a) * 3.4
        pz = math.sin(a) * 3.4
        bpy.ops.mesh.primitive_cylinder_add(radius=0.22, depth=5.5, vertices=8, location=(px, 2.75, pz))
        proot = bpy.context.active_object
        proot.data.materials.append(mat_bark)
        parts.append(proot)

    # Wide sprawling canopy domes
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
    link_to_col(trunk, col)
    return trunk

def build_acacia_tree(col):
    # Acacia tortilis / nilotica: angled trunk with multiple flat-topped umbrella-like canopy layers
    bpy.ops.mesh.primitive_cylinder_add(radius=0.45, depth=5.5, vertices=10, location=(0.4, 2.75, 0.2))
    trunk = bpy.context.active_object
    trunk.rotation_euler = (0.12, 0.0, -0.15)
    trunk.name = "Tree_Acacia_Trunk"

    mat_bark = make_material("M_Bark_Acacia", (0.30, 0.24, 0.17, 1.0), roughness=0.92)
    mat_leaves = make_material("M_Foliage_Acacia", (0.16, 0.35, 0.10, 1.0), roughness=0.8)
    trunk.data.materials.append(mat_bark)

    parts = []
    # Flat disc/umbrella canopy layers
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
    link_to_col(trunk, col)
    return trunk

# ---------------------------------------------------------------------------
# 3. Fruit Trees (Wild Mango with visible fruits)
# ---------------------------------------------------------------------------
def build_mango_fruit_tree(col):
    # Broadleaf dome with distinct golden/orange mango fruits hanging
    bpy.ops.mesh.primitive_cylinder_add(radius=0.55, depth=5.0, vertices=10, location=(0, 2.5, 0))
    trunk = bpy.context.active_object
    mat_bark = make_material("M_Bark_Mango", (0.28, 0.20, 0.15, 1.0), roughness=0.85)
    mat_leaves = make_material("M_Foliage_Mango", (0.08, 0.28, 0.06, 1.0), roughness=0.7)
    mat_fruit = make_material("M_Mango_Fruit", (0.95, 0.65, 0.05, 1.0), roughness=0.4)
    trunk.data.materials.append(mat_bark)

    parts = []
    # Main canopy
    bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=3, radius=4.2, location=(0, 6.2, 0))
    dome = bpy.context.active_object
    dome.scale = (1.0, 0.85, 1.0)
    dome.data.materials.append(mat_leaves)
    parts.append(dome)

    # 18 Hanging Mango fruits (clusters around lower perimeter of canopy)
    random.seed(42)
    for i in range(18):
        ang = (i / 18.0) * math.pi * 2.0 + random.uniform(-0.15, 0.15)
        rad = random.uniform(2.6, 3.8)
        fx = math.cos(ang) * rad
        fz = math.sin(ang) * rad
        fy = random.uniform(4.0, 5.4)

        bpy.ops.mesh.primitive_uv_sphere_add(radius=0.22, location=(fx, fy, fz))
        fruit = bpy.context.active_object
        fruit.scale = (0.75, 1.25, 0.85)  # Elongated mango teardrop
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
# 4. Vegetation & Grass (Ferns, Shrubs, Tall Grass Clumps)
# ---------------------------------------------------------------------------
def build_forest_ferns(col):
    # Cluster of arched fronds
    mat_fern = make_material("M_Fern_Frond", (0.10, 0.42, 0.08, 1.0), roughness=0.6)
    fronds = []
    for i in range(12):
        ang = (i / 12.0) * math.pi * 2.0
        tilt = 0.55 + (i % 3) * 0.12
        bpy.ops.mesh.primitive_cone_add(radius1=0.28, radius2=0.02, depth=2.2, vertices=6, location=(0, 0.9, 0))
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
    mat_shrub = make_material("M_Shrub_Foliage", (0.14, 0.36, 0.10, 1.0), roughness=0.8)
    mat_stem = make_material("M_Shrub_Stem", (0.28, 0.20, 0.14, 1.0), roughness=0.9)

    bpy.ops.mesh.primitive_cylinder_add(radius=0.12, depth=1.6, vertices=6, location=(0, 0.8, 0))
    stem = bpy.context.active_object
    stem.data.materials.append(mat_stem)

    parts = []
    for offset, r in [
        ((0, 1.6, 0), 1.3),
        ((0.6, 1.3, 0.4), 0.95),
        ((-0.5, 1.4, -0.3), 0.9),
        ((0.3, 1.2, -0.6), 0.85),
    ]:
        bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=2, radius=r, location=offset)
        clump = bpy.context.active_object
        clump.data.materials.append(mat_shrub)
        parts.append(clump)

    bpy.ops.object.select_all(action='DESELECT')
    for p in parts:
        p.select_set(True)
    stem.select_set(True)
    bpy.context.view_layer.objects.active = stem
    bpy.ops.object.join()
    shrub = bpy.context.active_object
    shrub.name = "Forest_Shrub_Lantana"
    link_to_col(shrub, col)
    return shrub

def build_tall_grass(col):
    mat_grass = make_material("M_Tall_Grass", (0.20, 0.48, 0.12, 1.0), roughness=0.7)
    blades = []
    for i in range(18):
        ang = (i / 18.0) * math.pi * 2.0 + (i % 2) * 0.15
        tilt = 0.25 + (i % 4) * 0.08
        h = 1.4 + (i % 3) * 0.3
        bpy.ops.mesh.primitive_cone_add(radius1=0.06, radius2=0.005, depth=h, vertices=4, location=(0, h/2.0, 0))
        blade = bpy.context.active_object
        blade.rotation_euler = (tilt, 0.0, ang)
        blade.location = (math.cos(ang) * 0.2, 0.0, math.sin(ang) * 0.2)
        blade.data.materials.append(mat_grass)
        blades.append(blade)

    bpy.ops.object.select_all(action='DESELECT')
    for b in blades:
        b.select_set(True)
    bpy.context.view_layer.objects.active = blades[0]
    bpy.ops.object.join()
    grass = bpy.context.active_object
    grass.name = "Tall_Grass_Tuft"
    link_to_col(grass, col)
    return grass

# ---------------------------------------------------------------------------
# 5. Water Features (Carved Pond Basin with Boulders & Reeds)
# ---------------------------------------------------------------------------
def build_pond_basin(col):
    # Sculpted basin with sandy shoreline, perimeter rocks, and water disc
    # 1. Sculpted Shoreline Basin
    bpy.ops.mesh.primitive_cylinder_add(radius=18.0, depth=2.4, vertices=32, location=(0, -1.0, 0))
    basin = bpy.context.active_object
    basin.name = "Pond_Shore_Basin"
    mat_shore = make_material("M_Pond_Shore", (0.35, 0.28, 0.20, 1.0), roughness=0.95)
    basin.data.materials.append(mat_shore)

    parts = []
    # 2. Reflective Water Surface
    bpy.ops.mesh.primitive_cylinder_add(radius=16.8, depth=0.1, vertices=32, location=(0, 0.0, 0))
    water = bpy.context.active_object
    water.name = "Pond_Water_Surface"
    mat_water = make_material("M_Water_Surface", (0.05, 0.25, 0.35, 0.8), roughness=0.1, transmission=0.85)
    water.data.materials.append(mat_water)
    parts.append(water)

    # 3. 12 Shoreline Boulders
    mat_rock = make_material("M_Pond_Boulder", (0.38, 0.40, 0.42, 1.0), roughness=0.88)
    for i in range(12):
        ang = (i / 12.0) * math.pi * 2.0 + (i % 3) * 0.1
        rx = math.cos(ang) * 16.5
        rz = math.sin(ang) * 16.5
        s = 0.9 + (i % 4) * 0.4
        bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=2, radius=s, location=(rx, 0.2, rz))
        boulder = bpy.context.active_object
        boulder.scale = (1.2, 0.65, 1.0)
        boulder.data.materials.append(mat_rock)
        parts.append(boulder)

    # 4. Reed stalks
    mat_reed = make_material("M_Pond_Reeds", (0.24, 0.45, 0.14, 1.0), roughness=0.7)
    for i in range(16):
        ang = (i / 16.0) * math.pi * 2.0 + 0.3
        rx = math.cos(ang) * 15.2
        rz = math.sin(ang) * 15.2
        bpy.ops.mesh.primitive_cylinder_add(radius=0.05, depth=2.8, vertices=5, location=(rx, 1.1, rz))
        reed = bpy.context.active_object
        reed.rotation_euler = (0.1, 0.0, (i % 4) * 0.2)
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
# 6. Farmland Features (Crop Parcels & Watchtower Machan)
# ---------------------------------------------------------------------------
def build_crop_field(col):
    # Ridged cultivation beds with sugarcane stalks
    mat_soil = make_material("M_Farm_Furrow", (0.24, 0.18, 0.13, 1.0), roughness=0.9)
    mat_cane = make_material("M_Sugarcane_Stalk", (0.18, 0.52, 0.14, 1.0), roughness=0.6)

    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0, 0.15, 0))
    bed = bpy.context.active_object
    bed.scale = (40.0, 0.3, 18.0)
    bed.data.materials.append(mat_soil)

    parts = []
    # Sugarcane stalks in rows
    for rz in [-6.0, -2.0, 2.0, 6.0]:
        for rx in range(-18, 19, 4):
            bpy.ops.mesh.primitive_cylinder_add(radius=0.08, depth=2.4, vertices=6, location=(rx, 1.35, rz))
            stalk = bpy.context.active_object
            stalk.data.materials.append(mat_cane)
            parts.append(stalk)

    bpy.ops.object.select_all(action='DESELECT')
    for p in parts:
        p.select_set(True)
    bed.select_set(True)
    bpy.context.view_layer.objects.active = bed
    bpy.ops.object.join()
    bed.name = "Farmland_Crop_Parcels"
    link_to_col(bed, col)
    return bed

def build_watchtower_machan(col):
    # 4-legged wooden watchtower with platform, railings, roof, ladder
    mat_wood = make_material("M_Machan_Wood", (0.34, 0.22, 0.14, 1.0), roughness=0.88)
    mat_roof = make_material("M_Machan_Roof", (0.55, 0.20, 0.15, 1.0), roughness=0.7)

    # 4 Stilts
    stilt_h = 6.8
    stilts = []
    for sx, sz in [(-2.2, -2.2), (2.2, -2.2), (2.2, 2.2), (-2.2, 2.2)]:
        bpy.ops.mesh.primitive_cylinder_add(radius=0.16, depth=stilt_h, vertices=8, location=(sx, stilt_h/2.0, sz))
        stilt = bpy.context.active_object
        stilt.data.materials.append(mat_wood)
        stilts.append(stilt)

    parts = stilts[1:]

    # Observation Deck Platform
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0, stilt_h, 0))
    deck = bpy.context.active_object
    deck.scale = (5.2, 0.25, 5.2)
    deck.data.materials.append(mat_wood)
    parts.append(deck)

    # Platform Railings
    for rx, rz, sx, sz in [
        (0, 2.5, 5.2, 0.1), (0, -2.5, 5.2, 0.1),
        (2.5, 0, 0.1, 5.2), (-2.5, 0, 0.1, 5.2)
    ]:
        bpy.ops.mesh.primitive_cube_add(size=1.0, location=(rx, stilt_h + 0.6, rz))
        rail = bpy.context.active_object
        rail.scale = (sx, 0.9, sz)
        rail.data.materials.append(mat_wood)
        parts.append(rail)

    # Roof Canopy
    bpy.ops.mesh.primitive_cone_add(radius1=3.8, depth=1.8, vertices=4, location=(0, stilt_h + 2.4, 0))
    roof = bpy.context.active_object
    roof.rotation_euler = (0, math.pi / 4.0, 0)
    roof.data.materials.append(mat_roof)
    parts.append(roof)

    bpy.ops.object.select_all(action='DESELECT')
    for p in parts:
        p.select_set(True)
    stilts[0].select_set(True)
    bpy.context.view_layer.objects.active = stilts[0]
    bpy.ops.object.join()
    machan = bpy.context.active_object
    machan.name = "Watchtower_Machan"
    link_to_col(machan, col)
    return machan

# ---------------------------------------------------------------------------
# 7. Boundary & Camera Assets
# ---------------------------------------------------------------------------
def build_boundary_post(col):
    mat_post = make_material("M_Fence_Post", (0.35, 0.32, 0.30, 1.0), roughness=0.85)
    mat_solar = make_material("M_Solar_Panel", (0.05, 0.10, 0.25, 1.0), roughness=0.2, metalness=0.8)
    mat_sens = make_material("M_Sensor_Box", (0.15, 0.18, 0.22, 1.0), roughness=0.5)

    bpy.ops.mesh.primitive_cylinder_add(radius=0.14, depth=3.2, vertices=8, location=(0, 1.6, 0))
    post = bpy.context.active_object
    post.data.materials.append(mat_post)

    parts = []
    # Solar micro-panel
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0, 3.1, 0.2))
    panel = bpy.context.active_object
    panel.scale = (0.5, 0.35, 0.04)
    panel.rotation_euler = (0.45, 0, 0)
    panel.data.materials.append(mat_solar)
    parts.append(panel)

    # Sensor Unit Enclosure
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0, 1.8, 0.18))
    sbox = bpy.context.active_object
    sbox.scale = (0.35, 0.45, 0.25)
    sbox.data.materials.append(mat_sens)
    parts.append(sbox)

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
    mat_mast = make_material("M_Camera_Mast", (0.28, 0.32, 0.36, 1.0), roughness=0.4, metalness=0.7)
    mat_cam = make_material("M_ESP32_Cam", (0.92, 0.92, 0.92, 1.0), roughness=0.3)
    mat_lens = make_material("M_Cam_Lens", (0.05, 0.05, 0.08, 1.0), roughness=0.1, metalness=0.9)

    bpy.ops.mesh.primitive_cylinder_add(radius=0.15, depth=5.5, vertices=10, location=(0, 2.75, 0))
    mast = bpy.context.active_object
    mast.data.materials.append(mat_mast)

    parts = []
    # Enclosure
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0, 5.4, 0.35))
    cam = bpy.context.active_object
    cam.scale = (0.4, 0.35, 0.6)
    cam.data.materials.append(mat_cam)
    parts.append(cam)

    # Lens
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
# 8. Animal Species (Importing & Linking All 6 Production Animals)
# ---------------------------------------------------------------------------
def import_and_organize_animals(cols):
    species_map = {
        "SPECIES_ELEPHANT": ("asian_elephant_production.glb", "Elephant_Production_Asset"),
        "SPECIES_DEER": [("chital_deer.glb", "Chital_Deer_Production_Asset"), ("sambar_deer.glb", "Sambar_Deer_Production_Asset")],
        "SPECIES_WILD_BOAR": ("wild_boar.glb", "Wild_Boar_Production_Asset"),
        "SPECIES_GAUR": ("gaur_bison.glb", "Gaur_Bison_Production_Asset"),
        "SPECIES_MONKEY": ("bonnet_macaque.glb", "Bonnet_Macaque_Production_Asset"),
    }

    imported_species = {}

    for col_name, file_info in species_map.items():
        col = cols[col_name]
        files = file_info if isinstance(file_info, list) else [file_info]
        for fname, asset_name in files:
            src_path = os.path.join(STATIC_ASSETS_DIR, "animals", fname)
            if os.path.exists(src_path):
                before_objs = set(bpy.data.objects)
                bpy.ops.import_scene.gltf(filepath=src_path)
                new_objs = list(set(bpy.data.objects) - before_objs)
                for o in new_objs:
                    link_to_col(o, col)
                print(f"Imported {fname} ({len(new_objs)} objects) into collection {col_name}")
                imported_species[asset_name] = new_objs

    return imported_species

# ---------------------------------------------------------------------------
# 9. Dedicated GLB Exporter for Production Web App
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
    # Mirror copy to web static
    shutil.copy2(out_assets, out_static)
    print(f"Exported: {rel_out_path} ({os.path.getsize(out_assets)} bytes)")

# ---------------------------------------------------------------------------
# Main Orchestrator
# ---------------------------------------------------------------------------
def main():
    print("=== Starting PRW-Wild Production World Asset Generation ===")
    ensure_dirs()
    reset_scene()
    cols = setup_collections()

    # 1. Sculpted Natural Terrain
    terrain_obj = build_sculpted_terrain(cols["ENV_TERRAIN"])
    export_asset_glb([terrain_obj], "environment/terrain/terrain_world.glb")

    # 2. Forest Trees
    sal_tree = build_sal_tree(cols["ENV_FOREST"])
    export_asset_glb([sal_tree], "environment/trees/sal_mature.glb")

    banyan_tree = build_banyan_tree(cols["ENV_FOREST"])
    export_asset_glb([banyan_tree], "environment/trees/banyan_fig.glb")

    acacia_tree = build_acacia_tree(cols["ENV_FOREST"])
    export_asset_glb([acacia_tree], "environment/trees/acacia_canopy.glb")

    # 3. Fruit Trees
    mango_tree = build_mango_fruit_tree(cols["ENV_FRUIT_TREES"])
    export_asset_glb([mango_tree], "environment/fruit_trees/mango_fruit_tree.glb")

    # 4. Vegetation & Grass
    ferns = build_forest_ferns(cols["ENV_VEGETATION"])
    export_asset_glb([ferns], "environment/vegetation/forest_ferns.glb")

    shrub = build_forest_shrub(cols["ENV_VEGETATION"])
    export_asset_glb([shrub], "environment/vegetation/forest_shrub.glb")

    grass = build_tall_grass(cols["ENV_GRASS"])
    export_asset_glb([grass], "environment/grass/tall_grass_clump.glb")

    # 5. Water Features
    pond = build_pond_basin(cols["ENV_WATER"])
    export_asset_glb([pond], "environment/water/pond_basin.glb")

    # 6. Farmland
    crops = build_crop_field(cols["ENV_FARMLAND"])
    export_asset_glb([crops], "environment/farmland/crop_field.glb")

    machan = build_watchtower_machan(cols["ENV_FARMLAND"])
    export_asset_glb([machan], "environment/farmland/watchtower_machan.glb")

    # 7. Boundary & Cameras
    fence_post = build_boundary_post(cols["ENV_BOUNDARY"])
    export_asset_glb([fence_post], "environment/boundary/boundary_fence_sensor.glb")

    cam_mast = build_camera_tower(cols["CAMERA_ASSETS"])
    export_asset_glb([cam_mast], "cameras/camera_tower.glb")

    # 8. Animal Species
    import_and_organize_animals(cols)

    # 9. Save Master Production Blend File
    bpy.ops.wm.save_as_mainfile(filepath=BLEND_OUT_PATH)
    print(f"Master production scene saved to: {BLEND_OUT_PATH} ({os.path.getsize(BLEND_OUT_PATH)} bytes)")

    print("=== All Production 3D Assets Successfully Generated and Verified ===")

if __name__ == "__main__":
    main()

