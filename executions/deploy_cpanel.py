import os
import time
from playwright.sync_api import sync_playwright
from dotenv import load_dotenv
from urllib.parse import urlparse, urljoin

def deploy_cpanel():
    load_dotenv()
    url = os.environ.get('CPANEL_URL')
    user = os.environ.get('CPANEL_USERNAME')
    pwd = os.environ.get('CPANEL_PASSWORD')

    if not all([url, user, pwd]):
        print("[FAIL] Missing cPanel credentials in .env")
        return

    print("Logging into cPanel...")
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        
        try:
            page.goto(url)
            page.fill('input[name="user"]', user)
            page.fill('input[name="pass"]', pwd)
            page.click('button[id="login_submit"]')
            page.wait_for_load_state('networkidle')
            page.wait_for_timeout(5000)
            
            # Extract cpsess
            current_url = page.url
            from urllib.parse import urlparse
            path = urlparse(current_url).path
            cpsess = path.split('/')[1]
            
            print("Logged in. Navigating File Manager...")
            fm_url = f"https://p3plzcpnl508185.prod.phx3.secureserver.net:2083/{cpsess}/frontend/jupiter/filemanager/index.html?dir=/home/{user}"
            page.goto(fm_url)
            page.wait_for_load_state('networkidle')
            page.wait_for_timeout(3000)
            
            # Click repositories folder in the left tree
            page.click('div[title="repositories"]')
            page.wait_for_load_state('networkidle')
            page.wait_for_timeout(1000)

            # Click toddtheteach folder
            page.click('div[title="toddtheteach"]')
            page.wait_for_load_state('networkidle')
            page.wait_for_timeout(1000)

            print("Copying files from repositories/toddtheteach to public_html...")
            # Click Select All button
            page.click('a:has-text("Select All")')
            page.wait_for_timeout(500)
            
            # Click Copy button in the top toolbar
            page.click('button[id="btnCopy"]')
            page.wait_for_selector('input[id="copymove_dest"]')
            
            # Fill the destination path
            page.fill('input[id="copymove_dest"]', '/public_html')
            
            # Confirm copy
            page.click('button[id="btnCopyMove_Confirm"]')
            
            # Wait a few seconds for copy to complete
            page.wait_for_timeout(5000)
            
            print("[PASS] Successfully deployed ToddTheTeach via cPanel File Manager copy.")
        except Exception as e:
            print(f"[FAIL] Error during deployment: {e}")
            page.screenshot(path="deploy_error_2.png")
            print("Saved deploy_error_2.png")
        finally:
            browser.close()

if __name__ == "__main__":
    deploy_cpanel()
