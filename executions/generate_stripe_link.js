import { Stripe } from 'stripe';
import * as dotenv from 'dotenv';
import path from 'path';

// For simplicity, resolve .env from the root project directory AutomateIT
dotenv.config({ path: path.resolve(process.cwd(), '../.env') });

const stripeKey = process.env.STRIPE_SECRET_KEY;

if (!stripeKey) {
    console.error("ERROR: No STRIPE_SECRET_KEY found. Ensure you have defined it in AutomateIT/.env");
    process.exit(1);
}

const stripe = new Stripe(stripeKey);

async function generateLink() {
    const args = process.argv.slice(2);

    if (args.length < 2) {
        console.log("Usage: node generate_stripe_link.js \"Product Name\" <price_in_cents>");
        console.log("Example: node generate_stripe_link.js \"Analog Pull Tester\" 95000");
        process.exit(1);
    }

    const productName = args[0];
    const priceInCents = parseInt(args[1], 10);

    if (isNaN(priceInCents)) {
        console.error("ERROR: Provided price must be an integer representing cents (e.g., 95000 for $950.00)");
        process.exit(1);
    }

    try {
        console.log(`Creating product: ${productName}...`);
        const product = await stripe.products.create({
            name: productName,
        });
        console.log(`> Product created. ID: ${product.id}`);

        console.log(`Creating price for $${(priceInCents / 100).toFixed(2)}...`);
        const price = await stripe.prices.create({
            product: product.id,
            unit_amount: priceInCents,
            currency: 'usd',
        });
        console.log(`> Price created. ID: ${price.id}`);

        console.log(`Generating Payment Link...`);
        const paymentLink = await stripe.paymentLinks.create({
            line_items: [
                {
                    price: price.id,
                    quantity: 1,
                },
            ],
            // Adds the shipping address collection widget
            shipping_address_collection: {
                allowed_countries: ['US'],
            }
        });

        console.log("\n==================================");
        console.log("SUCCESS!");
        console.log(`Payment Link: ${paymentLink.url}`);
        console.log("==================================\n");

    } catch (error) {
        console.error("Stripe API Error:", error.message);
    }
}

generateLink();
