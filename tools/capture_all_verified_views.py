from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import time
import os

ARTIFACT_DIR = r"C:\Users\navee\.gemini\antigravity\brain\f5908e20-83e2-46bf-bfd2-bb4ae4f60283"
os.makedirs(ARTIFACT_DIR, exist_ok=True)

options = Options()
options.add_argument('--headless=new')
options.add_argument('--no-sandbox')
options.add_argument('--disable-gpu')
options.add_argument('--window-size=1920,1080')

driver = webdriver.Chrome(options=options)
try:
    print("Navigating to Digital Twin with cachebust...")
    driver.get('http://127.0.0.1:8000/?cachebust=' + str(time.time()))
    time.sleep(3)

    # Let simulation run to t ~ 15s
    print("Advancing simulation to t ~ 15s...")
    time.sleep(12)

    # 1. Orbit View
    driver.execute_script("if (typeof setCameraView === 'function') setCameraView('orbit');")
    time.sleep(1.5)
    orbit_path = os.path.join(ARTIFACT_DIR, "production_orbit_view.png")
    driver.save_screenshot(orbit_path)
    print(f"Saved: {orbit_path}")

    # 2. Observer Eye-Level View
    driver.execute_script("if (typeof setCameraView === 'function') setCameraView('observer');")
    time.sleep(1.5)
    obs_path = os.path.join(ARTIFACT_DIR, "production_observer_view.png")
    driver.save_screenshot(obs_path)
    print(f"Saved: {obs_path}")

    # 3. Follow Elephant View
    driver.execute_script("if (typeof setCameraView === 'function') setCameraView('follow');")
    time.sleep(1.5)
    follow_path = os.path.join(ARTIFACT_DIR, "production_follow_view.png")
    driver.save_screenshot(follow_path)
    print(f"Saved: {follow_path}")

    # 4. Isometric View
    driver.execute_script("if (typeof setCameraView === 'function') setCameraView('isometric');")
    time.sleep(1.5)
    iso_path = os.path.join(ARTIFACT_DIR, "production_isometric_view.png")
    driver.save_screenshot(iso_path)
    print(f"Saved: {iso_path}")

    # 5. Top-Down View
    driver.execute_script("if (typeof setCameraView === 'function') setCameraView('topdown');")
    time.sleep(1.5)
    top_path = os.path.join(ARTIFACT_DIR, "production_topdown_view.png")
    driver.save_screenshot(top_path)
    print(f"Saved: {top_path}")

    # 6. Mode E: Hardware Workbench
    driver.execute_script("""
        const btn = document.querySelector('[data-lab-mode=\"hardware\"]');
        if (btn) btn.click();
    """)
    time.sleep(2)
    hw_path = os.path.join(ARTIFACT_DIR, "production_hardware_lab_view.png")
    driver.save_screenshot(hw_path)
    print(f"Saved: {hw_path}")

    # Check for any console errors
    logs = driver.get_log('browser')
    severe = [l for l in logs if l['level'] == 'SEVERE']
    print(f"Browser SEVERE error count: {len(severe)}")
    for s in severe:
        print("  Error:", s['message'])

finally:
    driver.quit()

print("All production captures completed successfully!")

