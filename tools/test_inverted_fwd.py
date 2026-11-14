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
    time.sleep(2.5)

    # Invert modelForwardAxis to (-1, 0, 0) so the face/tusks face the movement direction (fence/sensors)
    driver.execute_script("""
        window.elephantLocomotionController.modelForwardAxis.set(-1, 0, 0);
        window.elephantLocomotionController.reset({x: 20, y: 3, z: 100}, {vx: 1.5, vy: 0});
        updateSimulationStateAtTime(10);
        syncThreeScene(10);
        window.setCameraView('follow');
    """)
    time.sleep(1)
    
    p = os.path.join(artifacts_dir, "v9_test_face_towards_fence.png")
    driver.save_screenshot(p)
    print("Saved:", p)

    # Also capture close up from side/rear
    driver.execute_script("""
        const ep = window.threeObjects.elephantGroup.position;
        window.threeControls.target.set(ep.x, ep.y + 1.8, ep.z);
        window.threeCamera.position.set(ep.x - 10, ep.y + 5, ep.z + 10);
        window.threeControls.update();
    """)
    time.sleep(1)
    p_close = os.path.join(artifacts_dir, "v9_test_face_towards_fence_closeup.png")
    driver.save_screenshot(p_close)
    print("Saved:", p_close)

finally:
    driver.quit()

