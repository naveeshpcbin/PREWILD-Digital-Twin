import os

path = r"D:\Simulation For DT\prw-wild-digital-twin\src\prw_wild\ecosystem.py"
with open(path, "r", encoding="utf-8") as f:
    text = f.read()

# 1. Update SpeciesType
old_enum = """class SpeciesType(str, Enum):
    ASIAN_ELEPHANT = "asian_elephant"
    CHITAL_DEER = "chital_deer"
    SAMBAR_DEER = "sambar_deer"
    WILD_BOAR = "wild_boar"
    GAUR_BISON = "gaur_bison"
    BONNET_MACAQUE = "bonnet_macaque\""""

new_enum = """class SpeciesType(str, Enum):
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
    INDIAN_HARE = "indian_hare\""""

assert old_enum in text, "old_enum not found"
text = text.replace(old_enum, new_enum, 1)

# 2. Update SPECIES_REGISTRY
old_registry_tail = """    SpeciesType.BONNET_MACAQUE.value: SpeciesProfile(
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
}"""

new_registry_tail = """    SpeciesType.BONNET_MACAQUE.value: SpeciesProfile(
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
}"""

assert old_registry_tail in text, "old_registry_tail not found"
text = text.replace(old_registry_tail, new_registry_tail, 1)

# 3. Add 10 additional species specifications to individual_specs
old_specs_tail = """            ("bonnet_macaque", "Juvenile Macaque 02", "calf", 0.58, "boundary_averse", Point(67, 149), False),
            ("bonnet_macaque", "Juvenile Macaque 03", "calf", 0.62, "boundary_averse", Point(69, 153), False),
        ]"""

new_specs_tail = """            ("bonnet_macaque", "Juvenile Macaque 02", "calf", 0.58, "boundary_averse", Point(67, 149), False),
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
        ]"""

assert old_specs_tail in text, "old_specs_tail not found"
text = text.replace(old_specs_tail, new_specs_tail, 1)

with open(path, "w", encoding="utf-8") as f:
    f.write(text)

print("SUCCESS: Updated ecosystem.py with all 16 species")

