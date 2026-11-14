from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import time

options = Options()
options.add_argument('--headless=new')
options.add_argument('--no-sandbox')
options.add_argument('--disable-gpu')
options.add_argument('--window-size=1920,1080')

driver = webdriver.Chrome(options=options)
try:
    driver.get('http://127.0.0.1:8000/?cachebust=' + str(time.time()))
    time.sleep(3)
    
    scenarios = ['approach_crossing', 'turns_away', 'nuisance_triggers', 'degraded_network', 'camera_gating']
    for sc in scenarios:
        print(f"Testing scenario {sc}...")
        driver.execute_script(f"""
            const sel = document.getElementById('scenarioSelect');
            if (sel) {{
                sel.value = '{sc}';
                sel.dispatchEvent(new Event('change'));
            }}
        """)
        time.sleep(2)
        
        # Check for errors in browser logs
        logs = driver.get_log('browser')
        errors = [l for l in logs if l['level'] == 'SEVERE']
        if errors:
            print(f"ERRORS in {sc}:", errors)
        else:
            print(f"{sc} OK!")
            
    # Now test Mode switching!
    modes = ['live', 'layers', 'flightline', 'counterfactual', 'hardware', 'ecosystem']
    for m in modes:
        print(f"Testing mode {m}...")
        driver.execute_script(f"""
            const btn = document.querySelector('[data-lab-mode=\"{m}\"]') || document.getElementById('tab-{m}');
            if (btn) btn.click();
            else console.log('Mode btn for {m} not found by simple query');
        """)
        time.sleep(1)
        logs = driver.get_log('browser')
        errors = [l for l in logs if l['level'] == 'SEVERE']
        if errors:
            print(f"ERRORS in mode {m}:", errors)
        else:
            print(f"Mode {m} OK!")
finally:
    driver.quit()

