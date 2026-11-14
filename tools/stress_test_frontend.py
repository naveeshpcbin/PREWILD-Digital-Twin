from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
import time
import json

opts = Options()
opts.add_argument('--headless=new')
opts.add_argument('--window-size=1920,1080')
opts.add_argument('--disable-gpu')
driver = webdriver.Chrome(options=opts)

errors_found = []

try:
    driver.get('http://127.0.0.1:8000/')
    time.sleep(3)

    # 1. Test clicking all scenarios in dropdown
    scenario_select = driver.find_element(By.ID, 'scenarioSelect')
    options = [o.get_attribute('value') for o in scenario_select.find_elements(By.TAG_NAME, 'option')]
    print(f"Testing scenarios: {options}")

    for sc in options:
        print(f"Switching to scenario: {sc}")
        driver.execute_script(f"""
            const sel = document.getElementById('scenarioSelect');
            sel.value = '{sc}';
            sel.dispatchEvent(new Event('change'));
        """)
        time.sleep(1)
        # click run simulation button
        run_btn = driver.find_elements(By.ID, 'btnRunSim')
        if run_btn:
            run_btn[0].click()
            time.sleep(1)

    # 2. Test clicking all Mode Tabs
    modes = ['MODE A: LIVE TWIN', 'MODE B: LAYER EXPLORER (13)', 'MODE C: CAUSAL FLIGHTLINE', 'MODE D: COUNTERFACTUAL TWIN', 'MODE E: HARDWARE LAB', 'MODE F: MULTI-ANIMAL AI']
    buttons = driver.find_elements(By.CSS_SELECTOR, '.nav-tab')
    print(f"Found {len(buttons)} nav tabs")
    for btn in buttons:
        txt = btn.text
        print(f"Clicking mode tab: {txt}")
        btn.click()
        time.sleep(1)

    # 3. Test clicking view buttons
    views = ['btnViewObserver', 'btnViewOrbit', 'btnViewIso', 'btnViewTop', 'btnViewFollow', 'btnViewHuman', 'btnViewRouter', 'btnViewMast', 'btnViewBreach']
    for v in views:
        el = driver.find_elements(By.ID, v)
        if el:
            el[0].click()
            time.sleep(0.5)

    # 4. Test Multi-Animal AI interactions
    # Switch to mode F
    for btn in buttons:
        if 'MULTI-ANIMAL' in btn.text:
            btn.click()
            time.sleep(1)
            break

    # Click buttons in Multi-Animal panel
    for b_id in ['btnInjectApproach', 'btnInjectTurnAway', 'btnInjectCrossBreach', 'btnResetPopulation']:
        els = driver.find_elements(By.ID, b_id)
        if els:
            print(f"Clicking ecosystem button: {b_id}")
            els[0].click()
            time.sleep(1)

    # 5. Test species filter dropdown
    species_filter = driver.find_elements(By.ID, 'selSpeciesFilter')
    if species_filter:
        s_opts = [o.get_attribute('value') for o in species_filter[0].find_elements(By.TAG_NAME, 'option')]
        print(f"Testing species filter options: {s_opts[:5]}...")
        for so in s_opts[:5]:
            driver.execute_script(f"""
                const sf = document.getElementById('selSpeciesFilter');
                sf.value = '{so}';
                sf.dispatchEvent(new Event('change'));
            """)
            time.sleep(0.5)

    # Check browser console logs
    logs = driver.get_log('browser')
    for entry in logs:
        if entry['level'] == 'SEVERE':
            errors_found.append(entry['message'])
            print(f"ERROR: {entry['message']}")

    print(f"\nTotal severe errors caught: {len(errors_found)}")

finally:
    driver.quit()
