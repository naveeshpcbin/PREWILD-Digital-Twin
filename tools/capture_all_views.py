from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import time

opts = Options()
opts.add_argument('--headless=new')
opts.add_argument('--window-size=1920,1080')
opts.add_argument('--disable-gpu')
driver = webdriver.Chrome(options=opts)

try:
    # Use cachebust to ensure newly updated app.js and GLBs are loaded
    driver.get(f'http://127.0.0.1:8000/?v={int(time.time())}')
    time.sleep(5)

    # 1. Main panoramic live view
    p1 = r"C:\Users\navee\.gemini\antigravity\brain\f5908e20-83e2-46bf-bfd2-bb4ae4f60283\v5_live_panoramic.png"
    driver.save_screenshot(p1)
    print(f"Captured {p1}")

    # 2. Close up of elephant
    driver.execute_script("""
        if (window.threeCamera && window.threeObjects && window.threeObjects.elephantGroup) {
            const elPos = window.threeObjects.elephantGroup.position;
            window.threeCamera.position.set(elPos.x + 7, elPos.y + 3.5, elPos.z + 7);
            if (window.threeControls) {
                window.threeControls.target.set(elPos.x, elPos.y + 1.8, elPos.z);
                window.threeControls.update();
            }
        }
    """)
    time.sleep(1.5)
    p2 = r"C:\Users\navee\.gemini\antigravity\brain\f5908e20-83e2-46bf-bfd2-bb4ae4f60283\v5_elephant_closeup.png"
    driver.save_screenshot(p2)
    print(f"Captured {p2}")

    # 3. Follow Elephant view (from button)
    driver.execute_script("document.getElementById('btnViewFollow')?.click();")
    time.sleep(1.5)
    p3 = r"C:\Users\navee\.gemini\antigravity\brain\f5908e20-83e2-46bf-bfd2-bb4ae4f60283\v5_follow_view.png"
    driver.save_screenshot(p3)
    print(f"Captured {p3}")

    # 4. Observer Eye-Level view
    driver.execute_script("document.getElementById('btnViewObserver')?.click();")
    time.sleep(1.5)
    p4 = r"C:\Users\navee\.gemini\antigravity\brain\f5908e20-83e2-46bf-bfd2-bb4ae4f60283\v5_observer_view.png"
    driver.save_screenshot(p4)
    print(f"Captured {p4}")

    # 5. Play simulation for 6 seconds and capture locomotion
    driver.execute_script("document.getElementById('btnPlayPause')?.click();")
    print("Playing simulation...")
    time.sleep(6)
    p5 = r"C:\Users\navee\.gemini\antigravity\brain\f5908e20-83e2-46bf-bfd2-bb4ae4f60283\v5_locomotion_progress.png"
    driver.save_screenshot(p5)
    print(f"Captured {p5}")

finally:
    driver.quit()

