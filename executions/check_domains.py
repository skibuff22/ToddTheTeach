import os
from playwright.sync_api import sync_playwright
from dotenv import load_dotenv
from urllib.parse import urlparse

def check_domains():
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
        path = urlparse(current_url).path
        cpsess = path.split('/')[1]
        base_url = f"{urlparse(current_url).scheme}://{urlparse(current_url).netloc}"
        
        # Navigate to Domains area
        domain_url = f"{base_url}/{cpsess}/frontend/jupiter/domains/index.html"
        page.goto(domain_url)
        page.wait_for_load_state('networkidle')
        page.wait_for_timeout(5000)
        
        print("DOM extraction:")
        print(page.locator("body").inner_text()[:2000])

        browser.close()

if __name__ == "__main__":
    check_domains()
