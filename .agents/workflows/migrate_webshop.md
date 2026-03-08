---
description: Migrate a webshop from Hostinger to GitHub, redesign it, and deploy back
---

# Migrate Webshop from Hostinger to GitHub

This workflow automates the process of migrating a webshop from Hostinger, backing up its assets to GitHub, completely redesigning it according to a strict luxury design system, and then deploying the updated version back to Hostinger.

## 1. Retrieve Existing Webshop from Hostinger

Since Hostinger may not have a public API for direct file extraction, use the `browser_subagent` to log into Hostinger and export/download the site files.

- Ask the user for Hostinger credentials and the target website domain.
- Start a `browser_subagent` to navigate to `https://hpanel.hostinger.com/`, log in, go to the File Manager of the target website, and compress/download the `public_html` folder.
- Extract the downloaded files to a local workspace directory.

## 2. Initialize GitHub Repository

- Create a new directory for the project.
- Move the extracted site assets into this directory to serve as a backup/reference.
- Initialize a Git repository (`git init`).
- Push to the user's specified GitHub repository (ask for repo URL and credentials if necessary).

## 3. Redesign and Rebuild the Website

You must apply the following design system during the rebuild. If creating a new web app, prioritize a framework like Next.js or Vite with Tailwind CSS.

### Visual & Typography System

- **Minimalist Aesthetic:** Use generous white space (padding/margins) to reduce cognitive load and allow high-quality product imagery to serve as the focal point.
- **Refined Typography:**
  - Headings (h1, h2): **Playfair Display** (conveys luxury).
  - Body text: **Inter** (ensures absolute maximum readability and a modern feel).
- **Sophisticated Palette:** Replace high-contrast or neon colors with a balanced, neutral palette (e.g., slate, stone, or muted brand colors).

### Sophisticated Visual Hierarchy

- **Emotional Resonance:** Lead with the "Why". Focus on brand recognition, luxury unboxing experiences, and environmental commitment instead of technical forms or prices.
- **Benefit-First Sections:**
  - **Hero:** Luxury/Vision
  - **Core Benefits:** Experience/Sustainability
  - **Showcase:** Proof of Quality
- **High-End Imagery:** Use lifestyle-oriented photography (generate with `generate_image` or source appropriately) that shows the product in a premium context rather than a flat stock photo.

### Optimized Conversion Path

- **Streamlined "Get Started":** Remove all disruptive pop-ups or complex initial forms.
- **Low-Friction CTAs:** Use clear, inviting calls-to-action such as "Customize Now" or "Explore Options" rather than aggressive "Buy Now" or "Add to Cart" prompts.
- **Interactive Micro-interactions:** Use Tailwind CSS for subtle hover states (e.g., `hover:scale-[1.02]` or `transition-shadow duration-300 ease-in-out`) to provide tactile feedback during the exploration phase.

### Technical & Accessibility Standards

- **A11y Audit:** Ensure all text meets WCAG 2.1 AA contrast standards. Use semantic HTML5 (e.g., `<main>`, `<section>`, `<header>`, `<footer>`) for screen reader clarity.
- **Mobile-First Fluidity:** Ensure the layout remains "calm" on mobile, avoiding cramped elements and ensuring touch targets are appropriately sized for a premium feel.

## 4. Deploy Back to Hostinger

- Build the production bundle of the completely redesigned project (`npm run build`).
- Ensure the production output (e.g., `dist` or `out` directory) is ready.
- Use `browser_subagent` to log back into the Hostinger hPanel for the target domain.
- Navigate to the File Manager, clear the old `public_html` content (preserving any essential server configuration files if applicable), and upload the newly built assets.
- Validate that the live website successfully renders the new redesign.
