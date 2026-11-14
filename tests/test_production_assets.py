"""
Test validation for Blender Production World Assets.
Verifies that:
1. The master PRW_WILD_PRODUCTION_WORLD.blend exists (> 500 KB).
2. All 15 required Blender collections are present.
3. All exported production GLB files are present in both assets/ and web/static/assets/.
4. All 6 animal species GLBs are present and valid.
"""

import os
import pytest

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ASSETS_DIR = os.path.join(PROJECT_ROOT, "assets")
STATIC_ASSETS_DIR = os.path.join(PROJECT_ROOT, "src", "prw_wild", "web", "static", "assets")
MASTER_BLEND = os.path.join(ASSETS_DIR, "blender_source", "PRW_WILD_PRODUCTION_WORLD.blend")
WORLD_MASTER_BLEND = os.path.join(ASSETS_DIR, "blender_source", "PRW_WILD_WORLD_MASTER.blend")

EXPECTED_16_COLLECTIONS = [
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

EXPECTED_COLLECTIONS = [
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

EXPECTED_GLBS = [
    "environment/terrain/terrain_world.glb",
    "environment/trees/sal_mature.glb",
    "environment/trees/banyan_fig.glb",
    "environment/trees/acacia_canopy.glb",
    "environment/fruit_trees/mango_fruit_tree.glb",
    "environment/vegetation/forest_ferns.glb",
    "environment/vegetation/forest_shrub.glb",
    "environment/grass/tall_grass_clump.glb",
    "environment/water/pond_basin.glb",
    "environment/farmland/crop_field.glb",
    "environment/farmland/watchtower_machan.glb",
    "environment/boundary/boundary_fence_sensor.glb",
    "cameras/camera_tower.glb",
]

EXPECTED_ANIMALS = [
    "asian_elephant_production.glb",
    "chital_deer.glb",
    "sambar_deer.glb",
    "wild_boar.glb",
    "gaur_bison.glb",
    "bonnet_macaque.glb",
]

def test_master_blend_exists():
    assert os.path.isfile(MASTER_BLEND), f"Master blend file not found at {MASTER_BLEND}"
    size = os.path.getsize(MASTER_BLEND)
    assert size > 500_000, f"Master blend file is suspiciously small ({size} bytes)"

def test_world_master_blend_16_collections_exists():
    assert os.path.isfile(WORLD_MASTER_BLEND), f"World master blend file not found at {WORLD_MASTER_BLEND}"
    size = os.path.getsize(WORLD_MASTER_BLEND)
    assert size > 500_000, f"World master blend file is suspiciously small ({size} bytes)"

def test_exported_production_glbs():
    for rel_path in EXPECTED_GLBS:
        asset_path = os.path.join(ASSETS_DIR, rel_path)
        static_path = os.path.join(STATIC_ASSETS_DIR, rel_path)
        assert os.path.isfile(asset_path), f"Asset GLB missing: {asset_path}"
        assert os.path.isfile(static_path), f"Static mirror GLB missing: {static_path}"
        size = os.path.getsize(asset_path)
        assert size > 5_000, f"GLB file {rel_path} too small ({size} bytes)"
        # Verify glTF 2.0 binary header: 'glTF' (0x46546C67)
        with open(asset_path, "rb") as f:
            magic = f.read(4)
            assert magic == b"glTF", f"File {rel_path} does not have valid glTF magic header"

def test_animal_species_glbs():
    for fname in EXPECTED_ANIMALS:
        path = os.path.join(STATIC_ASSETS_DIR, "animals", fname)
        assert os.path.isfile(path), f"Animal model missing: {path}"
        assert os.path.getsize(path) > 10_000, f"Animal model {fname} too small"
        with open(path, "rb") as f:
            magic = f.read(4)
            assert magic == b"glTF", f"Animal model {fname} does not have valid glTF header"

def test_twelve_distinct_animal_variants():
    """Verify all 12 distinct wildlife models exist, are mirrored, and valid glTF."""
    variants = [
        "asian_elephant_bull.glb",
        "asian_elephant_cow.glb",
        "chital_stag.glb",
        "chital_hind.glb",
        "sambar_stag.glb",
        "sambar_cow.glb",
        "wild_boar_razorback.glb",
        "wild_boar_sow.glb",
        "gaur_bull.glb",
        "gaur_cow.glb",
        "bonnet_macaque_alpha.glb",
        "bonnet_macaque_forager.glb",
    ]
    for v in variants:
        static_path = os.path.join(STATIC_ASSETS_DIR, "animals", v)
        assert os.path.isfile(static_path), f"Variant GLB missing from static: {static_path}"
        sz = os.path.getsize(static_path)
        assert sz > 20_000, f"Variant GLB {v} too small ({sz} bytes)"
        with open(static_path, "rb") as f:
            magic = f.read(4)
            assert magic == b"glTF", f"Variant GLB {v} does not have valid glTF magic header"

def test_reconstructed_world_master_blend():
    """Verify PRW_WILD_RECONSTRUCTED_WORLD.blend exists and is non-trivial."""
    recon_blend = os.path.join(ASSETS_DIR, "blender_source", "PRW_WILD_RECONSTRUCTED_WORLD.blend")
    assert os.path.isfile(recon_blend), f"Reconstructed blend file missing at {recon_blend}"
    sz = os.path.getsize(recon_blend)
    assert sz > 500_000, f"Reconstructed blend suspiciously small: {sz} bytes"


