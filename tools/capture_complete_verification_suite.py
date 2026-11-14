"""Capture comprehensive verification suite for PRW-Wild Master Production Acceptance.
Generates high-res screenshots for:
- View 01: Master 3D Environment Orbit Overview (Western Ghats Reserve)
- View 02: Ground-Level Forest with High-Detail Trees and Grazing Wildlife
- View 03: Hero Asian Elephant Close-Up Inspection (Realistic PBR Hide & Scale)
- View 04: Three-Layer Sensing Ground Envelopes & Tactical Hardware Quickbar
- View 05: Hardware Control Workbench (Mode Switcher & Manual Toggles)
- View 06: Hardware Control Workbench (All Layers Active with Live Telemetry)
- View 07: Hardware Emergency All-Off Verification
- View 08: Optical Camera POV with AI Detection Bounding Box & Tracks
- View 09: Perimeter Fence Breach & Wi-Fi CSI Router Mast (WIFI_AP_01)
- View 10: Multi-Animal Autonomous AI Ecosystem Intelligence Directory
"""

import time
import os
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By

ARTIFACTS_DIR = r"C:\Users\navee\.gemini\antigravity\brain\f5908e20-83e2-46bf-bfd2-bb4ae4f60283"
CHROMEDRIVER_PATH = r"C:\Users\navee\.cache\selenium\chromedriver\win64\156.0.8078.80\chromedriver.exe"

def run_suite():
    opts = Options()
    opts.add_argument("--headless=new")
    opts.add_argument("--window-size=1920,1080")
    opts.add_argument("--disable-gpu")
    opts.add_argument("--no-sandbox")

    service = Service(executable_path=CHROMEDRIVER_PATH)
    driver = webdriver.Chrome(service=service, options=opts)
    try:
        url = "http://127.0.0.1:8000/"
        print(f"Connecting to {url}...", flush=True)
        driver.get(url)
        time.sleep(4.5)

        # View 01: Master Orbit Overview
        driver.find_element(By.XPATH, "//button[@data-view='orbit']").click()
        time.sleep(1.5)
        p1 = os.path.join(ARTIFACTS_DIR, "suite_01_master_orbit_overview.png")
        driver.save_screenshot(p1)
        print("Captured View 01:", p1, flush=True)

        # View 02: Ground-Level Observer
        driver.find_element(By.XPATH, "//button[@data-view='observer']").click()
        time.sleep(1.5)
        p2 = os.path.join(ARTIFACTS_DIR, "suite_02_ground_level_observer.png")
        driver.save_screenshot(p2)
        print("Captured View 02:", p2, flush=True)

        # View 03: Follow Elephant Hero Close-Up
        driver.find_element(By.XPATH, "//button[@data-view='follow']").click()
        time.sleep(1.8)
        p3 = os.path.join(ARTIFACTS_DIR, "suite_03_elephant_hero_inspection.png")
        driver.save_screenshot(p3)
        print("Captured View 03:", p3, flush=True)

        # View 04: Three-Layer Ground Envelopes & Tactical Quickbar Active
        # Click L1 toggle on quickbar to activate Layer 1
        driver.find_element(By.ID, "quickL1Toggle").click()
        time.sleep(0.5)
        driver.find_element(By.XPATH, "//button[@data-view='isometric']").click()
        time.sleep(1.5)
        p4 = os.path.join(ARTIFACTS_DIR, "suite_04_three_layer_ground_envelopes.png")
        driver.save_screenshot(p4)
        print("Captured View 04:", p4, flush=True)

        # View 05: Hardware Control Workbench Modal (HARDWARE TEST Mode)
        driver.find_element(By.ID, "quickOpenBench").click()
        time.sleep(1.2)
        driver.find_element(By.ID, "btnModeHwTest").click()
        time.sleep(0.5)
        p5 = os.path.join(ARTIFACTS_DIR, "suite_05_hardware_workbench_bench_test_mode.png")
        driver.save_screenshot(p5)
        print("Captured View 05:", p5, flush=True)

        # View 06: Hardware Control Workbench with All 3 Layers Active & Telemetry
        driver.find_element(By.ID, "btnL1On").click()
        time.sleep(0.3)
        driver.find_element(By.ID, "btnL2On").click()
        time.sleep(0.3)
        driver.find_element(By.ID, "btnL3On").click()
        time.sleep(0.5)
        p6 = os.path.join(ARTIFACTS_DIR, "suite_06_hardware_all_layers_active_telemetry.png")
        driver.save_screenshot(p6)
        print("Captured View 06:", p6, flush=True)

        # View 07: Emergency All-Off Execution
        driver.find_element(By.ID, "btnHwEmergencyStop").click()
        time.sleep(0.8)
        p7 = os.path.join(ARTIFACTS_DIR, "suite_07_emergency_all_off_executed.png")
        driver.save_screenshot(p7)
        print("Captured View 07:", p7, flush=True)

        # Close Modal
        driver.find_element(By.ID, "closeHardwareLabBtn").click()
        time.sleep(1.0)

        # View 08: Camera POV Optical Viewfinder
        driver.find_element(By.XPATH, "//button[@data-view='campov']").click()
        time.sleep(1.8)
        p8 = os.path.join(ARTIFACTS_DIR, "suite_08_camera_pov_optical_viewfinder.png")
        driver.save_screenshot(p8)
        print("Captured View 08:", p8, flush=True)

        # View 09: Wi-Fi Router Mast (WIFI_AP_01)
        driver.find_element(By.XPATH, "//button[@data-view='router']").click()
        time.sleep(1.5)
        p9 = os.path.join(ARTIFACTS_DIR, "suite_09_wifi_ap_01_router_mast.png")
        driver.save_screenshot(p9)
        print("Captured View 09:", p9, flush=True)

        # View 10: Multi-Animal Autonomous AI Ecosystem Intelligence Tab
        driver.find_element(By.ID, "tabModeEcosystem").click()
        time.sleep(1.8)
        p10 = os.path.join(ARTIFACTS_DIR, "suite_10_multi_animal_ecosystem_command.png")
        driver.save_screenshot(p10)
        print("Captured View 10:", p10, flush=True)

        print("\nALL 10 PRODUCTION VERIFICATION SUITE SCREENSHOTS CAPTURED SUCCESSFULLY!", flush=True)

    finally:
        driver.quit()

if __name__ == "__main__":
    run_suite()

