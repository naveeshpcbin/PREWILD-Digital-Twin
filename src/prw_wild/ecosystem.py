"""
PRW-Wild Autonomous Multi-Animal Ecosystem Engine.
Enriches all 60+ animals with distinct individual names, demographics, scale factors,
behavioral roles, dynamic tasks, and exact 3D terrain elevation grounding.
"""

import math
import random
from dataclasses import dataclass, field
from enum import Enum
from typing import List, Dict, Any, Optional, Tuple

from prw_wild.geometry import Point, Segment

# ---------------------------------------------------------------------------
# Terrain Analytical Elevation Function
# ---------------------------------------------------------------------------

def get_terrain_elevation(x: float, z: float) -> float:
    """Exact analytical elevation function matching Blender 5.2.2 terrain model.
    x: East-West coordinate (0..225m, fence at x=100)
    z: North-South coordinate (0..200m)
    """
    base = (100.0 - x) * 0.015 if x < 100 else -(x - 100.0) * 0.005
    y = base

    if x < 100:
        # Western Forest Zone rolling hills & west ridge
        hills = (
            math.sin(x * 0.065 + 1.2) * math.cos(z * 0.055) * 1.8 +
            math.sin(x * 0.12 - 0.5) * math.cos(z * 0.11 + 0.8) * 0.75 +
            math.sin(x * 0.22) * math.sin(z * 0.19) * 0.35
        )
        west_ridge = max(0.0, (40.0 - x) * 0.08)
        y += hills + west_ridge
    else:
        # Eastern Farmland stepped terraces every 28m
        ter_idx = math.floor((x - 100.0) / 28.0)
        ter_rem = (x - 100.0) % 28.0
        farm_grade = -ter_idx * 0.35 - (ter_rem / 28.0) * 0.08
        furrows = math.sin(z * 1.1) * 0.06
        y += farm_grade + furrows

    # Animal corridor riverbed / ancient migratory valley depression near z=100
    corr_dist_z = abs(z - (100.0 + math.sin(x * 0.05) * 6.0))
    if corr_dist_z < 22.0 and x < 105:
        corr_factor = (1.0 - (corr_dist_z / 22.0)) ** 2
        y -= corr_factor * 2.2

    # North Pond depression at (X=75, Z=140, radius ~22m)
    dist_p1 = math.hypot(x - 75.0, z - 140.0)
    if dist_p1 < 22.0:
        depth1 = (1.0 - (dist_p1 / 22.0)) ** 1.8
        y -= depth1 * 2.4

    # South Pond depression at (X=45, Z=60, radius ~18m)
    dist_p2 = math.hypot(x - 45.0, z - 60.0)
    if dist_p2 < 18.0:
        depth2 = (1.0 - (dist_p2 / 18.0)) ** 1.8
        y -= depth2 * 2.1

    # Surface micro-roughness
    y += math.sin(x * 1.7 + z * 1.3) * 0.04
    return y


# ---------------------------------------------------------------------------
# Species Registry & Taxonomy
# ---------------------------------------------------------------------------

class SpeciesType(str, Enum):
    ASIAN_ELEPHANT = "asian_elephant"
    CHITAL_DEER = "chital_deer"
    SAMBAR_DEER = "sambar_deer"
    WILD_BOAR = "wild_boar"
    GAUR_BISON = "gaur_bison"
    BONNET_MACAQUE = "bonnet_macaque"
    BENGAL_TIGER = "bengal_tiger"
    INDIAN_LEOPARD = "indian_leopard"
    SLOTH_BEAR = "sloth_bear"
    DHOLE = "dhole"
    INDIAN_MUNTJAC = "indian_muntjac"
    GOLDEN_JACKAL = "golden_jackal"
    GRAY_LANGUR = "gray_langur"
    CRESTED_PORCUPINE = "crested_porcupine"
    INDIAN_PEAFOWL = "indian_peafowl"
    INDIAN_HARE = "indian_hare"


@dataclass(frozen=True)
class SpeciesProfile:
    species_id: str
    common_name: str
    scientific_name: str
    mass_kg: float
    typical_speed_m_s: float
    sprint_speed_m_s: float
    diet: str  # "grazer", "browser", "omnivore", "frugivore"
    herd_affinity: float  # [0.0, 1.0]
    boundary_caution: float  # [0.0, 1.0]
    visual_model: str
    radar_color: str


SPECIES_REGISTRY: Dict[str, SpeciesProfile] = {
    SpeciesType.ASIAN_ELEPHANT.value: SpeciesProfile(
        species_id=SpeciesType.ASIAN_ELEPHANT.value,
        common_name="Asian Elephant",
        scientific_name="Elephas maximus",
        mass_kg=3500.0,
        typical_speed_m_s=1.2,
        sprint_speed_m_s=3.5,
        diet="browser",
        herd_affinity=0.75,
        boundary_caution=0.55,
        visual_model="assets/animals/asian_elephant_production.glb",
        radar_color="#e06666"
    ),
    SpeciesType.CHITAL_DEER.value: SpeciesProfile(
        species_id=SpeciesType.CHITAL_DEER.value,
        common_name="Chital / Spotted Deer",
        scientific_name="Axis axis",
        mass_kg=55.0,
        typical_speed_m_s=1.5,
        sprint_speed_m_s=5.0,
        diet="grazer",
        herd_affinity=0.85,
        boundary_caution=0.70,
        visual_model="assets/animals/chital_deer.glb",
        radar_color="#ffd966"
    ),
    SpeciesType.SAMBAR_DEER.value: SpeciesProfile(
        species_id=SpeciesType.SAMBAR_DEER.value,
        common_name="Sambar Deer",
        scientific_name="Rusa unicolor",
        mass_kg=220.0,
        typical_speed_m_s=1.3,
        sprint_speed_m_s=4.2,
        diet="browser",
        herd_affinity=0.40,
        boundary_caution=0.65,
        visual_model="assets/animals/sambar_deer.glb",
        radar_color="#b45f06"
    ),
    SpeciesType.WILD_BOAR.value: SpeciesProfile(
        species_id=SpeciesType.WILD_BOAR.value,
        common_name="Indian Wild Boar",
        scientific_name="Sus scrofa cristatus",
        mass_kg=85.0,
        typical_speed_m_s=1.6,
        sprint_speed_m_s=5.5,
        diet="omnivore",
        herd_affinity=0.60,
        boundary_caution=0.45,
        visual_model="assets/animals/wild_boar.glb",
        radar_color="#cc0000"
    ),
    SpeciesType.GAUR_BISON.value: SpeciesProfile(
        species_id=SpeciesType.GAUR_BISON.value,
        common_name="Gaur / Indian Bison",
        scientific_name="Bos gaurus",
        mass_kg=950.0,
        typical_speed_m_s=1.1,
        sprint_speed_m_s=3.8,
        diet="grazer",
        herd_affinity=0.65,
        boundary_caution=0.60,
        visual_model="assets/animals/gaur_bison.glb",
        radar_color="#76a5af"
    ),
    SpeciesType.BONNET_MACAQUE.value: SpeciesProfile(
        species_id=SpeciesType.BONNET_MACAQUE.value,
        common_name="Bonnet Macaque",
        scientific_name="Macaca radiata",
        mass_kg=8.5,
        typical_speed_m_s=1.8,
        sprint_speed_m_s=4.5,
        diet="frugivore",
        herd_affinity=0.90,
        boundary_caution=0.40,
        visual_model="assets/animals/bonnet_macaque.glb",
        radar_color="#8e7cc3"
    ),
    SpeciesType.BENGAL_TIGER.value: SpeciesProfile(
        species_id=SpeciesType.BENGAL_TIGER.value,
        common_name="Bengal Tiger",
        scientific_name="Panthera tigris tigris",
        mass_kg=220.0,
        typical_speed_m_s=1.8,
        sprint_speed_m_s=16.0,
        diet="carnivore",
        herd_affinity=0.10,
        boundary_caution=0.85,
        visual_model="assets/animals/bengal_tiger.glb",
        radar_color="#ff7700"
    ),
    SpeciesType.INDIAN_LEOPARD.value: SpeciesProfile(
        species_id=SpeciesType.INDIAN_LEOPARD.value,
        common_name="Indian Leopard",
        scientific_name="Panthera pardus fusca",
        mass_kg=65.0,
        typical_speed_m_s=1.7,
        sprint_speed_m_s=15.5,
        diet="carnivore",
        herd_affinity=0.10,
        boundary_caution=0.80,
        visual_model="assets/animals/indian_leopard.glb",
        radar_color="#ffa500"
    ),
    SpeciesType.SLOTH_BEAR.value: SpeciesProfile(
        species_id=SpeciesType.SLOTH_BEAR.value,
        common_name="Sloth Bear",
        scientific_name="Melursus ursinus",
        mass_kg=110.0,
        typical_speed_m_s=1.0,
        sprint_speed_m_s=9.0,
        diet="omnivore",
        herd_affinity=0.20,
        boundary_caution=0.60,
        visual_model="assets/animals/sloth_bear.glb",
        radar_color="#4a4a4a"
    ),
    SpeciesType.DHOLE.value: SpeciesProfile(
        species_id=SpeciesType.DHOLE.value,
        common_name="Dhole / Asiatic Wild Dog",
        scientific_name="Cuon alpinus",
        mass_kg=17.0,
        typical_speed_m_s=1.9,
        sprint_speed_m_s=13.0,
        diet="carnivore",
        herd_affinity=0.90,
        boundary_caution=0.50,
        visual_model="assets/animals/dhole.glb",
        radar_color="#c0392b"
    ),
    SpeciesType.INDIAN_MUNTJAC.value: SpeciesProfile(
        species_id=SpeciesType.INDIAN_MUNTJAC.value,
        common_name="Indian Muntjac / Barking Deer",
        scientific_name="Muntiacus muntjak",
        mass_kg=22.0,
        typical_speed_m_s=1.4,
        sprint_speed_m_s=12.5,
        diet="browser",
        herd_affinity=0.30,
        boundary_caution=0.75,
        visual_model="assets/animals/indian_muntjac.glb",
        radar_color="#d35400"
    ),
    SpeciesType.GOLDEN_JACKAL.value: SpeciesProfile(
        species_id=SpeciesType.GOLDEN_JACKAL.value,
        common_name="Golden Jackal",
        scientific_name="Canis aureus",
        mass_kg=9.5,
        typical_speed_m_s=1.6,
        sprint_speed_m_s=11.0,
        diet="omnivore",
        herd_affinity=0.40,
        boundary_caution=0.65,
        visual_model="assets/animals/golden_jackal.glb",
        radar_color="#e67e22"
    ),
    SpeciesType.GRAY_LANGUR.value: SpeciesProfile(
        species_id=SpeciesType.GRAY_LANGUR.value,
        common_name="Gray Langur / Hanuman Langur",
        scientific_name="Semnopithecus entellus",
        mass_kg=12.0,
        typical_speed_m_s=1.7,
        sprint_speed_m_s=9.5,
        diet="folivore",
        herd_affinity=0.85,
        boundary_caution=0.45,
        visual_model="assets/animals/gray_langur.glb",
        radar_color="#95a5a6"
    ),
    SpeciesType.CRESTED_PORCUPINE.value: SpeciesProfile(
        species_id=SpeciesType.CRESTED_PORCUPINE.value,
        common_name="Indian Crested Porcupine",
        scientific_name="Hystrix indica",
        mass_kg=14.5,
        typical_speed_m_s=0.8,
        sprint_speed_m_s=3.5,
        diet="herbivore",
        herd_affinity=0.30,
        boundary_caution=0.80,
        visual_model="assets/animals/crested_porcupine.glb",
        radar_color="#34495e"
    ),
    SpeciesType.INDIAN_PEAFOWL.value: SpeciesProfile(
        species_id=SpeciesType.INDIAN_PEAFOWL.value,
        common_name="Indian Peafowl",
        scientific_name="Pavo cristatus",
        mass_kg=5.0,
        typical_speed_m_s=1.1,
        sprint_speed_m_s=4.4,
        diet="omnivore",
        herd_affinity=0.50,
        boundary_caution=0.70,
        visual_model="assets/animals/indian_peafowl.glb",
        radar_color="#2980b9"
    ),
    SpeciesType.INDIAN_HARE.value: SpeciesProfile(
        species_id=SpeciesType.INDIAN_HARE.value,
        common_name="Indian Hare / Black-Naped Hare",
        scientific_name="Lepus nigricollis",
        mass_kg=3.2,
        typical_speed_m_s=1.5,
        sprint_speed_m_s=15.0,
        diet="grazer",
        herd_affinity=0.20,
        boundary_caution=0.85,
        visual_model="assets/animals/indian_hare.glb",
        radar_color="#bdc3c7"
    ),
}


# ---------------------------------------------------------------------------
# Behavior States
# ---------------------------------------------------------------------------

class BehaviorState(str, Enum):
    IDLE = "idle"
    WALKING = "walking"
    GRAZING = "grazing"
    BROWSING = "browsing"
    DRINKING = "drinking"
    RESTING = "resting"
    EXPLORING = "exploring"
    HERD_FOLLOW = "herd_following"
    APPROACHING_BOUNDARY = "approaching_boundary"
    TURNING_AWAY = "turning_away"
    CROSSING_BOUNDARY = "crossing_boundary"
    RETURNING_FOREST = "returning_forest"


# ---------------------------------------------------------------------------
# Ecological Resource Patches
# ---------------------------------------------------------------------------

@dataclass
class ResourcePatch:
    patch_id: str
    resource_type: str  # "grass", "browse", "water", "crops"
    position: Point
    radius_m: float
    max_capacity: float = 100.0
    current_amount: float = 100.0
    regeneration_rate: float = 0.5  # units/second

    def consume(self, amount: float) -> float:
        consumed = min(self.current_amount, amount)
        self.current_amount -= consumed
        return consumed

    def step(self, dt: float) -> None:
        if self.current_amount < self.max_capacity:
            self.current_amount = min(self.max_capacity, self.current_amount + self.regeneration_rate * dt)

    def contains(self, p: Point) -> bool:
        return self.position.distance_to(p) <= self.radius_m


# ---------------------------------------------------------------------------
# Autonomous Animal Agent with Individual Identity & Grounding
# ---------------------------------------------------------------------------

@dataclass
class AutonomousAnimal:
    animal_id: str
    species: str
    group_id: str
    position: Point
    velocity: Point
    heading_rad: float
    speed_m_s: float
    name: str = ""
    demographic: str = "adult"  # "alpha_male", "matriarch", "adult_female", "sub_adult", "juvenile", "calf"
    scale_factor: float = 1.0
    role: str = "forager"  # "boundary_prober", "boundary_averse", "grazing_herbivore", "canopy_browser", "pond_drinker", "cautious_sentinel"
    current_task: str = "Foraging in forest"
    is_leader: bool = False
    state: BehaviorState = BehaviorState.WALKING
    state_timer_s: float = 0.0
    model_variant: str = ""

    # Internal need drives [0.0 = satisfied, 1.0 = urgent need]
    hunger: float = 0.2
    thirst: float = 0.2
    fatigue: float = 0.1

    # Boundary relationships
    crossed_boundary: bool = False
    crossing_time_s: Optional[float] = None
    target_point: Optional[Point] = None

    # Manual test injection flag
    manual_intent: Optional[str] = None  # "approach", "turn_away", "cross"

    def __post_init__(self):
        if not self.model_variant:
            self.model_variant = self._resolve_model_variant()

    def _resolve_model_variant(self) -> str:
        sp = self.species
        demo = self.demographic
        nm = self.name.lower()
        if sp == "asian_elephant":
            if demo in ["alpha_male", "sub_adult"] or "tusker" in nm or "bull" in nm:
                return "asian_elephant_bull"
            return "asian_elephant_cow"
        elif sp == "chital_deer":
            if demo in ["alpha_male", "sub_adult"] or "stag" in nm:
                return "chital_stag"
            return "chital_hind"
        elif sp == "sambar_deer":
            if demo in ["alpha_male", "sub_adult"] or "stag" in nm:
                return "sambar_stag"
            return "sambar_cow"
        elif sp == "wild_boar":
            if demo in ["alpha_male", "sub_adult"] or "razorback" in nm or "boar" in nm:
                return "wild_boar_razorback"
            return "wild_boar_sow"
        elif sp == "gaur_bison":
            if demo in ["alpha_male", "sub_adult"] or "bull" in nm:
                return "gaur_bull"
            return "gaur_cow"
        elif sp == "bonnet_macaque":
            if demo in ["alpha_male"] or "alpha" in nm:
                return "bonnet_macaque_alpha"
            return "bonnet_macaque_forager"
        return sp

    @property
    def elevation_y(self) -> float:
        return get_terrain_elevation(self.position.x, self.position.y)

    def step(
        self,
        dt: float,
        boundary: Segment,
        all_agents: List["AutonomousAnimal"],
        resources: List[ResourcePatch],
        corridors: List[dict],
        rng: random.Random,
        world_bounds: Tuple[float, float, float, float]
    ) -> None:
        self.state_timer_s += dt

        # Increment need drives slowly
        self.hunger = min(1.0, self.hunger + 0.003 * dt)
        self.thirst = min(1.0, self.thirst + 0.004 * dt)
        self.fatigue = min(1.0, self.fatigue + 0.002 * dt)

        profile = SPECIES_REGISTRY.get(self.species, SPECIES_REGISTRY[SpeciesType.ASIAN_ELEPHANT.value])
        min_x, max_x, min_y, max_y = world_bounds

        # FSM State Transitions
        self._update_state_transitions(boundary, resources, profile, rng)

        # Steering calculation based on current state & flocking
        accel = self._compute_steering(dt, boundary, all_agents, resources, corridors, profile, rng, world_bounds)

        # Integrate velocity and position
        max_speed = profile.sprint_speed_m_s if self.state in [
            BehaviorState.CROSSING_BOUNDARY, BehaviorState.TURNING_AWAY
        ] else profile.typical_speed_m_s

        if self.state in [BehaviorState.IDLE, BehaviorState.RESTING]:
            self.velocity = Point(self.velocity.x * 0.8, self.velocity.y * 0.8)
        else:
            new_vx = self.velocity.x + accel.x * dt
            new_vy = self.velocity.y + accel.y * dt
            v_mag = math.hypot(new_vx, new_vy)
            if v_mag > max_speed:
                new_vx = (new_vx / v_mag) * max_speed
                new_vy = (new_vy / v_mag) * max_speed
            elif v_mag < 0.1 and self.state != BehaviorState.IDLE:
                new_vx = math.cos(self.heading_rad) * 0.5
                new_vy = math.sin(self.heading_rad) * 0.5
            self.velocity = Point(new_vx, new_vy)

        self.position = Point(
            min(max_x - 1.0, max(min_x + 1.0, self.position.x + self.velocity.x * dt)),
            min(max_y - 1.0, max(min_y + 1.0, self.position.y + self.velocity.y * dt))
        )

        speed = math.hypot(self.velocity.x, self.velocity.y)
        self.speed_m_s = speed
        if speed > 0.05:
            self.heading_rad = math.atan2(self.velocity.y, self.velocity.x)

        # Update human-readable current task
        self._update_current_task()

        # Check boundary crossing
        if not self.crossed_boundary:
            self._check_boundary_crossing(boundary)

    def _update_current_task(self) -> None:
        if self.state == BehaviorState.GRAZING:
            self.current_task = "Grazing tall pasture grass"
        elif self.state == BehaviorState.BROWSING:
            self.current_task = "Browsing wild mango & acacia canopy"
        elif self.state == BehaviorState.DRINKING:
            self.current_task = "Drinking at water pond basin"
        elif self.state == BehaviorState.RESTING:
            self.current_task = "Resting in shaded Banyan grove"
        elif self.state == BehaviorState.APPROACHING_BOUNDARY:
            self.current_task = "Probing perimeter fence [WARNING]"
        elif self.state == BehaviorState.TURNING_AWAY:
            self.current_task = "Deterred: Retreating to forest"
        elif self.state == BehaviorState.CROSSING_BOUNDARY:
            self.current_task = "Breaching fence into sugarcane crops [CRITICAL]"
        elif self.state == BehaviorState.HERD_FOLLOW:
            self.current_task = "Following herd matriarch"
        elif self.state == BehaviorState.WALKING:
            self.current_task = "Migrating through corridor valley"
        else:
            self.current_task = "Alert scanning and ruminating"

    def _update_state_transitions(
        self,
        boundary: Segment,
        resources: List[ResourcePatch],
        profile: SpeciesProfile,
        rng: random.Random
    ) -> None:
        fence_x = boundary.a.x
        dist_to_fence = fence_x - self.position.x

        if self.manual_intent == "cross":
            self.state = BehaviorState.CROSSING_BOUNDARY
            return
        elif self.manual_intent == "turn_away":
            self.state = BehaviorState.TURNING_AWAY
            return
        elif self.manual_intent == "approach":
            self.state = BehaviorState.APPROACHING_BOUNDARY
            return

        if self.crossed_boundary:
            if self.state_timer_s > 25.0:
                self.state = BehaviorState.RETURNING_FOREST
            return

        # Approaching fence interaction
        if 0 < dist_to_fence <= 25.0:
            if self.state not in [BehaviorState.APPROACHING_BOUNDARY, BehaviorState.TURNING_AWAY, BehaviorState.CROSSING_BOUNDARY]:
                # Boundary-averse animals immediately turn away
                if self.role == "boundary_averse":
                    self.state = BehaviorState.TURNING_AWAY
                    self.state_timer_s = 0.0
                    return

                # Boundary probers test fence
                if self.role == "boundary_prober":
                    self.state = BehaviorState.APPROACHING_BOUNDARY
                    self.state_timer_s = 0.0
                    return

                cross_prob = (1.0 - profile.boundary_caution) * 0.35 + (self.hunger * 0.3)
                if rng.random() < cross_prob:
                    self.state = BehaviorState.CROSSING_BOUNDARY
                elif rng.random() < 0.6:
                    self.state = BehaviorState.TURNING_AWAY
                else:
                    self.state = BehaviorState.APPROACHING_BOUNDARY
                self.state_timer_s = 0.0
            elif self.state == BehaviorState.APPROACHING_BOUNDARY and dist_to_fence < 8.0:
                if self.role == "boundary_prober" and rng.random() < 0.65:
                    self.state = BehaviorState.CROSSING_BOUNDARY
                elif rng.random() < 0.3:
                    self.state = BehaviorState.CROSSING_BOUNDARY
                else:
                    self.state = BehaviorState.TURNING_AWAY
                self.state_timer_s = 0.0
            return

        # Routine behavior state transitions
        if self.state_timer_s > rng.uniform(8.0, 18.0):
            self.state_timer_s = 0.0

            # Resource fulfillment
            for patch in resources:
                if patch.contains(self.position):
                    if patch.resource_type in ["grass", "browse", "crops"] and self.hunger > 0.3:
                        patch.consume(0.5)
                        self.hunger = max(0.0, self.hunger - 0.25)
                        self.state = BehaviorState.GRAZING if patch.resource_type == "grass" else BehaviorState.BROWSING
                        return
                    elif patch.resource_type == "water" and self.thirst > 0.3:
                        patch.consume(0.5)
                        self.thirst = max(0.0, self.thirst - 0.35)
                        self.state = BehaviorState.DRINKING
                        return

            if self.thirst > 0.6:
                self.state = BehaviorState.DRINKING
            elif self.hunger > 0.6:
                self.state = BehaviorState.GRAZING if profile.diet == "grazer" else BehaviorState.BROWSING
            elif self.fatigue > 0.7:
                self.state = BehaviorState.RESTING
            elif not self.is_leader and rng.random() < profile.herd_affinity:
                self.state = BehaviorState.HERD_FOLLOW
            else:
                self.state = rng.choice([BehaviorState.WALKING, BehaviorState.EXPLORING, BehaviorState.IDLE])

    def _compute_steering(
        self,
        dt: float,
        boundary: Segment,
        all_agents: List["AutonomousAnimal"],
        resources: List[ResourcePatch],
        corridors: List[dict],
        profile: SpeciesProfile,
        rng: random.Random,
        world_bounds: Tuple[float, float, float, float]
    ) -> Point:
        ax, ay = 0.0, 0.0

        if self.state == BehaviorState.APPROACHING_BOUNDARY:
            ax += 2.0
            ay += math.sin(self.state_timer_s * 1.5) * 0.5
            return Point(ax, ay)
        elif self.state == BehaviorState.TURNING_AWAY:
            ax -= 3.5
            ay += 1.0 if self.position.y < 100.0 else -1.0
            return Point(ax, ay)
        elif self.state == BehaviorState.CROSSING_BOUNDARY:
            ax += 3.8
            return Point(ax, ay)
        elif self.state == BehaviorState.RETURNING_FOREST:
            ax -= 2.5
            return Point(ax, ay)

        # Flocking behaviors: Separation, Alignment, Cohesion
        sep_x, sep_y = 0.0, 0.0
        align_x, align_y = 0.0, 0.0
        coh_x, coh_y = 0.0, 0.0
        neighbor_count = 0

        for other in all_agents:
            if other.animal_id == self.animal_id:
                continue
            dist = self.position.distance_to(other.position)
            if dist < 4.0:
                diff_x = self.position.x - other.position.x
                diff_y = self.position.y - other.position.y
                sep_x += diff_x / max(0.1, dist)
                sep_y += diff_y / max(0.1, dist)
            if other.group_id == self.group_id and dist < 25.0:
                align_x += other.velocity.x
                align_y += other.velocity.y
                coh_x += other.position.x
                coh_y += other.position.y
                neighbor_count += 1

        ax += sep_x * 1.8
        ay += sep_y * 1.8

        if neighbor_count > 0:
            ax += (align_x / neighbor_count - self.velocity.x) * 0.4 * profile.herd_affinity
            ay += (align_y / neighbor_count - self.velocity.y) * 0.4 * profile.herd_affinity
            coh_target_x = coh_x / neighbor_count
            coh_target_y = coh_y / neighbor_count
            ax += (coh_target_x - self.position.x) * 0.15 * profile.herd_affinity
            ay += (coh_target_y - self.position.y) * 0.15 * profile.herd_affinity

        # Resource Seeking
        if self.thirst > 0.5:
            nearest_water = min([r for r in resources if r.resource_type == "water"], key=lambda r: r.position.distance_to(self.position))
            dist_w = self.position.distance_to(nearest_water.position)
            if dist_w > nearest_water.radius_m * 0.5:
                ax += (nearest_water.position.x - self.position.x) / dist_w * 1.2
                ay += (nearest_water.position.y - self.position.y) / dist_w * 1.2
        elif self.hunger > 0.5:
            food_types = ["grass"] if profile.diet == "grazer" else ["browse", "grass"]
            food_patches = [r for r in resources if r.resource_type in food_types]
            if food_patches:
                nearest_food = min(food_patches, key=lambda r: r.position.distance_to(self.position))
                dist_f = self.position.distance_to(nearest_food.position)
                if dist_f > nearest_food.radius_m * 0.5:
                    ax += (nearest_food.position.x - self.position.x) / dist_f * 1.0
                    ay += (nearest_food.position.y - self.position.y) / dist_f * 1.0

        # Boundary Avoidance
        fence_x = boundary.a.x
        if self.position.x < fence_x and (fence_x - self.position.x) < 22.0:
            caution_weight = profile.boundary_caution * 2.5
            ax -= (22.0 - (fence_x - self.position.x)) * 0.2 * caution_weight

        # World bounds repulsion
        min_x, max_x, min_y, max_y = world_bounds
        if self.position.x < min_x + 10.0:
            ax += (min_x + 10.0 - self.position.x) * 0.3
        if self.position.x > max_x - 10.0:
            ax -= (self.position.x - (max_x - 10.0)) * 0.3
        if self.position.y < min_y + 10.0:
            ay += (min_y + 10.0 - self.position.y) * 0.3
        if self.position.y > max_y - 10.0:
            ay -= (self.position.y - (max_y - 10.0)) * 0.3

        return Point(ax, ay)

    def _check_boundary_crossing(self, boundary: Segment) -> None:
        bdir_x = boundary.b.x - boundary.a.x
        bdir_y = boundary.b.y - boundary.a.y
        to_pt_x = self.position.x - boundary.a.x
        to_pt_y = self.position.y - boundary.a.y
        cross = bdir_x * to_pt_y - bdir_y * to_pt_x
        if cross < 0:
            self.crossed_boundary = True

    def set_crossing_time(self, t: float) -> None:
        if self.crossed_boundary and self.crossing_time_s is None:
            self.crossing_time_s = t

    def to_dict(self) -> Dict[str, Any]:
        """Telemetry record with individual profile and 3D terrain elevation."""
        return {
            "animal_id": self.animal_id,
            "name": self.name,
            "species": self.species,
            "model_variant": self.model_variant,
            "group_id": self.group_id,
            "demographic": self.demographic,
            "scale_factor": round(self.scale_factor, 2),
            "role": self.role,
            "current_task": self.current_task,
            "position": {"x": round(self.position.x, 2), "y": round(self.position.y, 2), "z": round(self.elevation_y, 2)},
            "elevation_y": round(self.elevation_y, 2),
            "velocity": {"vx": round(self.velocity.x, 2), "vy": round(self.velocity.y, 2)},
            "heading_rad": round(self.heading_rad, 3),
            "speed_m_s": round(self.speed_m_s, 2),
            "state": self.state.value,
            "needs": {
                "hunger": round(self.hunger, 2),
                "thirst": round(self.thirst, 2),
                "fatigue": round(self.fatigue, 2),
            },
            "crossed_boundary": self.crossed_boundary,
            "crossing_time_s": self.crossing_time_s,
        }


# ---------------------------------------------------------------------------
# Population Ecosystem Simulator (60+ Individual Agents)
# ---------------------------------------------------------------------------

class PopulationEcosystem:
    """Manages an autonomous multi-animal ecosystem of 60+ distinct agents."""

    def __init__(
        self,
        population_size: int = 60,
        world_bounds: Tuple[float, float, float, float] = (0.0, 225.0, 0.0, 200.0),
        boundary_x: float = 100.0,
        seed: int = 42
    ):
        self.population_size = max(50, population_size)
        self.world_bounds = world_bounds
        self.boundary_x = boundary_x
        self.boundary = Segment(Point(boundary_x, world_bounds[2]), Point(boundary_x, world_bounds[3]))
        self.rng = random.Random(seed)
        self.time_s: float = 0.0

        # Resources
        self.resources: List[ResourcePatch] = self._init_resources()

        # Agents
        self.agents: List[AutonomousAnimal] = self._spawn_population()

    def _init_resources(self) -> List[ResourcePatch]:
        return [
            # Water sources in forest
            ResourcePatch("water_pond_north", "water", Point(75.0, 140.0), radius_m=20.0),
            ResourcePatch("water_pond_south", "water", Point(45.0, 60.0), radius_m=16.0),
            # Grazing grass clearings
            ResourcePatch("grass_glade_west", "grass", Point(35.0, 100.0), radius_m=22.0),
            ResourcePatch("grass_pasture_north", "grass", Point(55.0, 160.0), radius_m=20.0),
            # Browse groves (sal, banyan, wild mango)
            ResourcePatch("browse_forest_core", "browse", Point(50.0, 80.0), radius_m=25.0),
            ResourcePatch("browse_canopy_north", "browse", Point(40.0, 145.0), radius_m=20.0),
            ResourcePatch("mango_grove_south", "browse", Point(50.0, 50.0), radius_m=18.0),
            # Agricultural crop fields (across fence)
            ResourcePatch("farm_sugar_cane", "crops", Point(145.0, 75.0), radius_m=25.0),
            ResourcePatch("farm_paddy", "crops", Point(145.0, 145.0), radius_m=25.0),
        ]

    def _spawn_population(self) -> List[AutonomousAnimal]:
        agents: List[AutonomousAnimal] = []

        # Specification for all 62 individual animals
        individual_specs = [
            # 1. ASIAN ELEPHANTS (8)
            ("asian_elephant", "Airavata (Lead Tusker)", "alpha_male", 1.30, "herd_matriarch", Point(40, 100), True),
            ("asian_elephant", "Indira (Matriarch)", "matriarch", 1.15, "herd_matriarch", Point(38, 104), False),
            ("asian_elephant", "Gajendra (Calf)", "calf", 0.62, "boundary_averse", Point(35, 101), False),
            ("asian_elephant", "Balarama (Sub-Adult)", "sub_adult", 0.88, "canopy_browser", Point(45, 96), False),
            ("asian_elephant", "Kamala (Adult Cow)", "adult_female", 1.05, "pond_drinker", Point(72, 138), False),
            ("asian_elephant", "Ravana (Solitary Bull)", "alpha_male", 1.35, "boundary_prober", Point(82, 98), False),
            ("asian_elephant", "Meena (Adult Cow)", "adult_female", 1.02, "boundary_averse", Point(48, 55), False),
            ("asian_elephant", "Chota (Calf)", "calf", 0.60, "boundary_averse", Point(46, 52), False),

            # 2. CHITAL / SPOTTED DEER (18)
            ("chital_deer", "Chital Stag Alpha", "alpha_male", 1.18, "cautious_sentinel", Point(25, 45), True),
            ("chital_deer", "Chital Stag 02", "alpha_male", 1.12, "grazing_herbivore", Point(28, 48), False),
            ("chital_deer", "Chital Stag Prober", "alpha_male", 1.15, "boundary_prober", Point(78, 85), False),
            ("chital_deer", "Chital Hind 01", "adult_female", 1.00, "grazing_herbivore", Point(22, 42), False),
            ("chital_deer", "Chital Hind 02", "adult_female", 0.98, "grazing_herbivore", Point(26, 44), False),
            ("chital_deer", "Chital Hind 03", "adult_female", 1.02, "grazing_herbivore", Point(30, 46), False),
            ("chital_deer", "Chital Hind 04", "adult_female", 0.95, "grazing_herbivore", Point(24, 50), False),
            ("chital_deer", "Chital Fawn 01", "calf", 0.58, "boundary_averse", Point(25, 43), False),
            ("chital_deer", "Chital Fawn 02", "calf", 0.55, "boundary_averse", Point(27, 45), False),
            # North Herd
            ("chital_deer", "Chital Stag North", "alpha_male", 1.16, "cautious_sentinel", Point(35, 160), True),
            ("chital_deer", "Chital Hind 05", "adult_female", 1.00, "grazing_herbivore", Point(38, 162), False),
            ("chital_deer", "Chital Hind 06", "adult_female", 0.96, "grazing_herbivore", Point(32, 158), False),
            ("chital_deer", "Chital Hind 07", "adult_female", 1.04, "pond_drinker", Point(68, 145), False),
            ("chital_deer", "Chital Hind 08", "adult_female", 0.97, "grazing_herbivore", Point(36, 165), False),
            ("chital_deer", "Chital Hind 09", "adult_female", 1.01, "grazing_herbivore", Point(40, 160), False),
            ("chital_deer", "Chital Fawn 03", "calf", 0.60, "boundary_averse", Point(37, 161), False),
            ("chital_deer", "Chital Fawn 04", "calf", 0.57, "boundary_averse", Point(34, 159), False),
            ("chital_deer", "Chital Yearling 01", "sub_adult", 0.82, "grazing_herbivore", Point(42, 164), False),

            # 3. SAMBAR DEER (8)
            ("sambar_deer", "Sambar Stag Prime", "alpha_male", 1.25, "cautious_sentinel", Point(20, 120), True),
            ("sambar_deer", "Sambar Stag 02", "alpha_male", 1.18, "canopy_browser", Point(24, 125), False),
            ("sambar_deer", "Sambar Cow 01", "adult_female", 1.02, "canopy_browser", Point(18, 118), False),
            ("sambar_deer", "Sambar Cow 02", "adult_female", 0.98, "canopy_browser", Point(22, 122), False),
            ("sambar_deer", "Sambar Cow 03", "adult_female", 1.00, "pond_drinker", Point(42, 65), False),
            ("sambar_deer", "Sambar Yearling", "sub_adult", 0.78, "boundary_averse", Point(21, 119), False),
            ("sambar_deer", "Sambar Fawn", "calf", 0.60, "boundary_averse", Point(19, 121), False),
            ("sambar_deer", "Sambar Solitary Prober", "alpha_male", 1.20, "boundary_prober", Point(84, 115), False),

            # 4. INDIAN WILD BOAR (12)
            ("wild_boar", "Old Razorback Boar", "alpha_male", 1.28, "boundary_prober", Point(75, 75), True),
            ("wild_boar", "Boar Scout 01", "sub_adult", 0.95, "boundary_prober", Point(82, 120), False),
            ("wild_boar", "Sow Matron 01", "adult_female", 1.05, "forager", Point(55, 85), False),
            ("wild_boar", "Sow Matron 02", "adult_female", 1.00, "forager", Point(52, 82), False),
            ("wild_boar", "Boar Sub-Adult 01", "sub_adult", 0.85, "forager", Point(58, 88), False),
            ("wild_boar", "Boar Sub-Adult 02", "sub_adult", 0.82, "forager", Point(50, 84), False),
            ("wild_boar", "Piglet 01", "calf", 0.52, "boundary_averse", Point(54, 83), False),
            ("wild_boar", "Piglet 02", "calf", 0.50, "boundary_averse", Point(56, 85), False),
            ("wild_boar", "Piglet 03", "calf", 0.53, "boundary_averse", Point(53, 86), False),
            ("wild_boar", "Piglet 04", "calf", 0.48, "boundary_averse", Point(55, 82), False),
            ("wild_boar", "Piglet 05", "calf", 0.51, "boundary_averse", Point(51, 85), False),
            ("wild_boar", "Piglet 06", "calf", 0.49, "boundary_averse", Point(57, 84), False),

            # 5. GAUR / INDIAN BISON (8)
            ("gaur_bison", "Titan Gaur Bull", "alpha_male", 1.35, "herd_matriarch", Point(30, 85), True),
            ("gaur_bison", "Gaur Cow 01", "adult_female", 1.08, "grazing_herbivore", Point(26, 82), False),
            ("gaur_bison", "Gaur Cow 02", "adult_female", 1.02, "grazing_herbivore", Point(32, 88), False),
            ("gaur_bison", "Gaur Cow 03", "adult_female", 1.05, "grazing_herbivore", Point(28, 90), False),
            ("gaur_bison", "Gaur Cow 04", "adult_female", 1.00, "pond_drinker", Point(68, 135), False),
            ("gaur_bison", "Gaur Calf 01", "calf", 0.65, "boundary_averse", Point(29, 84), False),
            ("gaur_bison", "Gaur Calf 02", "calf", 0.62, "boundary_averse", Point(31, 86), False),
            ("gaur_bison", "Gaur Scout Bull", "alpha_male", 1.22, "boundary_prober", Point(80, 72), False),

            # 6. BONNET MACAQUE (8)
            ("bonnet_macaque", "Macaque Alpha Scout", "alpha_male", 1.15, "canopy_browser", Point(65, 150), True),
            ("bonnet_macaque", "Macaque Forager 01", "adult_female", 0.98, "canopy_browser", Point(68, 152), False),
            ("bonnet_macaque", "Macaque Forager 02", "adult_female", 0.95, "canopy_browser", Point(64, 148), False),
            ("bonnet_macaque", "Macaque Forager 03", "adult_female", 1.00, "canopy_browser", Point(70, 155), False),
            ("bonnet_macaque", "Macaque Sub-Adult", "sub_adult", 0.80, "boundary_prober", Point(85, 102), False),
            ("bonnet_macaque", "Juvenile Macaque 01", "calf", 0.60, "boundary_averse", Point(66, 151), False),
            ("bonnet_macaque", "Juvenile Macaque 02", "calf", 0.58, "boundary_averse", Point(67, 149), False),
            ("bonnet_macaque", "Juvenile Macaque 03", "calf", 0.62, "boundary_averse", Point(69, 153), False),

            # 7. BENGAL TIGER (2)
            ("bengal_tiger", "Sher - Apex Male", "alpha_male", 1.15, "cautious_sentinel", Point(22, 110), True),
            ("bengal_tiger", "Maya - Tigress", "adult_female", 1.05, "boundary_prober", Point(82, 105), False),

            # 8. INDIAN LEOPARD (1)
            ("indian_leopard", "Shadow Stalker", "alpha_male", 1.00, "boundary_prober", Point(78, 130), True),

            # 9. SLOTH BEAR (1)
            ("sloth_bear", "Baloo - Old Forager", "alpha_male", 1.05, "forager", Point(48, 62), True),

            # 10. DHOLE / WILD DOG (2)
            ("dhole", "Dhole Pack Alpha", "alpha_male", 0.95, "cautious_sentinel", Point(30, 140), True),
            ("dhole", "Dhole Pack Beta", "sub_adult", 0.88, "forager", Point(33, 142), False),

            # 11. INDIAN MUNTJAC (1)
            ("indian_muntjac", "Barking Deer Buck", "alpha_male", 0.85, "boundary_averse", Point(28, 70), True),

            # 12. GOLDEN JACKAL (1)
            ("golden_jackal", "Tawny Jackal Scout", "alpha_male", 0.82, "forager", Point(42, 85), True),

            # 13. GRAY LANGUR (2)
            ("gray_langur", "Hanuman Troop Alpha", "alpha_male", 0.92, "canopy_browser", Point(52, 155), True),
            ("gray_langur", "Hanuman Canopy Leaper", "sub_adult", 0.82, "canopy_browser", Point(55, 158), False),

            # 14. INDIAN CRESTED PORCUPINE (1)
            ("crested_porcupine", "Crested Quill Rattler", "alpha_male", 0.80, "forager", Point(36, 75), True),

            # 15. INDIAN PEAFOWL (1)
            ("indian_peafowl", "Mayura - Crested Peacock", "alpha_male", 0.95, "forager", Point(44, 90), True),

            # 16. INDIAN HARE (1)
            ("indian_hare", "Black-Naped Hare Sprinter", "adult_female", 0.65, "boundary_averse", Point(24, 95), True),
        ]

        for i, (sp, name, demo, scale, role, pos, leader) in enumerate(individual_specs):
            aid = f"anim_{i+1:03d}"
            heading = self.rng.uniform(-math.pi, math.pi)
            speed = SPECIES_REGISTRY[sp].typical_speed_m_s * (0.85 + self.rng.random() * 0.3)
            vx = math.cos(heading) * speed
            vy = math.sin(heading) * speed

            agent = AutonomousAnimal(
                animal_id=aid,
                species=sp,
                group_id=f"{sp}_group",
                position=Point(min(self.boundary_x - 6.0, max(10.0, pos.x + self.rng.gauss(0, 1.8))), max(15.0, min(self.world_bounds[3] - 15.0, pos.y + self.rng.gauss(0, 1.8)))),
                velocity=Point(vx, vy),
                heading_rad=heading,
                speed_m_s=speed,
                name=name,
                demographic=demo,
                scale_factor=scale,
                role=role,
                is_leader=leader,
                state=BehaviorState.APPROACHING_BOUNDARY if role == "boundary_prober" and self.rng.random() < 0.4 else (
                    BehaviorState.GRAZING if demo != "alpha_male" else BehaviorState.WALKING
                ),
                hunger=0.2 + self.rng.random() * 0.4,
                thirst=0.2 + self.rng.random() * 0.3,
                fatigue=0.1 + self.rng.random() * 0.2
            )
            agent._update_current_task()
            agents.append(agent)

        return agents[:self.population_size]

    def step(self, dt: float = 0.5) -> Dict[str, Any]:
        self.time_s += dt

        for patch in self.resources:
            patch.step(dt)

        for agent in self.agents:
            agent.step(
                dt=dt,
                boundary=self.boundary,
                all_agents=self.agents,
                resources=self.resources,
                corridors=[],
                rng=self.rng,
                world_bounds=self.world_bounds
            )
            agent.set_crossing_time(self.time_s)

        return [a.to_dict() for a in self.agents]

    def inject_event(self, animal_id: str, intent: str) -> bool:
        return self.inject_intent(animal_id, intent)

    def inject_intent(self, animal_id: str, intent: str) -> bool:
        for a in self.agents:
            if a.animal_id == animal_id:
                a.manual_intent = intent
                if intent == "approach":
                    a.state = BehaviorState.APPROACHING_BOUNDARY
                elif intent == "turn_away":
                    a.state = BehaviorState.TURNING_AWAY
                elif intent == "cross":
                    a.state = BehaviorState.CROSSING_BOUNDARY
                a.state_timer_s = 0.0
                a._update_current_task()
                return True
        return False

    def reset(self) -> None:
        self.time_s = 0.0
        self.agents = self._spawn_population()
        self.resources = self._init_resources()
