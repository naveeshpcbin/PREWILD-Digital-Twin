import os
import time
from pathlib import Path
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

ARTIFACT_DIR = r"C:\Users\navee\.gemini\antigravity\brain\f5908e20-83e2-46bf-bfd2-bb4ae4f60283"
EVIDENCE_DIR = r"D:\Simulation For DT\prw-wild-digital-twin\docs\evidence"
os.makedirs(EVIDENCE_DIR, exist_ok=True)

chrome_options = Options()
chrome_options.add_argument("--headless=new")
chrome_options.add_argument("--window-size=1920,1080")
chrome_options.add_argument("--enable-webgl")
chrome_options.add_argument("--ignore-certificate-errors")
chrome_options.add_argument("--no-sandbox")

driver = webdriver.Chrome(options=chrome_options)
driver.set_window_size(1920, 1080)

print("Navigating to http://127.0.0.1:8000/ ...")
driver.get("http://127.0.0.1:8000/")
time.sleep(4.0)

# 1. Perspective View 1: Orbit / Forest Landscape View
p1_file = os.path.join(EVIDENCE_DIR, "refreshed_01_landscape_trees_lake.png")
p1_art = os.path.join(ARTIFACT_DIR, "refreshed_01_landscape_trees_lake.png")
driver.save_screenshot(p1_file)
driver.save_screenshot(p1_art)
print("Captured View 1:", p1_file)

# 2. Adjust Camera to close-up on the Asian Elephant
driver.execute_script("""
    if (window.threeCamera && window.threeControls) {
        // Find elephant
        const elephant = window.threeScene.getObjectByName('Elephant_Production_GLB') || 
                         window.threeScene.getObjectByName('Elephant_Visual_Child_Root');
        if (elephant) {
            const worldPos = new THREE.Vector3();
            elephant.getWorldPosition(worldPos);
            window.threeCamera.position.set(worldPos.x + 8, worldPos.y + 4.5, worldPos.z + 12);
            window.threeControls.target.copy(worldPos);
            window.threeControls.update();
        } else {
            window.threeCamera.position.set(45, 6, 85);
            window.threeControls.target.set(38, 2, 95);
            window.threeControls.update();
        }
    }
""")
time.sleep(2.0)
p2_file = os.path.join(EVIDENCE_DIR, "refreshed_02_elephant_texture_fidelity.png")
p2_art = os.path.join(ARTIFACT_DIR, "refreshed_02_elephant_texture_fidelity.png")
driver.save_screenshot(p2_file)
driver.save_screenshot(p2_art)
print("Captured View 2:", p2_file)

# 3. View 3: Ground-level Forest Corridor & Vegetation
driver.execute_script("""
    if (window.threeCamera && window.threeControls) {
        window.threeCamera.position.set(25, 4.0, 50);
        window.threeControls.target.set(50, 2.0, 95);
        window.threeControls.update();
    }
""")
time.sleep(2.0)
p3_file = os.path.join(EVIDENCE_DIR, "refreshed_03_forest_corridor_vegetation.png")
p3_art = os.path.join(ARTIFACT_DIR, "refreshed_03_forest_corridor_vegetation.png")
driver.save_screenshot(p3_file)
driver.save_screenshot(p3_art)
print("Captured View 3:", p3_file)

# 4. View 4: Farmland & Machan Watchtower
driver.execute_script("""
    if (window.threeCamera && window.threeControls) {
        window.threeCamera.position.set(105, 5.0, 95);
        window.threeControls.target.set(130, 4.0, 110);
        window.threeControls.update();
    }
""")
time.sleep(2.0)
p4_file = os.path.join(EVIDENCE_DIR, "refreshed_04_farmland_watchtower_machan.png")
p4_art = os.path.join(ARTIFACT_DIR, "refreshed_04_farmland_watchtower_machan.png")
driver.save_screenshot(p4_file)
driver.save_screenshot(p4_art)
print("Captured View 4:", p4_file)

driver.quit()
print("All refreshed evidence captured successfully!")

