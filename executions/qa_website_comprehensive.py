import sys
import argparse
import requests
from urllib.parse import urljoin, urlparse
from bs4 import BeautifulSoup
from playwright.sync_api import sync_playwright
import time
import os

def check_link(url):
    """Simple HEAD request to check if a link is alive."""
    try:
        response = requests.head(url, timeout=5, allow_redirects=True)
        if response.status_code == 405: # Some servers block HEAD, try GET
            response = requests.get(url, timeout=5, stream=True)
        return response.status_code < 400
    except requests.RequestException:
        return False

def check_image(url):
    """Check if image exists and is accessible"""
    try:
        response = requests.head(url, timeout=5, allow_redirects=True)
        # Check if content type is image
        content_type = response.headers.get('content-type', '')
        return response.status_code < 400 and 'image' in content_type.lower()
    except requests.RequestException:
        return False

def analyze_seo(soup, url):
    """Check basic SEO tags."""
    seo_data = {
        'url': url,
        'title': None,
        'meta_desc': None,
        'h1_count': 0
    }
    
    title_tag = soup.find('title')
    if title_tag:
        seo_data['title'] = title_tag.string

    meta_desc = soup.find('meta', attrs={'name': 'description'})
    if meta_desc:
        seo_data['meta_desc'] = meta_desc.get('content')
        
    seo_data['h1_count'] = len(soup.find_all('h1'))
    return seo_data

def run_qa(target_url, max_pages=10):
    print(f"Starting Comprehensive QA on: {target_url}")
    
    domain = urlparse(target_url).netloc
    visited = set()
    to_visit = [target_url]
    
    broken_links = []
    broken_images = []
    missing_alt_images = []
    seo_issues = []
    payment_links = []
    
    with sync_playwright() as p:
        # Launch Chromium headless
        browser = p.chromium.launch(headless=True)
        
        # We'll use two contexts for Desktop and Mobile rendering tests
        desktop_context = browser.new_context(viewport={'width': 1920, 'height': 1080})
        mobile_context = browser.new_context(**p.devices['Pixel 5'])
        
        desktop_page = desktop_context.new_page()
        mobile_page = mobile_context.new_page()
        
        count = 0
        while to_visit and count < max_pages:
            current_url = to_visit.pop(0)
            if current_url in visited:
                continue
            
            print(f"[{count+1}/{max_pages}] Checking: {current_url}")
            visited.add(current_url)
            count += 1
            
            try:
                # Load page in desktop view to get fully rendered DOM
                response = desktop_page.goto(current_url, wait_until='networkidle', timeout=15000)
                
                if not response or response.status >= 400:
                    broken_links.append((current_url, response.status if response else "Timeout/Error"))
                    continue

                html_content = desktop_page.content()
                soup = BeautifulSoup(html_content, 'html.parser')
                
                # 1. Check Links
                for a_tag in soup.find_all('a', href=True):
                    link = urljoin(current_url, a_tag['href'])
                    
                    # Track payment links (simplistic check)
                    if any(provider in link.lower() for provider in ['stripe.com', 'paypal.com', 'checkout']):
                        payment_links.append(link)

                    # Only crawl internal links and exclude PDFs
                    if urlparse(link).netloc == domain and not link.lower().endswith('.pdf'):
                        clean_link = link.split('#')[0] # Remove fragments
                        if clean_link not in visited and clean_link not in to_visit:
                            to_visit.append(clean_link)
                            
                # 2. Check Images
                for img_tag in soup.find_all('img'):
                    src = img_tag.get('src')
                    alt = img_tag.get('alt')
                    
                    if not alt:
                        missing_alt_images.append(current_url)
                        
                    if src:
                        img_url = urljoin(current_url, src)
                        if not check_image(img_url):
                            broken_images.append((current_url, img_url))
                
                # 3. Check SEO
                seo = analyze_seo(soup, current_url)
                if not seo['title']: seo_issues.append((current_url, "Missing Title"))
                if not seo['meta_desc']: seo_issues.append((current_url, "Missing Meta Description"))
                if seo['h1_count'] != 1: seo_issues.append((current_url, f"Has {seo['h1_count']} H1 tags (Should be 1)"))
                
                # 4. Check Mobile Rendering
                try:
                    mobile_page.goto(current_url, wait_until='load', timeout=10000)
                except Exception as e:
                    print(f"WARNING: Mobile rendering issue on {current_url}: {e}")
                    
                # 5. Check Content Visibility
                # Ensure the page isn't rendering blank due to a broken fade-in wrapper or empty DOM
                is_visible = desktop_page.evaluate('''() => {
                    const bodyText = document.body.innerText.trim();
                    if (!bodyText) return false;
                    
                    // Check if primary headings are actually visible to the user and not stuck at opacity 0
                    const h1s = Array.from(document.querySelectorAll('h1'));
                    if (h1s.length > 0) {
                        for (let h1 of h1s) {
                            // Find the closest parent with a fade-in or container class to check if it's trapped in a hidden state
                            let el = h1;
                            while (el && el !== document.body) {
                                const st = window.getComputedStyle(el);
                                if (st.opacity === '0' || st.display === 'none' || st.visibility === 'hidden') return false;
                                el = el.parentElement;
                            }
                        }
                    }
                    return true;
                }''')
                if not is_visible:
                    broken_links.append((current_url, "BLANK_PAGE_ERROR (Content is hidden via CSS or missing)"))
                    
            except Exception as e:
                print(f"Error processing {current_url}: {e}")
                broken_links.append((current_url, str(e)))

        browser.close()

    # Generate Report
    safe_domain = domain.replace('.', '_').replace(':', '_')
    report_file = f"qa_report_{safe_domain}.md"
    with open(report_file, 'w', encoding='utf-8') as f:
        f.write(f"# QA Report for {target_url}\n\n")
        f.write(f"Pages Crawled: {len(visited)}\n\n")
        
        f.write("## 1. Broken Links & Errors\n")
        if broken_links:
            for url, status in broken_links:
                f.write(f"- {url} (Status: {status})\n")
        else:
            f.write("No broken links found on crawled pages.\n")
            
        f.write("\n## 2. Image Issues\n")
        f.write(f"**Broken Images:** {len(broken_images)}\n")
        for page_url, img_url in set(broken_images):
             f.write(f"- On {page_url}: {img_url}\n")
        f.write(f"\n**Pages with missing alt tags:** {len(set(missing_alt_images))}\n")
        for u in set(missing_alt_images):
            f.write(f"- {u}\n")
            
        f.write("\n## 3. SEO Issues\n")
        if seo_issues:
            for url, issue in seo_issues:
                f.write(f"- {url}: {issue}\n")
        else:
            f.write("No basic SEO issues found.\n")
            
        f.write("\n## 4. Payment Links Discovered\n")
        if payment_links:
            for link in set(payment_links):
                f.write(f"- {link}\n")
        else:
            f.write("No typical payment links (Stripe, PayPal, Checkout) found.\n")
            
    print(f"\nQA Complete. Report generated at {report_file}")
    
    # Simple pass/fail logic for orchestrator
    if broken_links or broken_images:
        print("\n[FAIL] QA Check failed due to broken links or images.")
        sys.exit(1)
    else:
        print("\n[PASS] QA Check passed.")
        sys.exit(0)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Comprehensive Website QA")
    parser.add_argument("url", help="Target URL to check")
    parser.add_argument("--max-pages", type=int, default=10, help="Max pages to crawl")
    
    args = parser.parse_args()
    run_qa(args.url, args.max_pages)
