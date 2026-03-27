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
            page.wait_for_load_state('domcontentloaded')
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
            page.wait_for_load_state('domcontentloaded')
            page.wait_for_timeout(3000)
            
            print("Triggering Git Pull via UAPI...")
            pull_url = f"{base_url}/{cpsess}/execute/VersionControl/update?repository_root=/home/r1clkhqj64ol/repositories/ToddTheTeach"
            page.goto(pull_url)
            page.wait_for_load_state('domcontentloaded')
            page.wait_for_timeout(3000)
            print("Pull response:", page.locator("body").text_content())
            
            # CRITICAL: UAPI triggers a background task. We must wait for the pull to finish before deploying.
            print("Waiting 15 seconds for Git Pull background task to finish...")
            page.wait_for_timeout(15000)
            
            print("Triggering Git Deployment via UAPI...")
            deploy_url = f"{base_url}/{cpsess}/execute/VersionControlDeployment/create?repository_root=/home/r1clkhqj64ol/repositories/ToddTheTeach"
            page.goto(deploy_url)
            page.wait_for_load_state('domcontentloaded')
            page.wait_for_timeout(3000)
            print("Deploy response:", page.locator("body").text_content())
            
            print("Waiting 15 seconds for Git Deploy background task to finish...")
            page.wait_for_timeout(15000)
            
            print("[PASS] Successfully pulled and deployed ToddTheTeach via cPanel Git Version Control.")
        except Exception as e:
            print(f"[FAIL] Error during deployment: {e}")
            page.screenshot(path="deploy_error_git.png")
            print("Saved deploy_error_git.png")
        finally:
            browser.close()

if __name__ == "__main__":
    deploy_cpanel_git()
