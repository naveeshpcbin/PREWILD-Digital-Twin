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
    print(f"Loading {url}...")
    driver.get(url)
    time.sleep(3)
    
    # Wait for elephant model
    for _ in range(20):
        loaded = driver.execute_script("return window.__PRW_ELEPHANT_LOADED__ === true;")
        if loaded:
            print("[OK] Elephant GLB model loaded.")
            break
        time.sleep(0.5)

    print("\n--- Testing Approach Crossing (Elephant Face towards Fence and Sensors) ---")
    driver.execute_script("""
        document.getElementById('scenarioSelect').value = 'approach_crossing';
        document.getElementById('scenarioSelect').dispatchEvent(new Event('change'));
    """)
    time.sleep(1.5)

    test_times = [0.0, 5.0, 15.0, 25.0, 35.0, 50.0]
    all_face_forward = True
    for t in test_times:
        res = driver.execute_script("""
            const t = arguments[0];
            updateSimulationStateAtTime(t);
            syncThreeScene(t);
            
            const animal = getGroundTruthAtTime(t);
            const prod = window.threeObjects ? window.threeObjects.elephantProdModel : null;
            const elGroup = window.threeObjects ? window.threeObjects.elephantGroup : null;
            const ctrl = window.elephantLocomotionController;
            
            let meshObj = null;
            prod.traverse(c => { if (c.isMesh) meshObj = c; });
            const posAttr = meshObj.geometry.attributes.position;
            const uvAttr = meshObj.geometry.attributes.uv;
            
            let tuskXSum = 0, tuskCount = 0;
            let bodyXSum = 0, bodyCount = 0;
            const v = new THREE.Vector3();
            for (let i = 0; i < posAttr.count; i++) {
                v.fromBufferAttribute(posAttr, i);
                meshObj.localToWorld(v);
                const u = uvAttr.getX(i);
                const w = uvAttr.getY(i);
                if (w > 0.75 && u > 0.25 && u < 0.65) {
                    tuskXSum += v.x;
                    tuskCount++;
                } else {
                    bodyXSum += v.x;
                    bodyCount++;
                }
            }
            const tuskX = tuskXSum / tuskCount;
            const bodyX = bodyXSum / bodyCount;
            const facePointsToFence = tuskX > bodyX;
            
            return {
                t: t,
                posX: elGroup.position.x,
                posZ: elGroup.position.z,
                vx: animal ? animal.vx : 0,
                tuskX: tuskX,
                bodyX: bodyX,
                facePointsToFence: facePointsToFence,
                quaternion: { x: elGroup.quaternion.x, y: elGroup.quaternion.y, z: elGroup.quaternion.z, w: elGroup.quaternion.w }
            };
        """, t)
        print(f"t={res['t']:4.1f}s | PosX={res['posX']:5.1f}m | TuskX={res['tuskX']:5.2f}m, BodyX={res['bodyX']:5.2f}m | FacePointsToFence={res['facePointsToFence']}")
        if not res['facePointsToFence']:
            all_face_forward = False

    print("\nCapture Official Verification Screenshots:")
    
    # 1. Follow view behind elephant (seeing its back and the head facing forward to fence)
    driver.execute_script("window.setCameraView('follow'); updateSimulationStateAtTime(15); syncThreeScene(15);")
    time.sleep(1)
    p_follow = os.path.join(artifacts_dir, "v10_elephant_face_to_fence_follow.png")
    driver.save_screenshot(p_follow)
    print("Saved:", p_follow)

    # 2. Side-angle view showing face, trunk and tusks pointing directly towards fence & sensor line
    driver.execute_script("""
        const ep = window.threeObjects.elephantGroup.position;
        window.threeControls.target.set(ep.x, ep.y + 1.8, ep.z);
        window.threeCamera.position.set(ep.x - 8, ep.y + 4.5, ep.z + 10);
        window.threeControls.update();
    """)
    time.sleep(1)
    p_side = os.path.join(artifacts_dir, "v10_elephant_face_to_fence_side.png")
    driver.save_screenshot(p_side)
    print("Saved:", p_side)

    # 3. Observer view showing full corridor with elephant advancing face-forward to fence
    driver.execute_script("window.setCameraView('observer'); updateSimulationStateAtTime(25); syncThreeScene(25);")
    time.sleep(1)
    p_obs = os.path.join(artifacts_dir, "v10_elephant_face_to_fence_observer.png")
    driver.save_screenshot(p_obs)
    print("Saved:", p_obs)

    logs = driver.get_log('browser')
    severe = [e for e in logs if e['level'] == 'SEVERE']
    print(f"\nBrowser Severe Errors: {len(severe)}")
    print(f"All Time Steps Face Pointing To Fence: {'PASSED' if all_face_forward else 'FAILED'}")

finally:
    driver.quit()

