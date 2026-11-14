from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import time

opts = Options()
opts.add_argument('--headless=new')
opts.add_argument('--window-size=1920,1080')
opts.add_argument('--disable-gpu')
driver = webdriver.Chrome(options=opts)
try:
    driver.get('http://127.0.0.1:8000/')
    time.sleep(3)

    # Click play button
    driver.execute_script("document.getElementById('btnPlayPause').click();")
    print("Clicked Play...")

    for sec in range(1, 10):
        time.sleep(1)
        info = driver.execute_script("""
            const el = window.threeObjects ? window.threeObjects.elephantGroup : null;
            const sim = window.simulationData;
            const curTime = window.currentTime;
            let res = { time: curTime };
            if (el) {
                res.x = el.position.x;
                res.z = el.position.z;
                res.rotY = el.rotation.y;
                // compute world position of head vs tail
                if (window.threeObjects.elephantProdModel) {
                    res.prodRotY = window.threeObjects.elephantProdModel.rotation.y;
                }
            }
            return res;
        """)
        print(f"Sec {sec}: {info}")
finally:
    driver.quit()

