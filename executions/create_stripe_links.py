import os
import sys
import json
import re
import stripe
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Set Stripe API key
stripe.api_key = os.getenv("STRIPE_SECRET_KEY")

def parse_price(price_str):
    """
    Parses a price string like '$1,800.00' into integer cents (180000).
    """
    # Remove $ and commas
    clean_str = re.sub(r'[\$,]', '', price_str)
    try:
        # Convert to float then multiply by 100 for cents, rounded to integer
        cents = int(round(float(clean_str) * 100))
        return cents
    except ValueError:
        print(f"Error parsing price string: {price_str}", file=sys.stderr)
        return None

def create_stripe_link(product):
    """
    Creates a product, price, and payment link in Stripe for a given product dict.
    Returns the payment link URL or None if failed.
    """
    try:
        name = product.get('name')
        price_str = product.get('price')
        
        if not name or not price_str:
            print(f"Missing name or price for product: {product.get('id', 'Unknown')}", file=sys.stderr)
            return None
            
        cents = parse_price(price_str)
        if cents is None:
            return None

        # 1. Create Product
        stripe_product = stripe.Product.create(name=name)
        
        # 2. Create Price under Product
        stripe_price = stripe.Price.create(
            product=stripe_product.id,
            unit_amount=cents,
            currency='usd',
        )
        
        # 3. Create Payment Link
        payment_link = stripe.PaymentLink.create(
            line_items=[
                {
                    "price": stripe_price.id,
                    "quantity": 1,
                }
            ]
        )
        
        return payment_link.url
        
    except stripe.error.StripeError as e:
        print(f"Stripe API error for {product.get('name', 'Unknown')}: {e.user_message}", file=sys.stderr)
        return None
    except Exception as e:
        print(f"Unexpected error for {product.get('name', 'Unknown')}: {e}", file=sys.stderr)
        return None

def main():
    if not stripe.api_key:
        print("Error: STRIPE_SECRET_KEY not found in .env", file=sys.stderr)
        sys.exit(1)
        
    # Read JSON input from stdin or argument
    if len(sys.argv) > 1:
        # If passed as file path
        try:
            with open(sys.argv[1], 'r') as f:
                products = json.load(f)
        except Exception as e:
            print(f"Error reading file {sys.argv[1]}: {e}", file=sys.stderr)
            sys.exit(1)
    else:
        # Read from stdin
        try:
            input_data = sys.stdin.read()
            if not input_data.strip():
                print("Error: No input data provided. Please pipe JSON or pass file path.", file=sys.stderr)
                sys.exit(1)
            products = json.loads(input_data)
        except json.JSONDecodeError as e:
            print(f"Error parsing JSON input: {e}", file=sys.stderr)
            sys.exit(1)
            
    if not isinstance(products, list):
        print("Error: Expected a JSON array of products.", file=sys.stderr)
        sys.exit(1)
        
    results = {}
    
    for product in products:
        p_id = product.get('id')
        if not p_id:
            print(f"Warning: Product missing 'id' field, skipping. {product}", file=sys.stderr)
            continue
            
        print(f"Processing {p_id}: {product.get('name')} - {product.get('price')}...", file=sys.stderr)
        link_url = create_stripe_link(product)
        
        if link_url:
            results[p_id] = link_url
            
    # Output JSON dictionary mapping id -> URL to stdout
    print(json.dumps(results, indent=2))

if __name__ == "__main__":
    main()
