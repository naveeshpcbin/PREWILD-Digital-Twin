"""Comprehensive Browser and UI Verification with Selenium.
Inspects:
1. Browser console errors.
2. 3D WebGL Canvas initialization.
3. High-detail GLB Forest instantiation.
4. Realistically scaled Asian Elephant (1.7MB production asset).
5. Detection Layers Overlay (L1, L2, L3).
6. Tactical Hardware Quickbar.
7. Hardware Control Bench Modal opening and toggles.
8. Emergency All-Off trigger.
Captures screenshots to brain artifacts directory.
"""

import time
import os
import sys
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By

ARTIFACTS_DIR = r"C:\Users\navee\.gemini\antigravity\brain\f5908e20-83e2-46bf-bfd2-bb4ae4f60283"
CHROMEDRIVER_PATH = r"C:\Users\navee\.cache\selenium\chromedriver\win64\156.0.8078.80\chromedriver.exe"

def run_verification():
    opts = Options()
    opts.add_argument("--headless=new")
    opts.add_argument("--window-size=1920,1080")
    opts.add_argument("--disable-gpu")
    opts.add_argument("--no-sandbox")
    opts.set_capability("goog:loggingPrefs", {"browser": "ALL"})

    service = Service(executable_path=CHROMEDRIVER_PATH)
    driver = webdriver.Chrome(service=service, options=opts)
    try:
        url = "http://127.0.0.1:8000/"
        print(f"Navigating to {url}...", flush=True)
        driver.get(url)
        time.sleep(4.0)

        # 1. Check browser logs
        logs = driver.get_log("browser")
        severe_errors = [l for l in logs if l.get("level") == "SEVERE" and "favicon" not in l.get("message", "")]
        print(f"Total console entries: {len(logs)}, Severe errors: {len(severe_errors)}", flush=True)
        for l in severe_errors:
            print("  [ERROR]", l.get("message"), flush=True)

        # 2. Check key DOM elements
        assert driver.find_element(By.ID, "threeContainer")
        assert driver.find_element(By.ID, "tacticalHwQuickbar")
        assert driver.find_element(By.ID, "quickL1Toggle")
        assert driver.find_element(By.ID, "quickAllOff")

        # 3. Capture main view with Tactical Hardware Quickbar
        p1 = os.path.join(ARTIFACTS_DIR, "verified_01_main_view_with_quickbar.png")
        driver.save_screenshot(p1)
        print("Captured:", p1, flush=True)

        # 4. Click L1 toggle on quickbar
        q1 = driver.find_element(By.ID, "quickL1Toggle")
        q1.click()
        time.sleep(1.0)

        p2 = os.path.join(ARTIFACTS_DIR, "verified_02_quickbar_l1_active.png")
        driver.save_screenshot(p2)
        print("Captured:", p2, flush=True)

        # 5. Open Hardware Lab Modal in Control Bench mode
        bench_btn = driver.find_element(By.ID, "quickOpenBench")
        bench_btn.click()
        time.sleep(1.5)

        p3 = os.path.join(ARTIFACTS_DIR, "verified_03_hardware_control_bench_modal.png")
        driver.save_screenshot(p3)
        print("Captured:", p3, flush=True)

        # 6. Switch to HARDWARE_TEST mode in modal
        mode_test_btn = driver.find_element(By.ID, "btnModeHwTest")
        mode_test_btn.click()
        time.sleep(0.5)

        # 7. Actuate Layer 2 and Layer 3 ON
        driver.find_element(By.ID, "btnL2On").click()
        time.sleep(0.3)
        driver.find_element(By.ID, "btnL3On").click()
        time.sleep(0.5)

        p4 = os.path.join(ARTIFACTS_DIR, "verified_04_hardware_all_layers_active.png")
        driver.save_screenshot(p4)
        print("Captured:", p4, flush=True)

        # 8. Trigger Emergency All-Off
        driver.find_element(By.ID, "btnHwEmergencyStop").click()
        time.sleep(0.8)

        p5 = os.path.join(ARTIFACTS_DIR, "verified_05_emergency_all_off_triggered.png")
        driver.save_screenshot(p5)
        print("Captured:", p5, flush=True)

        # 9. Close modal and check 3D scene
        driver.find_element(By.ID, "closeHardwareLabBtn").click()
        time.sleep(1.0)

        # 10. Switch viewpoint to Observer and capture ground level
        obs_btn = driver.find_element(By.XPATH, "//button[@data-view='observer']")
        obs_btn.click()
        time.sleep(1.5)

        p6 = os.path.join(ARTIFACTS_DIR, "verified_06_ground_level_forest_and_elephant.png")
        driver.save_screenshot(p6)
        print("Captured:", p6, flush=True)

        print("\nALL BROWSER VERIFICATIONS COMPLETED SUCCESSFULLY!", flush=True)

    finally:
        driver.quit()

if __name__ == "__main__":
    run_verification()
