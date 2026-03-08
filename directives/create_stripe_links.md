# Directive: Create Stripe Links

## Goal Description

Generate Stripe payment links for a list of products dynamically via the Stripe API. This saves time from manually navigating the Stripe dashboard for each new or updated product.

## Inputs

The script expects a JSON-formatted string or file path containing an array of product objects:

```json
[
  {
    "id": "ABAAK",
    "name": "Air Barrier Adhesion Test Kit",
    "price": "$1,800.00"
  }
]
```

It also requires the `STRIPE_SECRET_KEY` to be set in the `.env` file.

## Execution Tools

The deterministic work is handled by `executions/create_stripe_links.py`.
It uses the `stripe` and `python-dotenv` python packages.

## Outputs

The script will output a JSON mapping of product IDs to their generated Stripe Payment Link URLs:

```json
{
  "ABAAK": "https://buy.stripe.com/test_...",
  "FT1KPT": "https://buy.stripe.com/test_..."
}
```

## Edge Cases

- **Missing API Key:** If `STRIPE_SECRET_KEY` is missing from `.env`, the script will fail.
- **Price Format:** The price string (e.g., "$1,800.00") is parsed into cents (180000). Commas and dollar signs are stripped. Check for valid formats.
- **Duplicate Products:** Stripe allows multiple products with the same name. Running this script multiple times will create new Products and Prices in Stripe each time. It is best to only pass the products that *need* new links.
- **API Limits:** If processing hundreds of products, the script might hit Stripe's rate limits. The current script processes sequentially to avoid bursting.
