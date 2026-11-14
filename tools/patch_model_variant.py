import re

with open("src/prw_wild/ecosystem.py", "r", encoding="utf-8") as f:
    content = f.read()

# Normalize line endings for replacement
c = content.replace("\r\n", "\n")

target1 = """    state: BehaviorState = BehaviorState.WALKING
    state_timer_s: float = 0.0

    # Internal need drives [0.0 = satisfied, 1.0 = urgent need]"""

replacement1 = """    state: BehaviorState = BehaviorState.WALKING
    state_timer_s: float = 0.0
    model_variant: str = ""

    # Internal need drives [0.0 = satisfied, 1.0 = urgent need]"""

assert target1 in c, "target1 not found"
c = c.replace(target1, replacement1, 1)

target2 = """    # Manual test injection flag
    manual_intent: Optional[str] = None  # "approach", "turn_away", "cross"

    @property"""

replacement2 = """    # Manual test injection flag
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

    @property"""

assert target2 in c, "target2 not found"
c = c.replace(target2, replacement2, 1)

target3 = """            "animal_id": self.animal_id,
            "name": self.name,
            "species": self.species,"""

replacement3 = """            "animal_id": self.animal_id,
            "name": self.name,
            "species": self.species,
            "model_variant": self.model_variant,"""

assert target3 in c, "target3 not found"
c = c.replace(target3, replacement3, 1)

with open("src/prw_wild/ecosystem.py", "w", encoding="utf-8") as f:
    f.write(c)

print("Successfully updated src/prw_wild/ecosystem.py with model_variant support.")

