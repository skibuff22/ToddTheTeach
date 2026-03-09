# Build and Auto-Repair Website Directive

## Goal Description

Perform a conclusive build quality assurance check, comprehensive website QA, and verify product/payment parity. If any of the steps fail, the Orchestrator MUST use its tools to fix the underlying code, and then restart the loop from the beginning until all checks `[PASS]`.

## Inputs

- `project_dir`: The directory of the frontend application (e.g., `toddtheteach/`).
- `local_url`: The URL where the dev server is running (e.g., `http://localhost:5173`).
- `live_url`: The production URL where the site is hosted (e.g., `https://toddtheteach.com`).
- `products_file`: Path to the file containing product data (e.g., `toddtheteach/src/data/products.js`).

## Execution Tools & Loop

The Orchestrator must run the following sequence. If any step fails, FIX the code and RESTART at Step 1.

1. **Build QA:**
   - Run `npm run build` in the `project_dir`.
   - EXPECTED: Exit code 0 and a successful build output.
2. **Comprehensive QA & SEO Validation:**
   - Ensure the dev server is running, then run `python executions/qa_website_comprehensive.py <local_url>`.
   - **MANDATORY**: Ensure strict SEO Optimization checks are executed. The QA script must evaluate Title tags, Meta descriptions, Viewport tags, and properly structured Header hierarchies (H1, H2) for every page.
   - EXPECTED: `[PASS]` output for all functional and SEO-related checks.
3. **Product Verification:**
   - Run `python executions/verify_products.py <products_file>`.
   - This script will parse the products file, visit each Stripe link via a headless browser, and verify that the Stripe Product Name and Price match the local data exactly.
   - EXPECTED: `[PASS]` output.
4. **Live Site Verification (Post-Deploy):**
   - After code is pushed and successfully deployed, run `python executions/qa_website_comprehensive.py <live_url>` to QA the live environment.
   - This explicitly forces a check to ensure caching hasn't blocked the updates and that SEO optimizations are correctly surfacing on the public domain.
   - EXPECTED: `[PASS]` output and a correctly generated `qa_report_[domain].md`.

## Outputs

- Success message to the user ONLY when ALL FOUR checks pass sequentially in a single loop.

## Edge Cases

- **Stripe Blocking:** If Playwright is blocked by Stripe during product verification, it will log a warning. The Orchestrator should analyze the script output—if it's a sheer anti-bot block, note it and consider it a pass if the URLs are at least correctly formatted. But prioritize actual fetching.
- **Infinite Loops:** If the Orchestrator attempts to fix the same error 3 times and it still fails, it should break the loop, output the current state, and prompt the user for manual intervention to prevent endless token usage.
