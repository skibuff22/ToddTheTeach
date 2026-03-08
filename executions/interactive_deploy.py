import os
import time
from playwright.sync_api import sync_playwright
from dotenv import load_dotenv

load_dotenv()
url = os.environ.get('CPANEL_URL')
user = os.environ.get('CPANEL_USERNAME')
pwd = os.environ.get('CPANEL_PASSWORD')

p = sync_playwright().start()
# headless=False makes the browser visible on your screen
browser = p.chromium.launch(headless=False, slow_mo=500)
page = browser.new_page()

print("Navigating to cPanel...")
page.goto(url)
print("Browser is open and at the login screen!")
# Keep session open in interactive mode
