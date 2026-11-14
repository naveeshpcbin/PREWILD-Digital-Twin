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

views = ['observer', 'orbit', 'isometric', 'topdown', 'follow']

for v in views:
    # Click button in UI
    driver.execute_script(f"""
        const btn = document.querySelector('button[data-view="{v}"]');
        if (btn) btn.click();
    """)
    time.sleep(2.0)
    art_path = os.path.join(ARTIFACT_DIR, f"final_ui_{v}_view.png")
    driver.save_screenshot(art_path)
    ev_path = os.path.join(EVIDENCE_DIR, f"final_ui_{v}_view.png")
    driver.save_screenshot(ev_path)
    print(f"Captured UI view '{v}' -> {art_path}")

driver.quit()
print("All UI views captured!")

