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
    
    driver.execute_script("document.getElementById('btnPlayPause')?.click();")
    
    for step in range(10):
        time.sleep(0.5)
        info = driver.execute_script("""
            const el = window.threeObjects ? window.threeObjects.elephantGroup : null;
            const prod = window.threeObjects ? window.threeObjects.elephantProdModel : null;
            const action = window.threeObjects ? window.threeObjects.elephantWalkAction : null;
            
            return {
                elPos: el ? { x: el.position.x, y: el.position.y, z: el.position.z } : null,
                elRotY: el ? el.rotation.y : null,
                prodRotY: prod ? prod.rotation.y : null,
                actionTime: action ? action.time : null,
                actionTimeScale: action ? action.getEffectiveTimeScale() : null,
                actionPaused: action ? action.paused : null
            };
        """)
        print(f"Step {step}: {info}")
finally:
    driver.quit()

