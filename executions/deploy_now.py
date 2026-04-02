import os
import time
import subprocess
from playwright.sync_api import sync_playwright
from dotenv import load_dotenv

def git_push():
    print("Pushing local changes to GitHub...")
    try:
        subprocess.run(["git", "add", "-A"], check=True)
        # Allow commit to return non-zero if there are no changes
        res = subprocess.run(["git", "commit", "-m", "Auto-deploy update"], capture_output=True, text=True)
        if res.returncode == 0:
            print("Changes committed.")
        else:
            print("No new changes to commit.")
        
        subprocess.run(["git", "push", "origin", "main"], check=True)
        print("Successfully pushed to GitHub.")
        return True
    except subprocess.CalledProcessError as e:
        print(f"[FAIL] Git operation failed: {e}")
        return False

def deploy_cpanel_git():
    if not git_push():
        print("Warning: git push had an issue, but we will continue to attempt cPanel pull just in case.")

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
            
            print("Logged in. Navigating to Git Version Control UI...")
            base_url = f"{urlparse(current_url).scheme}://{urlparse(current_url).netloc}"
            git_url = f"{base_url}/{cpsess}/frontend/jupiter/version_control/index.html"
            page.goto(git_url)
            page.wait_for_load_state('domcontentloaded')
            
            # Wait for the repository table to load and click Manage
            print("Waiting for repository list and clicking Manage...")
            # Locate the row for ToddTheTeach and click the 'Manage' button in that row
            row = page.locator("tr", has_text="ToddTheTeach").first
            row.wait_for(state="visible", timeout=30000)
            # The manage button might be a span or link
            row.locator("text=Manage").click()
            
            # Now on the Manage page. Wait for it to load
            page.wait_for_load_state('domcontentloaded')
            
            print("Clicking 'Pull or Deploy' tab...")
            # Click the Pull or Deploy tab
            page.locator("text=Pull or Deploy").click()
            page.wait_for_timeout(2000) # Wait for tab animation
            
            print("Clicking 'Update from Remote'...")
            page.locator("text=Update from Remote").first.click()
            
            print("Waiting for Git Pull success message (this may take up to 60 seconds)...")
            # Usually cPanel shows a notification or alert success
            success_notification = page.locator(".alert-success, .cg-notify-message").first
            success_notification.wait_for(state="visible", timeout=60000)
            print("Pull success output:", success_notification.text_content())
            
            # Clear notifications if there's a close button to prevent overlapping during deploy
            close_btns = page.locator(".cg-notify-message .close, .alert-success .close").all()
            for btn in close_btns:
                try:
                    btn.click(timeout=1000)
                except Exception:
                    pass
                    
            page.wait_for_timeout(2000)
            
            print("Clicking 'Deploy'...")
            page.locator("text=Deploy").first.click()
            
            print("Waiting for Git Deploy success message...")
            success_notification = page.locator(".alert-success, .cg-notify-message").first
            success_notification.wait_for(state="visible", timeout=60000)
            print("Deploy success output:", success_notification.text_content())
            
            print("Extracting Active Deployment Information...")
            try:
                commit_info = page.locator("text=Active Deployment").locator("xpath=..").text_content()
                print(f"Deployment Info: {commit_info.strip()}")
            except Exception:
                try:
                    commit_info = page.locator(".commit-message, .deployment-info").first.text_content()
                    print(f"Deployment Info: {commit_info.strip()}")
                except Exception:
                    print("Could not specifically extract deployment info text, but deployment succeeded.")

            print("[PASS] Successfully pulled and deployed ToddTheTeach via cPanel UI.")
        except Exception as e:
            print(f"[FAIL] Error during deployment: {e}")
            page.screenshot(path="logs/deploy_error_git.png")
            print("Saved logs/deploy_error_git.png")
        finally:
            browser.close()

if __name__ == "__main__":
    deploy_cpanel_git()
