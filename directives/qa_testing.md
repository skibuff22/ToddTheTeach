# Comprehensive Website QA Directive

## Goal Description

Perform a complete Quality Assurance (QA) check on any specified website URL. This check is design-agnostic and should ensure the website is fully functional, optimized, and visually sound across devices.

Specifically, it must:

1. Verify all internal and external links are active (no 404s).
2. Verify all images load correctly and have alt text.
3. Check SEO content (Title tags, Meta descriptions, Header hierarchy).
4. Check all payment or checkout links to ensure they are reachable.
5. Emulate mobile and desktop environments to check for basic rendering or responsive issues.

## Inputs

- `target_url`: The full URL of the website to test (e.g., `https://example.com`).

## Execution Tools

- `executions/qa_website_comprehensive.py`: The primary orchestration script.
  - This script will likely utilize `playwright` or `puppeteer` to handle the rendering, responsive checks, and network intercepts.
  - It will crawl the provided URL up to a certain depth or map.

## Outputs

- A detailed `qa_report_[domain].md` summarizing:
  - Total links checked & Broken links found.
  - Image load failures & Missing alt tags.
  - SEO analysis per page.
  - Payment link health.
  - Screenshots or logs from Mobile/Desktop layout testing.
- Terminal output with clear `[PASS]` or `[FAIL]` indicators for the Orchestrator.

## Edge Cases

- **Rate Limiting/Blocking**: Automated crawlers can be blocked by mechanisms like Cloudflare. The script should use reasonable delays or user-agent spoofing if needed, and gracefully report if it's blocked.
- **Large Websites (1000+ pages)**: Running a full QA might take hours. The script should have an optional `--max-pages` limit or limit crawling to the main sitemap to avoid infinite loops.
- **Dynamic Content/SPAs**: The execution tool MUST utilize a headless browser (not just simple HTTP requests) so that it waits for JavaScript to load before checking DOM elements (vital for React/Vite apps like `toddtheteach`).
- **Payment Link Testing**: It should *verify* the payment link goes to the expected provider (e.g., Stripe, PayPal), but it should NEVER attempt to complete a transaction.
