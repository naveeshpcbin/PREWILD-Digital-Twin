import os
import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

opts = Options()
opts.add_argument('--headless=new')
opts.add_argument('--disable-gpu')
opts.add_argument('--window-size=1920,1080')

scenarios = [
    'approach_crossing',
    'grazing_deflection',
    'false_positive_flutter',
    'herd_multimodal_split',
    'sensor_blindspot_evasion'
]

driver = webdriver.Chrome(options=opts)
try:
    driver.get(f"http://127.0.0.1:8000/?cachebust={int(time.time())}")
    time.sleep(3)
    
    all_passed = True
    
    for sc in scenarios:
        print(f"\n--- Testing Scenario: {sc} ---")
        driver.execute_script(f"""
            document.getElementById('scenarioSelect').value = '{sc}';
            document.getElementById('scenarioSelect').dispatchEvent(new Event('change'));
        """)
        time.sleep(1.5)
        
        # Test time steps 5, 10, 20
        for t in [5.0, 15.0, 25.0]:
            res = driver.execute_script("""
                const t = arguments[0];
                updateSimulationStateAtTime(t);
                syncThreeScene(t);
                
                const animal = getGroundTruthAtTime(t);
                const speed = animal ? Math.hypot(animal.vx, animal.vy) : 0;
                const elGroup = window.threeObjects ? window.threeObjects.elephantGroup : null;
                const prod = window.threeObjects ? window.threeObjects.elephantProdModel : null;
                
                if (!elGroup || !prod) return { error: 'Model missing' };
                
                let meshObj = null;
                prod.traverse(c => { if (c.isMesh) meshObj = c; });
                const posAttr = meshObj.geometry.attributes.position;
                const uvAttr = meshObj.geometry.attributes.uv;
                
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
                const fwdX = (tuskXSum / tuskCount) - (bodyXSum / bodyCount);
                const fwdZ = (tuskZSum / tuskCount) - (bodyZSum / bodyCount);
                const fwdLen = Math.hypot(fwdX, fwdZ);
                
                let dot = 0;
                let isFacingForward = true;
                if (speed > 0.05) {
                    const nVx = animal.vx / speed;
                    const nVz = animal.vy / speed;
                    dot = (fwdX * nVx + fwdZ * nVz) / (fwdLen || 1.0);
                    isFacingForward = dot > 0.3; // positive forward alignment
                }
                return {
                    t: t,
                    speed: speed,
                    vx: animal ? animal.vx : 0,
                    vy: animal ? animal.vy : 0,
                    dot: dot,
                    isFacingForward: isFacingForward
                };
            """, t)
            print(f"[{sc}] t={t:4.1f}s | Speed={res['speed']:4.2f}m/s (vx={res['vx']:5.2f}, vy={res['vy']:5.2f}) | Dot={res['dot']:5.3f} | FacingForward={res['isFacingForward']}")
            if res['speed'] > 0.05 and not res['isFacingForward']:
                all_passed = False
                print(f"FAILED on scenario {sc} at t={t}")
                
    logs = driver.get_log('browser')
    severe = [e for e in logs if e['level'] == 'SEVERE']
    print(f"\nAll scenarios forward verification: {'PASSED' if all_passed else 'FAILED'}")
    print(f"Browser severe console errors: {len(severe)}")
finally:
    driver.quit()

