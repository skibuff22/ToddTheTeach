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
            
            print("Logged in. Uploading style.css to public_html/css...")
            upload_url_css = f"https://p3plzcpnl508185.prod.phx3.secureserver.net:2083/{cpsess}/frontend/jupiter/filemanager/upload-ajax.html?file=&dir=/home/{user}/public_html/css"
            page.goto(upload_url_css)
            page.wait_for_load_state('networkidle')
            page.wait_for_timeout(3000)
            page.set_input_files('input[type="file"]', 'css/style.css')
            page.wait_for_timeout(5000)

            print("Uploading index.html to public_html...")
            upload_url_html = f"https://p3plzcpnl508185.prod.phx3.secureserver.net:2083/{cpsess}/frontend/jupiter/filemanager/upload-ajax.html?file=&dir=/home/{user}/public_html"
            page.goto(upload_url_html)
            page.wait_for_load_state('networkidle')
            page.wait_for_timeout(3000)
            page.set_input_files('input[type="file"]', 'index.html')
            page.wait_for_timeout(5000)
            
            print("[PASS] Successfully deployed ToddTheTeach via cPanel File Manager copy.")
        except Exception as e:
            print(f"[FAIL] Error during deployment: {e}")
            page.screenshot(path="logs/deploy_error_2.png")
            print("Saved logs/deploy_error_2.png")
        finally:
            browser.close()

if __name__ == "__main__":
    deploy_cpanel()
