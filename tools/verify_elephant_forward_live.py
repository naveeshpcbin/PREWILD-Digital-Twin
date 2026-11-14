import os
import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

opts = Options()
opts.add_argument('--headless=new')
opts.add_argument('--disable-gpu')
opts.add_argument('--window-size=1920,1080')

driver = webdriver.Chrome(options=opts)
try:
    url = f"http://127.0.0.1:8000/?cachebust={int(time.time())}"
    print(f"Navigating to {url}...")
    driver.get(url)
    time.sleep(3)
    
    # Wait for elephant model to load
    for _ in range(20):
        is_loaded = driver.execute_script("return window.__PRW_ELEPHANT_LOADED__ === true;")
        if is_loaded:
            print("Production elephant GLB model loaded successfully!")
            break
        time.sleep(0.5)
        
    # Check orientation at time = 0, 5, 10, 15, 20
    test_times = [0.0, 5.0, 10.0, 15.0, 20.0, 30.0]
    eval_results = []
    
    for t in test_times:
        res = driver.execute_script("""
            const t = arguments[0];
            updateSimulationStateAtTime(t);
            syncThreeScene(t);
            
            const animal = getGroundTruthAtTime(t);
            const speed = animal ? Math.hypot(animal.vx, animal.vy) : 0;
            const elGroup = window.threeObjects ? window.threeObjects.elephantGroup : null;
            const prod = window.threeObjects ? window.threeObjects.elephantProdModel : null;
            
            if (!elGroup || !prod) return { error: 'Objects missing' };
            
            let meshObj = null;
            prod.traverse(c => { if (c.isMesh) meshObj = c; });
            const geom = meshObj.geometry;
            const posAttr = geom.attributes.position;
            const uvAttr = geom.attributes.uv;
            
            let tuskXSum = 0, tuskCount = 0;
            let bodyXSum = 0, bodyCount = 0;
            let tuskZSum = 0, bodyZSum = 0;
            const v = new THREE.Vector3();
            for (let i = 0; i < posAttr.count; i++) {
                v.fromBufferAttribute(posAttr, i);
                meshObj.localToWorld(v);
                const u = uvAttr.getX(i);
                const w = uvAttr.getY(i);
                if (w > 0.75 && u > 0.25 && u < 0.65) {
                    tuskXSum += v.x;
                    tuskZSum += v.z;
                    tuskCount++;
                } else {
                    bodyXSum += v.x;
                    bodyZSum += v.z;
                    bodyCount++;
                }
            }
            const tuskX = tuskXSum / tuskCount;
            const tuskZ = tuskZSum / tuskCount;
            const bodyX = bodyXSum / bodyCount;
            const bodyZ = bodyZSum / bodyCount;
            
            const fwdX = tuskX - bodyX;
            const fwdZ = tuskZ - bodyZ;
            const fwdLen = Math.hypot(fwdX, fwdZ);
            
            let dot = 0;
            let isFacingForward = true;
            if (speed > 0.05) {
                const nVx = animal.vx / speed;
                const nVz = animal.vy / speed;
                dot = (fwdX * nVx + fwdZ * nVz) / (fwdLen || 1.0);
                isFacingForward = dot > 0.5;
            }
            
            return {
                t: t,
                speed: speed,
                vx: animal ? animal.vx : 0,
                vy: animal ? animal.vy : 0,
                heading: elGroup.rotation.y,
                fwdX: fwdX,
                fwdZ: fwdZ,
                dot: dot,
                isFacingForward: isFacingForward,
                elephantPos: { x: elGroup.position.x, y: elGroup.position.y, z: elGroup.position.z }
            };
        """, t)
        eval_results.append(res)
        print(f"t={t:4.1f}s | Speed={res['speed']:4.2f}m/s | vx={res['vx']:5.2f}, vy={res['vy']:5.2f} | Heading={res['heading']:6.3f} rad | FwdDot={res['dot']:5.3f} | FacingForward={res['isFacingForward']}")

    # Capture screenshots
    artifacts_dir = r"C:\Users\navee\.gemini\antigravity\brain\f5908e20-83e2-46bf-bfd2-bb4ae4f60283"
    
    # 1. Observer View at t=15s
    driver.execute_script("setCameraView('observer'); updateSimulationStateAtTime(15); syncThreeScene(15);")
    time.sleep(1)
    obs_path = os.path.join(artifacts_dir, "v7_elephant_forward_observer.png")
    driver.save_screenshot(obs_path)
    print(f"Saved {obs_path}")
    
    # 2. Follow View at t=15s
    driver.execute_script("setCameraView('follow'); updateSimulationStateAtTime(15); syncThreeScene(15);")
    time.sleep(1)
    follow_path = os.path.join(artifacts_dir, "v7_elephant_forward_follow.png")
    driver.save_screenshot(follow_path)
    print(f"Saved {follow_path}")

    # 3. Close-up Isometric View of Elephant Head & Body
    driver.execute_script("""
        const ep = window.threeObjects.elephantGroup.position;
        window.threeControls.target.set(ep.x, ep.y + 1.8, ep.z);
        window.threeCamera.position.set(ep.x + 8, ep.y + 4.5, ep.z + 8);
        window.threeControls.update();
    """)
    time.sleep(1)
    close_path = os.path.join(artifacts_dir, "v7_elephant_forward_closeup.png")
    driver.save_screenshot(close_path)
    print(f"Saved {close_path}")
    
    # Check browser logs for errors
    logs = driver.get_log('browser')
    severe_errors = [entry for entry in logs if entry['level'] == 'SEVERE']
    print(f"Console severe errors: {len(severe_errors)}")
    for err in severe_errors:
        print(f"  [ERROR] {err['message']}")
        
finally:
    driver.quit()

