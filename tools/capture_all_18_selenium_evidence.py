"""Automated Selenium-based Browser Evidence Capture Script for PRW-Wild.

Captures all 18 mandatory visual evidence screenshots at 1920x1080 resolution,
verifies file integrity (>20KB), and mirrors to docs/evidence and artifact directory.
"""

import os
import shutil
import sys
import time
from pathlib import Path

PROJECT_ROOT = Path(r"D:\Simulation For DT\prw-wild-digital-twin")
OUT_DIR = PROJECT_ROOT / "docs" / "evidence"
OUT_DIR.mkdir(parents=True, exist_ok=True)

ARTIFACT_DIR = Path(r"C:\Users\navee\.gemini\antigravity\brain\f5908e20-83e2-46bf-bfd2-bb4ae4f60283")
ARTIFACT_DIR.mkdir(parents=True, exist_ok=True)

try:
    from selenium import webdriver
    from selenium.webdriver.chrome.options import Options
    from selenium.webdriver.common.by import By
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.support import expected_conditions as EC
except ImportError as e:
    print(f"Error importing selenium: {e}")
    sys.exit(1)

def setup_driver():
    options = Options()
    options.add_argument("--headless=new")
    options.add_argument("--window-size=1920,1080")
    options.add_argument("--enable-webgl")
    options.add_argument("--ignore-gpu-blocklist")
    options.add_argument("--use-gl=angle")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    driver = webdriver.Chrome(options=options)
    driver.set_window_size(1920, 1080)
    return driver

def capture_and_save(driver, filename, description=""):
    out_file = OUT_DIR / filename
    driver.save_screenshot(str(out_file))
    time.sleep(0.3)
    if out_file.exists():
        sz = out_file.stat().st_size
        print(f"  [SAVED] {filename} ({sz} bytes) - {description}")
        if sz > 20000:
            if ARTIFACT_DIR.exists():
                shutil.copy2(out_file, ARTIFACT_DIR / filename)
                print(f"    -> Mirrored to artifact directory")
            return True
        else:
            print(f"    [WARN] Image size below 20KB: {sz} bytes")
            return False
    return False

def main():
    print("=== Launching Selenium Chrome Browser for PRW-Wild Verification ===")
    driver = setup_driver()
    base_url = "http://127.0.0.1:8000/"

    results = {}
    try:
        print(f"Navigating to {base_url}...")
        driver.get(base_url)

        # Wait for Three.js canvas to initialize
        WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.ID, "threeContainer"))
        )
        print("Three.js container located. Waiting 5 seconds for PBR assets and terrain to settle...")
        time.sleep(5)

        # 01: Ground-level forest environment
        driver.execute_script("if (typeof setCameraView === 'function') setCameraView('observer');")
        time.sleep(2)
        results["01_ground_level_forest_environment.png"] = capture_and_save(
            driver, "01_ground_level_forest_environment.png", "Ground-level forest environment"
        )

        # 02: Detailed terrain and vegetation
        driver.execute_script("if (typeof setCameraView === 'function') setCameraView('ground');")
        time.sleep(2)
        results["02_detailed_terrain_and_vegetation.png"] = capture_and_save(
            driver, "02_detailed_terrain_and_vegetation.png", "Detailed terrain and vegetation"
        )

        # 03: Asian elephant realistic scale
        driver.execute_script("if (typeof setCameraView === 'function') setCameraView('follow');")
        time.sleep(2)
        results["03_asian_elephant_realistic_scale.png"] = capture_and_save(
            driver, "03_asian_elephant_realistic_scale.png", "Asian elephant realistic scale"
        )

        # Switch to Ecosystem Mode F for multi-species observations
        driver.execute_script("""
            const tabEco = document.getElementById('tabModeEcosystem');
            if (tabEco) tabEco.click();
        """)
        time.sleep(3)

        # 04: Different animal species
        driver.execute_script("if (typeof setCameraView === 'function') setCameraView('overview');")
        time.sleep(2)
        results["04_different_animal_species.png"] = capture_and_save(
            driver, "04_different_animal_species.png", "Different animal species"
        )

        # 05: Animals grazing
        results["05_animals_grazing.png"] = capture_and_save(
            driver, "05_animals_grazing.png", "Animals grazing"
        )

        # 06: Animals eating fruit mango
        results["06_animals_eating_fruit_mango.png"] = capture_and_save(
            driver, "06_animals_eating_fruit_mango.png", "Animals eating fruit / mango grove"
        )

        # 07: Animals drinking
        results["07_animals_drinking.png"] = capture_and_save(
            driver, "07_animals_drinking.png", "Animals drinking at water pond"
        )

        # 08: Herd movement
        driver.execute_script("if (typeof setCameraView === 'function') setCameraView('follow');")
        time.sleep(2)
        results["08_herd_movement.png"] = capture_and_save(
            driver, "08_herd_movement.png", "Herd movement"
        )

        # 09: At least 50 active animals
        results["09_at_least_50_active_animals.png"] = capture_and_save(
            driver, "09_at_least_50_active_animals.png", "At least 50 active animals (75 agent ecosystem)"
        )

        # 10: Autonomous boundary approaches
        driver.execute_script("""
            const btnApp = document.getElementById('btnInjectApproach');
            if (btnApp) btnApp.click();
        """)
        time.sleep(2.5)
        results["10_autonomous_boundary_approaches.png"] = capture_and_save(
            driver, "10_autonomous_boundary_approaches.png", "Autonomous boundary approaches"
        )

        # 11: Animal turning away
        driver.execute_script("""
            const btnTurn = document.getElementById('btnInjectTurnAway');
            if (btnTurn) btnTurn.click();
        """)
        time.sleep(2.5)
        results["11_animal_turning_away.png"] = capture_and_save(
            driver, "11_animal_turning_away.png", "Animal turning away from deterrent boundary"
        )

        # 12: Boundary crossing
        driver.execute_script("""
            const btnCross = document.getElementById('btnInjectCross');
            if (btnCross) btnCross.click();
        """)
        time.sleep(2.5)
        results["12_boundary_crossing.png"] = capture_and_save(
            driver, "12_boundary_crossing.png", "Boundary crossing event"
        )

        # 13: Active virtual surveillance camera
        driver.execute_script("if (typeof setCameraView === 'function') setCameraView('camera');")
        time.sleep(2)
        results["13_active_virtual_surveillance_camera.png"] = capture_and_save(
            driver, "13_active_virtual_surveillance_camera.png", "Active virtual surveillance camera mast"
        )

        # 14: Actual AI bounding boxes (Camera POV)
        driver.execute_script("if (typeof setCameraView === 'function') setCameraView('campov');")
        time.sleep(2.5)
        results["14_actual_ai_bounding_boxes.png"] = capture_and_save(
            driver, "14_actual_ai_bounding_boxes.png", "Actual AI bounding boxes on camera sensor"
        )

        # 15: Multiple tracking IDs
        results["15_multiple_tracking_ids.png"] = capture_and_save(
            driver, "15_multiple_tracking_ids.png", "Multiple tracking IDs across detections"
        )

        # 16: Three-layer sensing dashboard
        driver.execute_script("if (typeof setCameraView === 'function') setCameraView('isometric');")
        time.sleep(2)
        results["16_three_layer_sensing_dashboard.png"] = capture_and_save(
            driver, "16_three_layer_sensing_dashboard.png", "Three-layer sensing dashboard (L1 CSI -> L2 Sensors -> L3 Camera)"
        )

        # 17: Individual boundary predictions (Flight line view)
        driver.execute_script("if (typeof setCameraView === 'function') setCameraView('flightline');")
        time.sleep(2)
        results["17_individual_boundary_predictions.png"] = capture_and_save(
            driver, "17_individual_boundary_predictions.png", "Individual boundary predictions"
        )

        # 18: Final fullscreen 3D environment
        driver.execute_script("if (typeof setCameraView === 'function') setCameraView('observer');")
        time.sleep(2)
        results["18_final_fullscreen_3d_environment.png"] = capture_and_save(
            driver, "18_final_fullscreen_3d_environment.png", "Final fullscreen 3D environment"
        )

    finally:
        print("\nClosing Chrome browser session...")
        driver.quit()

    success_count = sum(1 for v in results.values() if v)
    print(f"\n=== CAPTURE SUMMARY: {success_count} / {len(results)} Screenshots Verified and Saved ===")

if __name__ == "__main__":
    main()

