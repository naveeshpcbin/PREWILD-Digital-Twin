from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import time
import os

opts = Options()
opts.add_argument('--headless=new')
opts.add_argument('--window-size=1920,1080')
opts.add_argument('--disable-gpu')
driver = webdriver.Chrome(options=opts)
try:
    driver.get('http://127.0.0.1:8000/')
    time.sleep(5)

    logs = driver.get_log('browser')
    print("Browser console logs:")
    severe_count = 0
    for entry in logs:
        if entry['level'] in ['SEVERE', 'WARNING']:
            print(f"  [{entry['level']}] {entry['message']}")
        if entry['level'] == 'SEVERE':
            severe_count += 1
    print(f"Total SEVERE errors: {severe_count}")

    out_path = r"C:\Users\navee\.gemini\antigravity\brain\f5908e20-83e2-46bf-bfd2-bb4ae4f60283\current_live_render.png"
    driver.save_screenshot(out_path)
    print(f"Saved screenshot to {out_path}")

    # Also capture close up of elephant
    driver.execute_script("""
        if (window.threeCamera && window.threeObjects && window.threeObjects.elephantGroup) {
            const elPos = window.threeObjects.elephantGroup.position;
            window.threeCamera.position.set(elPos.x + 8, elPos.y + 4, elPos.z + 8);
            if (window.threeControls) {
                window.threeControls.target.copy(elPos);
                window.threeControls.update();
            }
        }
    """)
    time.sleep(1)
    close_path = r"C:\Users\navee\.gemini\antigravity\brain\f5908e20-83e2-46bf-bfd2-bb4ae4f60283\current_elephant_closeup.png"
    driver.save_screenshot(close_path)
    print(f"Saved close up to {close_path}")

finally:
    driver.quit()

