# Generate Stripe Payment Links

## Goal Description

Create a reusable Stripe Payment Link for a specified product using the official Stripe API. This tool prevents having to manually navigate the Stripe Dashboard and click through the UI to generate new payment links for product variants.

## Inputs

The script requires the following parameters to be passed exactly via the command line:

1. `product_name` (String, required): The exact name of the product as it will appear on the checkout page. (Wrap in quotes if it contains spaces).
2. `price_amount` (Integer, required): The price of the product in cents ($100.00 = 10000).

## Execution Tools

`node executions/generate_stripe_link.js "Product Name" 135000`

## Outputs

The script will output a success message containing the **live** or **test** URL (e.g., `https://buy.stripe.com/test_...`) that you can directly copy into `products.js`.
It will also output the Product ID and Price ID for future reference.

## Edge Cases

- **Missing Stripe Secret Key:** The script requires `STRIPE_SECRET_KEY` in the `.env` file located in the root `AutomateIT` directory. If missing, it will throw an authentication error. Notify the user to provide their Stripe Secret Key.
- **Price Format:** The price *must* be an integer representing cents. If you pass `$1,350.00`, you must pass `135000` to the script.
- **Identical Products:** If you run the script multiple times for the same product name, Stripe will create duplicate products in the dashboard. Be sure you only run this once per SKU/Product.
