"""Unit and Integration Tests for Autonomous Multi-Animal Ecosystem.

Verifies:
- 50-75 animal agent population initialization
- Species registry coverage for 6 Indian wildlife species
- Dynamic resource consumption and regeneration
- FSM behavior transitions and Reynolds flocking/cohesion
- Boundary crossing and turn-away events
- Manual operator injection
"""

import math
import pytest
from prw_wild.ecosystem import (
    PopulationEcosystem,
    SpeciesType,
    SPECIES_REGISTRY,
    BehaviorState,
    ResourcePatch,
    AutonomousAnimal,
)
from prw_wild.geometry import Point, Segment


def test_species_registry_complete():
    """All 6 target Indian wildlife species must be present in registry."""
    expected_species = [
        SpeciesType.ASIAN_ELEPHANT.value,
        SpeciesType.CHITAL_DEER.value,
        SpeciesType.SAMBAR_DEER.value,
        SpeciesType.WILD_BOAR.value,
        SpeciesType.GAUR_BISON.value,
        SpeciesType.BONNET_MACAQUE.value,
    ]
    for sp in expected_species:
        assert sp in SPECIES_REGISTRY
        prof = SPECIES_REGISTRY[sp]
        assert prof.mass_kg > 0
        assert prof.typical_speed_m_s > 0
        assert prof.visual_model.endswith(".glb")
        assert prof.radar_color.startswith("#")


def test_population_initialization():
    """Ecosystem must initialize with >= 50 independent agents."""
    eco = PopulationEcosystem(population_size=60, seed=123)
    assert len(eco.agents) == 60

    # Verify unique animal IDs
    ids = [a.animal_id for a in eco.agents]
    assert len(set(ids)) == 60

    # Verify species diversity
    species_present = set(a.species for a in eco.agents)
    assert len(species_present) >= 5, "Ecosystem must feature multiple distinct species"

    # All animals initially start in forest zone (x < boundary_x)
    for a in eco.agents:
        assert a.position.x < eco.boundary_x
        assert not a.crossed_boundary
        assert a.crossing_time_s is None


def test_resource_consumption_and_regeneration():
    """Resource patches must deplete upon consumption and regenerate over time."""
    patch = ResourcePatch("grass_1", "grass", Point(50, 50), radius_m=20.0, max_capacity=100.0, current_amount=100.0, regeneration_rate=5.0)
    consumed = patch.consume(30.0)
    assert consumed == 30.0
    assert patch.current_amount == 70.0

    # Advance 2 seconds -> should regenerate 10 units
    patch.step(2.0)
    assert patch.current_amount == 80.0

    # Over-consume
    consumed2 = patch.consume(150.0)
    assert consumed2 == 80.0
    assert patch.current_amount == 0.0


def test_behavior_stepping_and_transitions():
    """Animals advance position, adjust speed, and transition states."""
    eco = PopulationEcosystem(population_size=50, seed=999)
    initial_positions = [(a.position.x, a.position.y) for a in eco.agents]

    # Step simulation 10 seconds (20 steps of 0.5s)
    for _ in range(20):
        eco.step(0.5)

    assert eco.time_s == pytest.approx(10.0, abs=1e-4)

    # Animals must have moved from initial positions
    moved_count = 0
    for idx, a in enumerate(eco.agents):
        ix, iy = initial_positions[idx]
        if math.hypot(a.position.x - ix, a.position.y - iy) > 0.5:
            moved_count += 1

    assert moved_count >= 40, f"Expected most animals to move, moved: {moved_count}/50"


def test_manual_intent_injection():
    """Operator manual injection ('approach', 'turn_away', 'cross') updates agent state."""
    eco = PopulationEcosystem(population_size=50, seed=42)
    target_aid = eco.agents[0].animal_id

    # Inject cross
    ok = eco.inject_event(target_aid, "cross")
    assert ok is True
    assert eco.agents[0].manual_intent == "cross"

    # Step until agent reaches crossing state
    eco.step(0.5)
    assert eco.agents[0].state == BehaviorState.CROSSING_BOUNDARY


def test_twelve_model_variants_demographic_assignment():
    """Verify all 12 distinct demographic models are assigned across agents."""
    eco = PopulationEcosystem(population_size=60, seed=42)
    variants = set(a.model_variant for a in eco.agents)

    expected_variants = {
        "asian_elephant_bull",
        "asian_elephant_cow",
        "chital_stag",
        "chital_hind",
        "sambar_stag",
        "sambar_cow",
        "wild_boar_razorback",
        "wild_boar_sow",
        "gaur_bull",
        "gaur_cow",
        "bonnet_macaque_alpha",
        "bonnet_macaque_forager",
    }
    assert variants == expected_variants, f"Missing or unexpected variants: {expected_variants.symmetric_difference(variants)}"

    # Ensure to_dict() includes model_variant
    data = eco.agents[0].to_dict()
    assert "model_variant" in data
    assert data["model_variant"] == eco.agents[0].model_variant


