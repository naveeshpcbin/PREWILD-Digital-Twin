from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import time
import os

ARTIFACT_DIR = r"C:\Users\navee\.gemini\antigravity\brain\f5908e20-83e2-46bf-bfd2-bb4ae4f60283"

options = Options()
options.add_argument('--headless=new')
options.add_argument('--no-sandbox')
options.add_argument('--disable-gpu')
options.add_argument('--window-size=1920,1080')

driver = webdriver.Chrome(options=options)
try:
    driver.get('http://127.0.0.1:8000/?cachebust=' + str(time.time()))
    time.sleep(3)
    
    # Click Mode F tab
    driver.execute_script("""
        const btn = document.querySelector('[data-lab-mode=\"ecosystem\"]') || document.getElementById('tab-ecosystem');
        if (btn) btn.click();
    """)
    time.sleep(3)
    
    # Switch to Free Orbit or Top-down to see all animals
    driver.execute_script("""
        const btn = Array.from(document.querySelectorAll('.view-btn')).find(b => b.textContent.includes('Free Orbit') || b.textContent.includes('Isometric'));
        if (btn) btn.click();
    """)
    time.sleep(2)
    
    fp = os.path.join(ARTIFACT_DIR, "v6_mode_f_ecosystem.png")
    driver.save_screenshot(fp)
    print(f"Captured {fp}")
    
    logs = driver.get_log('browser')
    errors = [l for l in logs if l['level'] == 'SEVERE']
    print(f"Severe errors in Mode F: {len(errors)}")
    for e in errors:
        print("  Error:", e['message'])
finally:
    driver.quit()

