import os
import time
from playwright.sync_api import sync_playwright
from dotenv import load_dotenv

def inspect():
    load_dotenv()
    url = os.environ.get('CPANEL_URL')
    user = os.environ.get('CPANEL_USERNAME')
    pwd = os.environ.get('CPANEL_PASSWORD')

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        
        page.goto(url)
        page.fill('input[name="user"]', user)
        page.fill('input[name="pass"]', pwd)
        page.click('button[id="login_submit"]')
        page.wait_for_load_state('domcontentloaded')
        page.wait_for_timeout(5000)
        
        current_url = page.url
        from urllib.parse import urlparse
        path = urlparse(current_url).path
        cpsess = path.split('/')[1]
        
        base_url = f"{urlparse(current_url).scheme}://{urlparse(current_url).netloc}"
        git_url = f"{base_url}/{cpsess}/frontend/jupiter/version_control/index.html"
        page.goto(git_url)
        page.wait_for_load_state('domcontentloaded')
        page.wait_for_timeout(5000)
        
        with open("cpanel_git.html", "w", encoding="utf-8") as f:
            f.write(page.content())
        page.screenshot(path="logs/cpanel_git_1.png")
        print("Saved logs/cpanel_git_1.png")
        
        browser.close()

if __name__ == "__main__":
    inspect()
