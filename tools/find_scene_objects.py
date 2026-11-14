from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import time
import json

opts = Options()
opts.add_argument('--headless=new')
opts.add_argument('--window-size=1920,1080')
opts.add_argument('--disable-gpu')
driver = webdriver.Chrome(options=opts)

try:
    driver.get('http://127.0.0.1:8000/')
    time.sleep(4)

    # Inspect all scene meshes near the camera and elephant
    objs = driver.execute_script("""
        const list = [];
        window.threeScene.traverse(obj => {
            if (obj.isMesh) {
                const wp = new THREE.Vector3();
                obj.getWorldPosition(wp);
                // if near x in [10, 60] and z in [70, 130]
                if (wp.x >= 10 && wp.x <= 70 && wp.z >= 70 && wp.z <= 130) {
                    let col = null;
                    if (obj.material) {
                        if (Array.isArray(obj.material)) col = obj.material.map(m => m.color ? m.color.getHexString() : null);
                        else col = obj.material.color ? obj.material.color.getHexString() : null;
                    }
                    list.push({
                        name: obj.name || obj.parent?.name || 'unnamed',
                        parent: obj.parent?.name,
                        type: obj.geometry?.type,
                        pos: [wp.x.toFixed(1), wp.y.toFixed(1), wp.z.toFixed(1)],
                        color: col,
                        visible: obj.visible
                    });
                }
            }
        });
        return list;
    """)
    print(f"Total meshes near (30, 100): {len(objs)}")
    for o in objs:
        print(" ", o)

finally:
    driver.quit()

