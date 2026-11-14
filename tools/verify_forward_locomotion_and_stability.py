from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from PIL import Image
import time
import json
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
    print("Loading Digital Twin application...")
    driver.get('http://127.0.0.1:8000/?cachebust=' + str(time.time()))
    time.sleep(3)

    # 1. Switch to observer view first to check
    driver.execute_script("""
        if (typeof setCameraView === 'function') setCameraView('observer');
    """)
    time.sleep(1)

    print("Checking elephant locomotion across 6 playback seconds...")
    locomotion_log = []
    for s in range(6):
        time.sleep(1)
        step_data = driver.execute_script("""
            const prod = window.threeObjects ? window.threeObjects.elephantProdModel : null;
            let headPos = null, tailPos = null;
            if (prod) {
                prod.traverse(c => {
                    if (c.name === 'Head') { const wp = new THREE.Vector3(); c.getWorldPosition(wp); headPos = {x: wp.x, y: wp.y, z: wp.z}; }
                    if (c.name === 'Tail') { const wp = new THREE.Vector3(); c.getWorldPosition(wp); tailPos = {x: wp.x, y: wp.y, z: wp.z}; }
                });
            }
            const elGroup = window.threeObjects ? window.threeObjects.elephantGroup : null;
            return {
                groupX: elGroup ? elGroup.position.x : null,
                groupZ: elGroup ? elGroup.position.z : null,
                rotY: elGroup ? elGroup.rotation.y : null,
                headX: headPos ? headPos.x : null,
                headZ: headPos ? headPos.z : null,
                tailX: tailPos ? tailPos.x : null,
                tailZ: tailPos ? tailPos.z : null
            };
        """)
        locomotion_log.append(step_data)
        dx = (step_data['headX'] or 0) - (step_data['tailX'] or 0)
        print(f"Second {s+1}: GroupX={step_data['groupX']:.2f}, HeadX={step_data['headX']:.2f}, TailX={step_data['tailX']:.2f}, HeadAhead={dx > 0} (dx={dx:+.2f})")

    # 2. Capture Observer View Screenshot
    obs_path = os.path.join(ARTIFACT_DIR, "verified_observer_forward_locomotion.png")
    driver.save_screenshot(obs_path)
    print(f"Saved observer screenshot: {obs_path}")

    # Crop elephant close-up from observer view
    img_obs = Image.open(obs_path)
    w, h = img_obs.size
    # Crop center area around elephant
    crop_elephant = img_obs.crop((450, 480, 850, 720))
    crop_path = os.path.join(ARTIFACT_DIR, "verified_elephant_close_up.png")
    crop_elephant.save(crop_path)
    print(f"Saved elephant close-up: {crop_path}")

    # 3. Capture Follow View Screenshot
    driver.execute_script("if (typeof setCameraView === 'function') setCameraView('follow');")
    time.sleep(2)
    follow_path = os.path.join(ARTIFACT_DIR, "verified_follow_elephant_view.png")
    driver.save_screenshot(follow_path)
    print(f"Saved follow screenshot: {follow_path}")

    # 4. Capture Orbit View Screenshot
    driver.execute_script("if (typeof setCameraView === 'function') setCameraView('orbit');")
    time.sleep(2)
    orbit_path = os.path.join(ARTIFACT_DIR, "verified_orbit_panoramic_view.png")
    driver.save_screenshot(orbit_path)
    print(f"Saved orbit screenshot: {orbit_path}")

    # 5. Capture Isometric View Screenshot
    driver.execute_script("if (typeof setCameraView === 'function') setCameraView('isometric');")
    time.sleep(2)
    iso_path = os.path.join(ARTIFACT_DIR, "verified_isometric_tactical_view.png")
    driver.save_screenshot(iso_path)
    print(f"Saved isometric screenshot: {iso_path}")

    # 6. Check console logs for errors
    logs = driver.get_log('browser')
    severe = [l for l in logs if l['level'] == 'SEVERE']
    print(f"Console SEVERE errors count: {len(severe)}")
    for e in severe:
        print(f"  [ERROR] {e['message']}")

finally:
    driver.quit()

print("Verification run completed!")

