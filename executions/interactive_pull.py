import os
from playwright.sync_api import sync_playwright
from dotenv import load_dotenv

load_dotenv()
url = os.environ.get('CPANEL_URL')
user = os.environ.get('CPANEL_USERNAME')
pwd = os.environ.get('CPANEL_PASSWORD')

p = sync_playwright().start()
browser = p.chromium.launch(headless=False, slow_mo=500)
page = browser.new_page()

page.goto(url)
page.fill('input[name="user"]', user)
page.fill('input[name="pass"]', pwd)
page.click('button[id="login_submit"]')
page.wait_for_load_state('networkidle')
print("Browser session ready for manual steering.")

# Keep session open
import time
time.sleep(3600)
