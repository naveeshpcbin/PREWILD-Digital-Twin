with open('src/prw_wild/ecosystem.py', 'r', encoding='utf-8') as f:
    text = f.read()

target = """        return {
            "time_s": round(self.time_s, 2),
            "population_count": len(self.agents),
            "agents": [a.to_dict() for a in self.agents],
            "resources": [
                {
                    "patch_id": r.patch_id,
                    "type": r.resource_type,
                    "current": round(r.current_amount, 1),
                    "capacity": r.max_capacity,
                    "pct": round((r.current_amount / r.max_capacity) * 100.0, 1)
                }
                for r in self.resources
            ],
            "boundary_status": {
                "approaching_count": sum(1 for a in self.agents if a.state == BehaviorState.APPROACHING_BOUNDARY),
                "turning_away_count": sum(1 for a in self.agents if a.state == BehaviorState.TURNING_AWAY),
                "crossed_count": sum(1 for a in self.agents if a.crossed_boundary),
            }
        }"""

replacement = """        return [a.to_dict() for a in self.agents]"""

assert target in text, "target not found"
text = text.replace(target, replacement, 1)

with open('src/prw_wild/ecosystem.py', 'w', encoding='utf-8') as f:
    f.write(text)

print("step(dt) return value successfully updated!")

