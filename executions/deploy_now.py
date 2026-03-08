import os
import time
from playwright.sync_api import sync_playwright
from dotenv import load_dotenv

def deploy_cpanel_git():
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
            
            print("Logged in. Navigating to Git Version Control...")
            base_url = f"{urlparse(current_url).scheme}://{urlparse(current_url).netloc}"
            git_url = f"{base_url}/{cpsess}/frontend/jupiter/version_control/index.html"
            page.goto(git_url)
            page.wait_for_load_state('networkidle')
            page.wait_for_timeout(3000)
            
            # Find the Manage button for the toddtheteach repository and click it
            print("Navigating to repository management...")
            manage_button = page.locator('a[href*="manage.html?uid=toddtheteach"]')
            
            if manage_button.count() == 0:
                 manage_button = page.locator('a:has-text("Manage")').first
            
            manage_button.click()
            page.wait_for_load_state('networkidle')
            page.wait_for_timeout(3000)
            
            # Switch to Pull or Deploy tab
            print("Switching to Pull or Deploy tab...")
            page.click('a[href="#pull"]')
            page.wait_for_timeout(2000)
            
            # Click Update from Remote
            print("Clicking Update from Remote...")
            page.click('button[id="btnUpdateFromRemote"]')
            page.wait_for_timeout(5000) # Wait for pull to complete
            
            # Click Deploy HEAD Commit
            print("Clicking Deploy HEAD Commit...")
            page.click('button[id="btnDeployButton"]')
            page.wait_for_timeout(5000) # Wait for deploy to complete
            
            print("[PASS] Successfully pulled and deployed ToddTheTeach via cPanel Git Version Control.")
        except Exception as e:
            print(f"[FAIL] Error during deployment: {e}")
            page.screenshot(path="deploy_error_git.png")
            print("Saved deploy_error_git.png")
        finally:
            browser.close()

if __name__ == "__main__":
    deploy_cpanel_git()
