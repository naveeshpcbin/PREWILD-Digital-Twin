import os
import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

opts = Options()
opts.add_argument('--headless=new')
opts.add_argument('--disable-gpu')
opts.add_argument('--window-size=1920,1080')

driver = webdriver.Chrome(options=opts)
artifacts_dir = r"C:\Users\navee\.gemini\antigravity\brain\f5908e20-83e2-46bf-bfd2-bb4ae4f60283"

try:
    url = f"http://127.0.0.1:8000/?cachebust={int(time.time())}"
    driver.get(url)
    time.sleep(3)
    
    driver.execute_script("window.setCameraView('follow');")
    
    # Observe moving forward over 4 seconds
    for s in range(1, 5):
        time.sleep(1.0)
        p = os.path.join(artifacts_dir, f"v12_forward_advancing_{s}s.png")
        driver.save_screenshot(p)
        info = driver.execute_script("""
            const ep = window.threeObjects.elephantGroup.position;
            return {
                x: ep.x,
                z: ep.z
            };
        """)
        print(f"[{s}s] ElephantPos=({info['x']:.1f}, {info['z']:.1f})")

finally:
    driver.quit()
