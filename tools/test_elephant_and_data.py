from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import time, json

options = Options()
options.add_argument('--headless=new')
options.add_argument('--no-sandbox')
options.add_argument('--disable-gpu')
options.add_argument('--window-size=1920,1080')

driver = webdriver.Chrome(options=options)
try:
    driver.get('http://127.0.0.1:8000/?cachebust=' + str(time.time()))
    time.sleep(3)
    
    # Click play button
    driver.execute_script("""
        const btn = document.getElementById('playPauseBtn') || document.getElementById('btnPlay') || document.querySelector('.play-btn');
        if (btn) {
            console.log('Clicking play button:', btn);
            btn.click();
        } else {
            console.warn('Play button not found, calling startSimulation() directly');
            if (typeof startSimulation === 'function') startSimulation();
        }
    """)
    
    for s in range(12):
        time.sleep(1)
        res = driver.execute_script("""
            let report = {
                simTime: typeof currentTime !== 'undefined' ? currentTime : (typeof simTime !== 'undefined' ? simTime : null),
                isPlaying: typeof isPlaying !== 'undefined' ? isPlaying : null,
                simulationDataLoaded: typeof simulationData !== 'undefined' && simulationData !== null,
                gtLen: (typeof simulationData !== 'undefined' && simulationData && simulationData.ground_truth) ? simulationData.ground_truth.length : 0
            };
            if (window.threeObjects && window.threeObjects.elephantProdModel) {
                const prod = window.threeObjects.elephantProdModel;
                prod.traverse(child => {
                    if (child.name === 'Head') {
                        const wp = new THREE.Vector3();
                        child.getWorldPosition(wp);
                        report.headX = wp.x;
                        report.headZ = wp.z;
                    }
                    if (child.name === 'Tail') {
                        const wp = new THREE.Vector3();
                        child.getWorldPosition(wp);
                        report.tailX = wp.x;
                        report.tailZ = wp.z;
                    }
                });
                if (window.threeObjects.elephantGroup) {
                    report.groupX = window.threeObjects.elephantGroup.position.x;
                    report.groupZ = window.threeObjects.elephantGroup.position.z;
                    report.groupRotY = window.threeObjects.elephantGroup.rotation.y;
                }
            }
            return report;
        """)
        print(f"Second {s}:", json.dumps(res))
        
    logs = driver.get_log('browser')
    print("=== BROWSER LOGS (SEVERE/WARNING) ===")
    for l in logs:
        if l['level'] in ['SEVERE', 'WARNING']:
            print(f"[{l['level']}] {l['message']}")
            
    # Also grab screenshot
    driver.save_screenshot('C:/Users/navee/.gemini/antigravity/brain/f5908e20-83e2-46bf-bfd2-bb4ae4f60283/live_sim_playback.png')
    print("Screenshot saved to live_sim_playback.png")
finally:
    driver.quit()

