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
    print("[1/4] Loading web dashboard...")
    driver.get("http://127.0.0.1:8000/")
    time.sleep(3.5)

    p_slider = driver.find_element(By.ID, "sidePiezoSlider")
    m_slider = driver.find_element(By.ID, "sideMicSlider")
    
    p_min = p_slider.get_attribute("min")
    p_max = p_slider.get_attribute("max")
    p_step = p_slider.get_attribute("step")
    
    m_min = m_slider.get_attribute("min")
    m_max = m_slider.get_attribute("max")
    m_step = m_slider.get_attribute("step")

    print(f"  Piezo Slider -> min={p_min}, max={p_max}, step={p_step}")
    print(f"  Mic Slider   -> min={m_min}, max={m_max}, step={m_step}")

    assert int(p_max) >= 4095, f"Expected Piezo max >= 4095, got {p_max}"
    assert int(m_max) >= 500000, f"Expected Mic max >= 500000, got {m_max}"

    print("[2/4] Testing setting Piezo threshold beyond sensor reading (e.g. 1500 ADC)...")
    driver.execute_script("""
        const p = document.getElementById('sidePiezoSlider');
        p.value = 1500;
        p.dispatchEvent(new Event('input'));
        p.dispatchEvent(new Event('change'));
    """)
    time.sleep(1.0)

    p_val = driver.find_element(By.ID, "sidePiezoThreshVal").text
    print(f"  DOM Piezo Threshold display: {p_val}")
    assert p_val == "1500", f"Expected 1500, got {p_val}"

    print("[3/4] Testing setting Mic threshold beyond sensor reading (e.g. 250,000 RMS)...")
    driver.execute_script("""
        const m = document.getElementById('sideMicSlider');
        m.value = 250000;
        m.dispatchEvent(new Event('input'));
        m.dispatchEvent(new Event('change'));
    """)
    time.sleep(1.5)

    m_val = driver.find_element(By.ID, "sideMicThreshVal").text
    print(f"  DOM Mic Threshold display: {m_val}")
    assert "250,000" in m_val, f"Expected 250,000, got {m_val}"

    print("[4/4] Capturing verified screenshots...")
    panel = driver.find_element(By.ID, "sidePhysicalHardwarePanel")
    out_panel = os.path.join(ARTIFACT_DIR, "hardware_panel_expanded_thresholds.png")
    panel.screenshot(out_panel)
    print(f"  Saved: {out_panel}")

    out_full = os.path.join(ARTIFACT_DIR, "full_dashboard_expanded_thresholds.png")
    driver.save_screenshot(out_full)
    print(f"  Saved: {out_full}")

    print("\n>>> EXPANDED THRESHOLDS VALIDATION COMPLETED 100% SUCCESSFULLY! <<<")

finally:
    driver.quit()
