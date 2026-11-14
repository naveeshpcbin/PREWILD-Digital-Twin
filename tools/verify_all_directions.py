from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import time

opts = Options()
opts.add_argument('--headless=new')
opts.add_argument('--disable-gpu')
driver = webdriver.Chrome(options=opts)
try:
    driver.get('http://127.0.0.1:8000/?cachebust=' + str(time.time()))
    time.sleep(3)
    results = driver.execute_script("""
        const prod = window.threeObjects ? window.threeObjects.elephantProdModel : null;
        const elGroup = window.threeObjects ? window.threeObjects.elephantGroup : null;
        if (!prod || !elGroup) return { error: 'Not loaded' };
        
        prod.rotation.y = 0;
        
        let meshObj = null;
        prod.traverse(c => {
            if (c.isMesh) meshObj = c;
        });
        const geom = meshObj.geometry;
        const posAttr = geom.attributes.position;
        const uvAttr = geom.attributes.uv;
        
        function testVelocity(vx, vy) {
            const targetHeading = Math.atan2(-vy, vx);
            elGroup.rotation.y = targetHeading;
            elGroup.updateMatrixWorld(true);
            
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
            const dx = (tuskXSum / tuskCount) - (bodyXSum / bodyCount);
            const dz = (tuskZSum / tuskCount) - (bodyZSum / bodyCount);
            
            const vLen = Math.hypot(vx, vy);
            const nVx = vx / vLen;
            const nVz = vy / vLen;
            const dot = dx * nVx + dz * nVz;
            
            return {
                vx: vx, vy: vy,
                heading: targetHeading,
                dx: dx, dz: dz,
                dotWithVelocity: dot,
                isFacingVelocity: dot > 0.5
            };
        }
        
        return [
            testVelocity(1.5, 0.0),   // Moving +X (towards fence)
            testVelocity(-1.5, 0.0),  // Moving -X (into forest)
            testVelocity(0.0, 1.5),   // Moving +Z (South)
            testVelocity(0.0, -1.5),  // Moving -Z (North)
            testVelocity(1.0, 1.0),   // Moving diagonal (+X, +Z)
            testVelocity(-1.0, 1.0)   // Moving diagonal (-X, +Z)
        ];
    """)
    for r in results:
        v = (r['vx'], r['vy'])
        dot = r['dotWithVelocity']
        fwd = r['isFacingVelocity']
        dx = r['dx']
        dz = r['dz']
        print(f"Velocity {v}: dot={dot:.3f}, isFacingVelocity={fwd}, dx={dx:.3f}, dz={dz:.3f}")
finally:
    driver.quit()

