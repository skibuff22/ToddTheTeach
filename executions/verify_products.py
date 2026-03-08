import sys
import subprocess
import json
import argparse
import os
from playwright.sync_api import sync_playwright

def get_products(file_path):
    # Ensure absolute path with forward slashes for cross-platform node import
    abs_path = os.path.abspath(file_path).replace('\\', '/')
    
    js_code = f"""
    import('file://{abs_path}').then(module => {{
        console.log(JSON.stringify(module.products));
    }}).catch(err => {{
        console.error("Failed to load module:", err);
        process.exit(1);
    }});
    """
    
    result = subprocess.run(['node', '-e', js_code], capture_output=True, text=True, encoding='utf-8')
    if result.returncode != 0:
        print("[FAIL] Failed to parse products.js using Node.")
        print(result.stderr)
        sys.exit(1)
        
    try:
        # Node might print some experimental warnings to stderr, but stdout should be the pure JSON.
        return json.loads(result.stdout.strip())
    except json.JSONDecodeError as e:
        print("[FAIL] Failed to decode JSON from Node output")
        print("Raw output:", result.stdout)
        sys.exit(1)

def verify_stripe_links(products):
    print(f"Loaded {len(products)} products from source of truth.")
    
    errors = []
    
    with sync_playwright() as p:
        # Using a visible browser sometimes bypasses simple bot checks. We'll stick to headless for now unless blocked.
        browser = p.chromium.launch(headless=True)
        context = browser.new_context()
        page = context.new_page()
        
        for prod in products:
            name = prod.get('name', 'Unknown')
            price = prod.get('price', '')
            link = prod.get('stripeLink', '')
            
            if not link or 'stripe.com' not in link:
                print(f"Skipping {name}: No stripe link.")
                continue
                
            print(f"Checking Stripe Link for: {name} ({price}) -> {link}")
            
            try:
                # Go to the Stripe checkout page
                # networkidle can time out on stripe due to tracking scripts. We'll use domcontentloaded.
                page.goto(link, wait_until='domcontentloaded', timeout=15000)
                # wait a little bit for dynamic react rendering on the stripe side
                page.wait_for_timeout(2000)
                
                # Broad text search on the body content. Stripe checkout usually includes the name and price in plain text.
                content = page.locator("body").inner_text()
                
                # 1. Product Name check
                if name not in content:
                    # Softer check - all major words in name
                    words = name.split()
                    missing = [w for w in words if w not in content and len(w) > 2]
                    
                    if len(missing) > len(words) / 2:
                        errors.append(f"[{name}] Name mismatch on Stripe page. Missing terms: {missing}")
                
                # 2. Product Price check ($1,800.00 -> $1,800 or $1,800.00)
                base_price = price.replace('.00', '')
                if price not in content and base_price not in content:
                    errors.append(f"[{name}] Price mismatch. Expected '{price}' or '{base_price}', but not found in checkout text.")
                    
            except Exception as e:
                errors.append(f"[{name}] Failed to load or parse Stripe link: {e}")
                
        browser.close()
        
    if errors:
        print("\n[FAIL] Product Verification Failed with the following mismatches/errors:")
        for err in errors:
            print(f" - {err}")
        sys.exit(1)
    else:
        print("\n[PASS] Product Verification Passed. All Stripe checkout pages reflect correct product info.")
        sys.exit(0)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Verify Stripe Links match local product definitions.")
    parser.add_argument("products_file", help="Path to products.js")
    args = parser.parse_args()
    
    prods = get_products(args.products_file)
    verify_stripe_links(prods)
