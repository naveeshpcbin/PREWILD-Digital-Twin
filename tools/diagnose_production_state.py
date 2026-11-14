import json
import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By

options = Options()
options.add_argument("--headless=new")
options.add_argument("--window-size=1920,1080")
options.add_argument("--enable-webgl")
options.add_argument("--use-gl=angle")
options.set_capability("goog:loggingPrefs", {"browser": "ALL"})

driver = webdriver.Chrome(options=options)
try:
    print("Navigating to http://127.0.0.1:8000/ ...")
    driver.get("http://127.0.0.1:8000/")
    time.sleep(4)

    logs = driver.get_log("browser")
    print(f"\n--- BROWSER CONSOLE LOGS ({len(logs)} entries) ---")
    for log in logs:
        print(f"[{log['level']}] {log['message']}")

    # Inspect window variables and Three.js state
    status_diag = driver.execute_script("""
        return {
            hasThree: typeof THREE !== 'undefined',
            threeVersion: typeof THREE !== 'undefined' ? THREE.REVISION : null,
            hasScene: typeof threeScene !== 'undefined' && threeScene !== null,
            sceneChildrenCount: (typeof threeScene !== 'undefined' && threeScene) ? threeScene.children.length : 0,
            sceneChildrenNames: (typeof threeScene !== 'undefined' && threeScene) ? threeScene.children.map(c => c.name || c.type) : [],
            activeMode: typeof currentMode !== 'undefined' ? currentMode : null,
            multiAnimalPopulationCount: typeof multiAnimalPopulation !== 'undefined' ? multiAnimalPopulation.length : 0,
            multiAnimalMeshesCount: typeof multiAnimalMeshes !== 'undefined' ? Object.keys(multiAnimalMeshes).length : 0,
            elephantMeshLoaded: typeof threeObjects !== 'undefined' && !!threeObjects.elephantMesh,
            groundMeshLoaded: typeof threeObjects !== 'undefined' && !!threeObjects.groundMesh,
            errorsOnWindow: window.__appErrors || []
        };
    """)
    print("\n--- RUNTIME DIAGNOSTIC STATE ---")
    print(json.dumps(status_diag, indent=2))

    # Take screenshot of current state
    driver.save_screenshot("docs/evidence/diagnose_recovery_state.png")
    print("\nSaved diagnostics screenshot to docs/evidence/diagnose_recovery_state.png")

finally:
    driver.quit()

