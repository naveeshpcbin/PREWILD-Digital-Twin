import os
import time
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

driver.get("http://127.0.0.1:8000/")
time.sleep(4.0)

# 1. View: Free Orbit (shows the entire landscape from above)
driver.execute_script("if (typeof setCameraView === 'function') setCameraView('orbit');")
time.sleep(2.0)
orbit_art = os.path.join(ARTIFACT_DIR, "v1_free_orbit_view.png")
driver.save_screenshot(orbit_art)
print("Captured Orbit View:", orbit_art)

# 2. View: Follow Elephant (follows the Asian Elephant close-up)
driver.execute_script("if (typeof setCameraView === 'function') setCameraView('follow');")
time.sleep(2.0)
follow_art = os.path.join(ARTIFACT_DIR, "v2_follow_elephant_view.png")
driver.save_screenshot(follow_art)
print("Captured Follow View:", follow_art)

# 3. View: Observer Eye-Level (ground-level forest perspective)
driver.execute_script("if (typeof setCameraView === 'function') setCameraView('observer');")
time.sleep(2.0)
obs_art = os.path.join(ARTIFACT_DIR, "v3_observer_eye_level_view.png")
driver.save_screenshot(obs_art)
print("Captured Observer View:", obs_art)

# 4. View: Isometric View
driver.execute_script("if (typeof setCameraView === 'function') setCameraView('isometric');")
time.sleep(2.0)
iso_art = os.path.join(ARTIFACT_DIR, "v4_isometric_view.png")
driver.save_screenshot(iso_art)
print("Captured Isometric View:", iso_art)

driver.quit()
print("All 4 standard viewpoints captured successfully!")

