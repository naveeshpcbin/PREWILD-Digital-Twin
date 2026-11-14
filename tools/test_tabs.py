from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
import time

opts = Options()
opts.add_argument('--headless=new')
opts.add_argument('--window-size=1920,1080')
opts.add_argument('--disable-gpu')
driver = webdriver.Chrome(options=opts)

try:
    driver.get('http://127.0.0.1:8000/')
    time.sleep(3)

    tabs = driver.find_elements(By.CSS_SELECTOR, '.lab-mode-tab')
    print(f"Found {len(tabs)} lab-mode tabs")
    for t in tabs:
        t_id = t.get_attribute('id')
        t_mode = t.get_attribute('data-mode')
        print(f"Clicking mode tab: {t_id} (mode={t_mode})")
        t.click()
        time.sleep(1.5)

    logs = driver.get_log('browser')
    print(f"\nBrowser logs after switching all tabs:")
    for entry in logs:
        if entry['level'] in ['SEVERE', 'WARNING']:
            print(f"  [{entry['level']}] {entry['message']}")

finally:
    driver.quit()

