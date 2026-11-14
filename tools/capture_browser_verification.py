"""Automated Browser Inspection and Screenshot Verification Script for PRW-Wild.

Uses Selenium to automate Google Chrome, inspect the running production digital twin,
execute interactions across all simulation modes, and capture evidence screenshots.
"""

import os
import sys
import time
from pathlib import Path

def run_browser_verification():
    try:
        from selenium import webdriver
        from selenium.webdriver.chrome.options import Options
        from selenium.webdriver.chrome.service import Service
        from selenium.webdriver.common.by import By
        from selenium.webdriver.support.ui import WebDriverWait
        from selenium.webdriver.support import expected_conditions as EC
    except ImportError as e:
        print(f"Selenium import error: {e}")
        return False

    out_dir = Path("docs/evidence")
    out_dir.mkdir(parents=True, exist_ok=True)

    chrome_options = Options()
    chrome_options.add_argument("--headless=new")
    chrome_options.add_argument("--window-size=1920,1080")
    chrome_options.add_argument("--disable-gpu-rasterization")
    chrome_options.add_argument("--enable-webgl")
    chrome_options.add_argument("--ignore-certificate-errors")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.set_capability("goog:loggingPrefs", {"browser": "ALL"})

    print("[Verification] Launching Chrome driver...")
    driver = webdriver.Chrome(options=chrome_options)
    driver.set_window_size(1920, 1080)

    try:
        url = "http://127.0.0.1:8000/"
        print(f"[Verification] Navigating to {url}...")
        driver.get(url)

        # Wait for app container to load
        WebDriverWait(driver, 15).until(
            EC.presence_of_element_located((By.ID, "threeContainer"))
        )
        print("[Verification] WebGL Three.js container found. Allowing 4 seconds for asset rendering...")
        time.sleep(4)

        # 1. Main World Overview
        path_overview = out_dir / "01_main_world_overview.png"
        driver.save_screenshot(str(path_overview))
        print(f"[Verification] Saved {path_overview} ({path_overview.stat().st_size} bytes)")

        # 2. Switch to Mode F: Multi-Animal Ecosystem
        tab_eco = driver.find_element(By.ID, "tabModeEcosystem")
        if tab_eco:
            tab_eco.click()
            time.sleep(2)
            path_eco = out_dir / "02_mode_f_ecosystem_intelligence.png"
            driver.save_screenshot(str(path_eco))
            print(f"[Verification] Saved {path_eco} ({path_eco.stat().st_size} bytes)")

        # 3. Test Camera POV Viewpoint and Live AI Detection Overlay
        btn_campov = driver.find_element(By.CSS_SELECTOR, "button[data-view='campov']")
        if btn_campov:
            btn_campov.click()
            time.sleep(2)
            path_cam = out_dir / "03_camera_ai_detection_overlay.png"
            driver.save_screenshot(str(path_cam))
            print(f"[Verification] Saved {path_cam} ({path_cam.stat().st_size} bytes)")

        # 4. Trigger Manual Event Injection: Force Approach & Warning
        btn_approach = driver.find_element(By.ID, "btnInjectApproach")
        if btn_approach:
            btn_approach.click()
            print("[Verification] Clicked Inject Approach button. Waiting 3 seconds for trajectory update...")
            time.sleep(3)
            path_approach = out_dir / "04_boundary_approach_trajectory.png"
            driver.save_screenshot(str(path_approach))
            print(f"[Verification] Saved {path_approach} ({path_approach.stat().st_size} bytes)")

        # 5. Switch to Mode E: Hardware Lab (Regression verification)
        tab_hw = driver.find_element(By.ID, "tabModeHardware")
        if tab_hw:
            tab_hw.click()
            time.sleep(2)
            path_hw = out_dir / "05_mode_e_hardware_lab_verified.png"
            driver.save_screenshot(str(path_hw))
            print(f"[Verification] Saved {path_hw} ({path_hw.stat().st_size} bytes)")

        # 6. Switch to 2D Spatial Radar Fallback
        btn_2d = driver.find_element(By.ID, "btnView2D")
        if btn_2d:
            btn_2d.click()
            time.sleep(1.5)
            path_2d = out_dir / "06_2d_spatial_radar_multi_animal.png"
            driver.save_screenshot(str(path_2d))
            print(f"[Verification] Saved {path_2d} ({path_2d.stat().st_size} bytes)")

        # Check console logs for errors
        logs = driver.get_log("browser")
        severe_errors = [l for l in logs if l.get("level") == "SEVERE"]
        print(f"[Verification] Browser console log count: {len(logs)}, Severe errors: {len(severe_errors)}")
        if severe_errors:
            for err in severe_errors[:5]:
                print(f"  [Console Error]: {err.get('message')}")

        return True
    except Exception as e:
        print(f"[Verification Error] {e}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        driver.quit()

if __name__ == "__main__":
    success = run_browser_verification()
    sys.exit(0 if success else 1)

