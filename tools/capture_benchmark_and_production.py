"""Capture benchmark views and master production verification screenshots.
Saves to both docs/evidence and the agent artifacts directory.
"""
import os
import shutil
import time
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By

ARTIFACTS_DIR = r"C:\Users\navee\.gemini\antigravity\brain\f5908e20-83e2-46bf-bfd2-bb4ae4f60283"
DOCS_EVIDENCE_DIR = r"D:\Simulation For DT\prw-wild-digital-twin\docs\evidence"
CHROMEDRIVER_PATH = r"C:\Users\navee\.cache\selenium\chromedriver\win64\156.0.8078.80\chromedriver.exe"

os.makedirs(DOCS_EVIDENCE_DIR, exist_ok=True)

def save_and_copy(driver, filename):
    p_art = os.path.join(ARTIFACTS_DIR, filename)
    p_ev = os.path.join(DOCS_EVIDENCE_DIR, filename)
    driver.save_screenshot(p_art)
    shutil.copy2(p_art, p_ev)
    print(f"[CAPTURED] {filename} -> {os.path.getsize(p_art)} bytes", flush=True)

def main():
    opts = Options()
    opts.add_argument("--headless=new")
    opts.add_argument("--window-size=1920,1080")
    opts.add_argument("--disable-gpu")
    opts.add_argument("--no-sandbox")

    service = Service(executable_path=CHROMEDRIVER_PATH)
    driver = webdriver.Chrome(service=service, options=opts)

    try:
        # =====================================================================
        # PART 1: STAGE 6 BENCHMARK VIEW (ELEPHANT & GAUR)
        # =====================================================================
        benchmark_url = "http://127.0.0.1:8000/benchmark_view.html"
        print(f"\n--- Loading Benchmark: {benchmark_url} ---", flush=True)
        driver.get(benchmark_url)
        time.sleep(3.5)

        # 1. Elephant 3/4 Hero View
        driver.find_element(By.ID, "btnFocusElephant").click()
        driver.find_element(By.ID, "btnCam34").click()
        time.sleep(1.2)
        save_and_copy(driver, "benchmark_01_elephant_three_quarter.png")

        # 2. Elephant Front View (Direct face & trunk)
        driver.find_element(By.ID, "btnCamFront").click()
        time.sleep(1.2)
        save_and_copy(driver, "benchmark_02_elephant_front_view.png")

        # 3. Elephant Side Profile (Locomotion & ground contact)
        driver.find_element(By.ID, "btnCamSide").click()
        time.sleep(1.2)
        save_and_copy(driver, "benchmark_03_elephant_side_profile.png")

        # 4. Elephant Rear View
        driver.find_element(By.ID, "btnCamRear").click()
        time.sleep(1.2)
        save_and_copy(driver, "benchmark_04_elephant_rear_view.png")

        # 5. Gaur Bull 3/4 Hero View
        driver.find_element(By.ID, "btnFocusGaur").click()
        driver.find_element(By.ID, "btnCam34").click()
        time.sleep(1.2)
        save_and_copy(driver, "benchmark_05_gaur_three_quarter.png")

        # 6. Gaur Bull Side Profile
        driver.find_element(By.ID, "btnCamSide").click()
        time.sleep(1.2)
        save_and_copy(driver, "benchmark_06_gaur_side_profile.png")

        # 7. Side-by-Side Dual Patrol View (Both Elephant & Gaur moving forward)
        driver.find_element(By.ID, "btnFocusBoth").click()
        driver.find_element(By.ID, "btnCam34").click()
        time.sleep(1.5)
        save_and_copy(driver, "benchmark_07_dual_species_patrol.png")

        # =====================================================================
        # PART 2: MAIN PRODUCTION ENVIRONMENT & MULTI-ANIMAL OVERHAUL
        # =====================================================================
        prod_url = "http://127.0.0.1:8000/"
        print(f"\n--- Loading Production: {prod_url} ---", flush=True)
        driver.get(prod_url)
        time.sleep(4.5)

        # 8. Master Orbit Overview (Zero Primitive Lollipop Trees)
        driver.find_element(By.XPATH, "//button[@data-view='orbit']").click()
        time.sleep(1.5)
        save_and_copy(driver, "production_01_orbit_forest_overhaul.png")

        # 9. Ground-Level Observer (Sal, Banyan, Acacia GLB foliage & terrain)
        driver.find_element(By.XPATH, "//button[@data-view='observer']").click()
        time.sleep(1.8)
        save_and_copy(driver, "production_02_observer_ground_fidelity.png")

        # 10. Elephant Hero Follow (Walking strictly forward along path)
        driver.find_element(By.XPATH, "//button[@data-view='follow']").click()
        time.sleep(2.0)
        save_and_copy(driver, "production_03_elephant_true_forward.png")

        # 11. Multi-Species Autonomous Ecosystem (16 Species, 75 agents)
        # Scroll directory or center camera on multi-animal population
        driver.find_element(By.XPATH, "//button[@data-view='orbit']").click()
        time.sleep(1.5)
        save_and_copy(driver, "production_04_multi_species_ecosystem.png")

        # 12. Hardware Control Modal & Quickbar (Three layers)
        driver.find_element(By.ID, "quickOpenBench").click()
        time.sleep(1.2)
        driver.find_element(By.ID, "btnHwModeControl").click()
        time.sleep(1.2)
        save_and_copy(driver, "production_05_hardware_control_bench.png")

        print("\nAll benchmark & production verification captures completed successfully!", flush=True)

    finally:
        driver.quit()

if __name__ == "__main__":
    main()
