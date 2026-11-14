import os
import time
import math
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
            print("[OK] Elephant GLB production model loaded.")
            break
        time.sleep(0.5)

    print("\n==================================================================")
    print("MANDATORY TEST 1 & 2: Forward Movement & Layer Approach (approach_crossing)")
    print("==================================================================")
    driver.execute_script("""
        document.getElementById('scenarioSelect').value = 'approach_crossing';
        document.getElementById('scenarioSelect').dispatchEvent(new Event('change'));
    """)
    time.sleep(1.5)
    
    # Capture Screenshot 1: Initial Elephant Orientation
    driver.execute_script("window.setCameraView('follow'); updateSimulationStateAtTime(0); syncThreeScene(0);")
    time.sleep(1)
    p1 = os.path.join(artifacts_dir, "v8_01_initial_orientation.png")
    driver.save_screenshot(p1)
    print(f"Screenshot 1 saved: {p1}")

    # Evaluate approach crossing at multiple time intervals
    t_samples = [0.5, 5.0, 15.0, 25.0, 35.0, 50.0]
    for t in t_samples:
        diag = driver.execute_script("""
            const t = arguments[0];
            updateSimulationStateAtTime(t);
            syncThreeScene(t);
            
            const animal = getGroundTruthAtTime(t);
            const speed = animal ? Math.hypot(animal.vx, animal.vy) : 0;
            const elGroup = window.threeObjects ? window.threeObjects.elephantGroup : null;
            const prod = window.threeObjects ? window.threeObjects.elephantProdModel : null;
            
            // Measure actual bone positions in world space
            let headPos = null, tailPos = null;
            if (prod) {
                prod.traverse(c => {
                    if (c.name === 'Head') {
                        const wp = new THREE.Vector3();
                        c.getWorldPosition(wp);
                        headPos = { x: wp.x, y: wp.y, z: wp.z };
                    }
                    if (c.name === 'Tail') {
                        const wp = new THREE.Vector3();
                        c.getWorldPosition(wp);
                        tailPos = { x: wp.x, y: wp.y, z: wp.z };
                    }
                });
            }
            
            const dbg = window.__PRW_ELEPHANT_LOCOMOTION_DEBUG__ || {};
            let fwdDot = 0;
            if (headPos && tailPos && speed > 0.05) {
                const fX = headPos.x - tailPos.x;
                const fZ = headPos.z - tailPos.z;
                const fLen = Math.hypot(fX, fZ);
                const nVx = animal.vx / speed;
                const nVz = animal.vy / speed;
                fwdDot = (fX * nVx + fZ * nVz) / (fLen || 1.0);
            }
            
            return {
                t: t,
                posX: elGroup ? elGroup.position.x : 0,
                posZ: elGroup ? elGroup.position.z : 0,
                vx: animal ? animal.vx : 0,
                vy: animal ? animal.vy : 0,
                speed: speed,
                headX: headPos ? headPos.x : 0,
                tailX: tailPos ? tailPos.x : 0,
                boneForwardDot: fwdDot,
                locomotionDot: dbg.dotProductWithVelocity,
                isFacingForward: fwdDot > 0.6
            };
        """, t)
        print(f"t={diag['t']:4.1f}s | Pos=({diag['posX']:5.1f}, {diag['posZ']:5.1f}) | Vel=({diag['vx']:4.2f}, {diag['vy']:4.2f}) | HeadX={diag['headX']:5.2f}, TailX={diag['tailX']:5.2f} | Dot={diag['boneForwardDot']:5.3f} | Forward={diag['isFacingForward']}")

    # Capture Screenshot 2: Moving Forward Along Path
    driver.execute_script("updateSimulationStateAtTime(15); syncThreeScene(15);")
    time.sleep(1)
    p2 = os.path.join(artifacts_dir, "v8_02_moving_forward_path.png")
    driver.save_screenshot(p2)
    print(f"Screenshot 2 saved: {p2}")

    # Capture Screenshot 3: Approaching Detection Layers
    driver.execute_script("window.setCameraView('observer'); updateSimulationStateAtTime(28); syncThreeScene(28);")
    time.sleep(1)
    p3 = os.path.join(artifacts_dir, "v8_03_approaching_detection_layers.png")
    driver.save_screenshot(p3)
    print(f"Screenshot 3 saved: {p3}")

    print("\n==================================================================")
    print("MANDATORY TEST 3 & 4: Direction Changes & Temporary Stop (turns_away)")
    print("==================================================================")
    driver.execute_script("""
        document.getElementById('scenarioSelect').value = 'turns_away';
        document.getElementById('scenarioSelect').dispatchEvent(new Event('change'));
    """)
    time.sleep(1.5)

    # In turns_away, waypoints:
    # [20,100] -> [50,100] (East +X)
    # [50,100] -> [75,105] (East-Southeast)
    # [75,105] -> [70,120] (Southwest turning back! X decreases from 75 to 70)
    # [70,120] -> [50,140] (West-Southwest back into forest)
    turn_samples = [10.0, 35.0, 45.0, 50.0, 65.0]
    for t in turn_samples:
        turn_diag = driver.execute_script("""
            const t = arguments[0];
            updateSimulationStateAtTime(t);
            syncThreeScene(t);
            
            const animal = getGroundTruthAtTime(t);
            const speed = animal ? Math.hypot(animal.vx, animal.vy) : 0;
            const elGroup = window.threeObjects ? window.threeObjects.elephantGroup : null;
            const prod = window.threeObjects ? window.threeObjects.elephantProdModel : null;
            
            let headPos = null, tailPos = null;
            if (prod) {
                prod.traverse(c => {
                    if (c.name === 'Head') {
                        const wp = new THREE.Vector3();
                        c.getWorldPosition(wp);
                        headPos = { x: wp.x, y: wp.y, z: wp.z };
                    }
                    if (c.name === 'Tail') {
                        const wp = new THREE.Vector3();
                        c.getWorldPosition(wp);
                        tailPos = { x: wp.x, y: wp.y, z: wp.z };
                    }
                });
            }
            
            const dbg = window.__PRW_ELEPHANT_LOCOMOTION_DEBUG__ || {};
            let fwdDot = 0;
            if (headPos && tailPos && speed > 0.05) {
                const fX = headPos.x - tailPos.x;
                const fZ = headPos.z - tailPos.z;
                const fLen = Math.hypot(fX, fZ);
                const nVx = animal.vx / speed;
                const nVz = animal.vy / speed;
                fwdDot = (fX * nVx + fZ * nVz) / (fLen || 1.0);
            } else if (headPos && tailPos) {
                // If stopped, dot with last valid direction
                const fX = headPos.x - tailPos.x;
                const fZ = headPos.z - tailPos.z;
                const fLen = Math.hypot(fX, fZ);
                const lDir = dbg.targetDirection || { x: 1, z: 0 };
                fwdDot = (fX * lDir.x + fZ * lDir.z) / (fLen || 1.0);
            }
            
            return {
                t: t,
                posX: elGroup ? elGroup.position.x : 0,
                posZ: elGroup ? elGroup.position.z : 0,
                vx: animal ? animal.vx : 0,
                vy: animal ? animal.vy : 0,
                speed: speed,
                isStationary: dbg.isStationary,
                boneForwardDot: fwdDot,
                isFacingForward: fwdDot > 0.6
            };
        """, t)
        print(f"[turns_away] t={turn_diag['t']:4.1f}s | Pos=({turn_diag['posX']:5.1f}, {turn_diag['posZ']:5.1f}) | Vel=({turn_diag['vx']:5.2f}, {turn_diag['vy']:5.2f}) | Speed={turn_diag['speed']:4.2f}m/s | Stationary={turn_diag['isStationary']} | Dot={turn_diag['boneForwardDot']:5.3f} | FacingForward={turn_diag['isFacingForward']}")

    # Capture Screenshot 4: Changing Direction at Waypoint (turning away)
    driver.execute_script("window.setCameraView('follow'); updateSimulationStateAtTime(45); syncThreeScene(45);")
    time.sleep(1)
    p4 = os.path.join(artifacts_dir, "v8_04_changing_direction_waypoint.png")
    driver.save_screenshot(p4)
    print(f"Screenshot 4 saved: {p4}")

    print("\n==================================================================")
    print("MANDATORY TEST 5: Restart Scenario Resilience")
    print("==================================================================")
    restart_ok = True
    for cycle in range(1, 4):
        res = driver.execute_script("""
            document.getElementById('btnReset').click();
            updateSimulationStateAtTime(0);
            syncThreeScene(0);
            
            const animal = getGroundTruthAtTime(0);
            const dbg = window.__PRW_ELEPHANT_LOCOMOTION_DEBUG__ || {};
            const prod = window.threeObjects ? window.threeObjects.elephantProdModel : null;
            
            let headX = 0, tailX = 0;
            if (prod) {
                prod.traverse(c => {
                    if (c.name === 'Head') {
                        const wp = new THREE.Vector3(); c.getWorldPosition(wp); headX = wp.x;
                    }
                    if (c.name === 'Tail') {
                        const wp = new THREE.Vector3(); c.getWorldPosition(wp); tailX = wp.x;
                    }
                });
            }
            return {
                headLeading: headX > tailX,
                dot: dbg.dotProductWithVelocity,
                heading: dbg.headingRad
            };
        """)
        print(f"Restart Cycle {cycle}: HeadLeading={res['headLeading']} (Dot={res['dot']:.3f}, Heading={res['heading']:.3f})")
        if not res['headLeading']:
            restart_ok = False

    # Capture Screenshot 5: Restarted Scenario Verification
    driver.execute_script("window.setCameraView('observer'); updateSimulationStateAtTime(0); syncThreeScene(0);")
    time.sleep(1)
    p5 = os.path.join(artifacts_dir, "v8_05_restarted_scenario.png")
    driver.save_screenshot(p5)
    print(f"Screenshot 5 saved: {p5}")

    print("\n==================================================================")
    print("MANDATORY TEST 6 & 7: Animation Consistency & L1/L2/L3 Detection Flow")
    print("==================================================================")
    driver.execute_script("""
        document.getElementById('scenarioSelect').value = 'approach_crossing';
        document.getElementById('scenarioSelect').dispatchEvent(new Event('change'));
    """)
    time.sleep(1.5)
    
    detection_flow = driver.execute_script("""
        const events = window.simulationData ? window.simulationData.events : [];
        const l1Ev = events.filter(e => e.event_type && e.event_type.includes('rf') || e.event_type === 'sensor_trigger' && e.sensor_id && e.sensor_id.includes('csi'));
        const l2Ev = events.filter(e => e.sensor_id && (e.sensor_id.includes('pir') || e.sensor_id.includes('aco') || e.sensor_id.includes('vib')));
        const l3Ev = events.filter(e => e.sensor_id && e.sensor_id.includes('cam'));
        
        return {
            totalEvents: events.length,
            hasL1: events.some(e => e.layer === 1 || (e.sensor_id && e.sensor_id.includes('csi'))),
            hasL2: events.some(e => e.layer === 2 || (e.sensor_id && (e.sensor_id.includes('pir') || e.sensor_id.includes('aco')))),
            hasL3: events.some(e => e.layer === 3 || (e.sensor_id && e.sensor_id.includes('cam'))),
            firstL1Time: events.find(e => e.layer === 1)?.timestamp_s,
            firstL2Time: events.find(e => e.layer === 2)?.timestamp_s,
            firstL3Time: events.find(e => e.layer === 3)?.timestamp_s,
            breachTime: events.find(e => e.event_type === 'boundary_breach')?.timestamp_s
        };
    """)
    print("Detection Event Flow:", detection_flow)

    logs = driver.get_log('browser')
    severe = [e for e in logs if e['level'] == 'SEVERE']
    print(f"\nBrowser Severe Errors: {len(severe)}")
    for err in severe:
        print(f"  [ERROR] {err['message']}")

finally:
    driver.quit()

