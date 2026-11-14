import os
import time
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By

CHROMEDRIVER_PATH = r"C:\Users\navee\.cache\selenium\chromedriver\win64\157.0.8103.38\chromedriver.exe"
ARTIFACT_DIR = r"C:\Users\navee\.gemini\antigravity\brain\f5908e20-83e2-46bf-bfd2-bb4ae4f60283"
os.makedirs(ARTIFACT_DIR, exist_ok=True)

service = Service(CHROMEDRIVER_PATH)
opts = Options()
opts.add_argument("--headless=new")
opts.add_argument("--window-size=1920,1080")
opts.add_argument("--enable-webgl")
opts.add_argument("--no-sandbox")

driver = webdriver.Chrome(service=service, options=opts)
driver.set_window_size(1920, 1080)

try:
    print("[1/5] Loading web dashboard at http://127.0.0.1:8000/...")
    driver.get("http://127.0.0.1:8000/")
    time.sleep(3.5)

    panel = driver.find_element(By.ID, "sidePhysicalHardwarePanel")

    # Step 1: Capture Active Baseline
    step1_panel = os.path.join(ARTIFACT_DIR, "step1_both_active_panel.png")
    step1_full = os.path.join(ARTIFACT_DIR, "step1_both_active_full.png")
    panel.screenshot(step1_panel)
    driver.save_screenshot(step1_full)
    print(f"  [OK] Saved Step 1 Active screenshots: {step1_panel}")

    btn_a = driver.find_element(By.ID, "toggleEsp32AMode")
    btn_b = driver.find_element(By.ID, "toggleEsp32BMode")

    init_a = btn_a.get_attribute("data-state")
    init_b = btn_b.get_attribute("data-state")
    print(f"  Initial State -> Node A: {init_a}, Node B: {init_b}")

    # Step 2: Click ESP32-A to OFF -> Must cascade Node B to OFF automatically
    print("[2/5] Clicking ESP32-A toggle to switch OFF...")
    btn_a.click()
    time.sleep(2.0)

    state_a = btn_a.get_attribute("data-state")
    txt_a = driver.find_element(By.ID, "txtEsp32AMode").text
    state_b = btn_b.get_attribute("data-state")
    txt_b = driver.find_element(By.ID, "txtEsp32BMode").text
    classes_b = btn_b.get_attribute("class")
    notice = driver.find_element(By.ID, "txtNodeCascadeNotice").text

    print(f"  Result -> Node A: {state_a} ({txt_a})")
    print(f"  Result -> Node B: {state_b} ({txt_b}) [CASCADED AUTOMATICALLY]")
    print(f"  Node B CSS Classes: {classes_b}")
    print(f"  Notice Banner: {notice}")

    assert state_a == "OFF", f"Expected Node A OFF, got {state_a}"
    assert state_b == "OFF", f"Expected Node B OFF (Cascaded), got {state_b}"
    assert "cascade-locked" in classes_b, f"Expected cascade-locked in Node B classes"

    step2_panel = os.path.join(ARTIFACT_DIR, "step2_cascaded_off_panel.png")
    step2_full = os.path.join(ARTIFACT_DIR, "step2_cascaded_off_full.png")
    panel.screenshot(step2_panel)
    driver.save_screenshot(step2_full)
    print(f"  [OK] Saved Step 2 Cascaded OFF screenshots: {step2_panel}")

    # Step 3: Attempt to turn Node B ON while Node A is OFF (MUST BE BLOCKED)
    print("[3/5] Attempting to click ESP32-B toggle while ESP32-A is OFF...")
    btn_b.click()
    time.sleep(1.0)
    blocked_b_state = btn_b.get_attribute("data-state")
    print(f"  Result -> Node B state remained: {blocked_b_state} (BLOCKED SUCCESSFULLY)")
    assert blocked_b_state == "OFF", f"Node B should remain OFF when A is OFF, got {blocked_b_state}"

    # Step 4: Turn Node A back ON
    print("[4/5] Clicking ESP32-A toggle to switch back ON...")
    btn_a.click()
    time.sleep(2.0)
    state_a_back = btn_a.get_attribute("data-state")
    print(f"  Result -> Node A: {state_a_back}")
    assert state_a_back == "ON", f"Expected Node A ON, got {state_a_back}"

    # Step 5: Turn Node B back ON
    print("[5/5] Clicking ESP32-B toggle to switch back ON...")
    btn_b.click()
    time.sleep(2.0)
    state_b_back = btn_b.get_attribute("data-state")
    print(f"  Result -> Node B: {state_b_back}")
    assert state_b_back == "ON", f"Expected Node B ON, got {state_b_back}"

    step3_panel = os.path.join(ARTIFACT_DIR, "step3_restored_active_panel.png")
    step3_full = os.path.join(ARTIFACT_DIR, "step3_restored_active_full.png")
    panel.screenshot(step3_panel)
    driver.save_screenshot(step3_full)
    print(f"  [OK] Saved Step 3 Restored Active screenshots: {step3_panel}")

    print("\n>>> ALL LIVE VERIFICATION CRITERIA PASSED WITH 100% SUCCESS! <<<")

finally:
    driver.quit()

