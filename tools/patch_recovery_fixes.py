import re

app_path = r"D:\Simulation For DT\prw-wild-digital-twin\src\prw_wild\web\static\app.js"
with open(app_path, "r", encoding="utf-8") as f:
    text = f.read()

# 1. Add global declarations for multiAnimalPopulation and speciesGlbTemplates
target1 = "  let counterfactualCache = null;"
replacement1 = """  let counterfactualCache = null;

  // Multi-Animal Ecosystem Global Cache (Fixed Scope)
  let multiAnimalPopulation = [];
  let speciesGlbTemplates = {};"""

assert target1 in text, "target1 not found"
text = text.replace(target1, replacement1, 1)

# 2. Fix lines 2392-2415 null reference on fenceRibbon
target2 = """    if (isBreach) {
      threeObjects.fenceBoundaryLine.material.color.setHex(0xef4444);
      threeObjects.fenceRibbon.material.color.setHex(0xef4444);
      threeObjects.fenceRibbon.material.opacity = 0.35 + Math.sin(t * 8) * 0.15;
      threeObjects.fenceBreachLights.forEach(l => l.material.color.setHex(0xef4444));

      alarmManager.startBreachSiren();
      document.getElementById('breachCriticalBanner')?.classList.remove('hidden');
    } else if (isWarning || isWatch) {
      threeObjects.fenceBoundaryLine.material.color.setHex(0xf59e0b);
      threeObjects.fenceRibbon.material.color.setHex(0xf59e0b);
      threeObjects.fenceRibbon.material.opacity = 0.18;
      threeObjects.fenceBreachLights.forEach(l => l.material.color.setHex(0xf59e0b));

      if (isWarning) alarmManager.playApproachChime();
      document.getElementById('breachCriticalBanner')?.classList.add('hidden');
    } else {
      threeObjects.fenceBoundaryLine.material.color.setHex(0x10b981);
      threeObjects.fenceRibbon.material.color.setHex(0x10b981);
      threeObjects.fenceRibbon.material.opacity = 0.08;
      threeObjects.fenceBreachLights.forEach(l => l.material.color.setHex(0x10b981));
      document.getElementById('breachCriticalBanner')?.classList.add('hidden');
    }"""

replacement2 = """    if (isBreach) {
      if (threeObjects.fenceBoundaryLine && threeObjects.fenceBoundaryLine.material) {
        threeObjects.fenceBoundaryLine.material.color.setHex(0xef4444);
      }
      if (threeObjects.fenceRibbon && threeObjects.fenceRibbon.material) {
        threeObjects.fenceRibbon.material.color.setHex(0xef4444);
        threeObjects.fenceRibbon.material.opacity = 0.35 + Math.sin(t * 8) * 0.15;
      }
      if (Array.isArray(threeObjects.fenceBreachLights)) {
        threeObjects.fenceBreachLights.forEach(l => { if (l && l.material) l.material.color.setHex(0xef4444); });
      }

      alarmManager.startBreachSiren();
      document.getElementById('breachCriticalBanner')?.classList.remove('hidden');
    } else if (isWarning || isWatch) {
      if (threeObjects.fenceBoundaryLine && threeObjects.fenceBoundaryLine.material) {
        threeObjects.fenceBoundaryLine.material.color.setHex(0xf59e0b);
      }
      if (threeObjects.fenceRibbon && threeObjects.fenceRibbon.material) {
        threeObjects.fenceRibbon.material.color.setHex(0xf59e0b);
        threeObjects.fenceRibbon.material.opacity = 0.18;
      }
      if (Array.isArray(threeObjects.fenceBreachLights)) {
        threeObjects.fenceBreachLights.forEach(l => { if (l && l.material) l.material.color.setHex(0xf59e0b); });
      }

      if (isWarning) alarmManager.playApproachChime();
      document.getElementById('breachCriticalBanner')?.classList.add('hidden');
    } else {
      if (threeObjects.fenceBoundaryLine && threeObjects.fenceBoundaryLine.material) {
        threeObjects.fenceBoundaryLine.material.color.setHex(0x10b981);
      }
      if (threeObjects.fenceRibbon && threeObjects.fenceRibbon.material) {
        threeObjects.fenceRibbon.material.color.setHex(0x10b981);
        threeObjects.fenceRibbon.material.opacity = 0.08;
      }
      if (Array.isArray(threeObjects.fenceBreachLights)) {
        threeObjects.fenceBreachLights.forEach(l => { if (l && l.material) l.material.color.setHex(0x10b981); });
      }
      document.getElementById('breachCriticalBanner')?.classList.add('hidden');
    }"""

assert target2 in text, "target2 not found"
text = text.replace(target2, replacement2, 1)

# 3. Fix pondNorth / pondSouth undefined in initMultiAnimalEcosystem
target3 = """        // Hide primitive flat cylinder discs once sculpted basins are loaded
        pondNorth.visible = false;
        pondSouth.visible = false;
        console.log('[PRW-Wild] Loaded Blender Production Carved Pond Basins');"""

replacement3 = """        console.log('[PRW-Wild] Loaded Blender Production Carved Pond Basins');"""

assert target3 in text, "target3 not found"
text = text.replace(target3, replacement3, 1)

with open(app_path, "w", encoding="utf-8") as f:
    f.write(text)

print("SUCCESS: Recovery fixes applied to app.js")

