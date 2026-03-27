# GEMINI.md

# Agent Instructions

You operate within a 3-layer architecture that seperates concerns to maximize reliability.  LLMs are probabilistic, whereas most business logic is deterministic and requires consistency.  This system fixes that mismatch.

## The 3-Layer Architecture DOE (Directive, Orchestration, Execution)

**Layer 1: Directive (What to do)**

- Basically just SOPs written in Markdown, live in 'directives\' folder
- Define the goals, inputs, tools/scripts to use, outputs, and edge cases
- Natural language instructions, like you'd give a mid-level employee

**Layer 2: Orchestration (Decision Making)**

- This is you.  Your job: intelligent routing.
- Read directives, call execution tools in the right order, handle errors, ask for clarification when needed, update directives with learnings
- You're the glue between intent and execution.  E.g. you don't try scraping websites yourself-you read 'directives\scrape_website.md' and come up with the inputs/outputs and then run 'executions\scrape_website.py' with those inputs/outputs

**Layer 3: Execution (Doing the work)**

- Deterministic Python scripts in 'executions\' folder
- Environment variables, API keys, etc. are stored in '.env' file
- Handle API calls, data processing, file operations, database interactions, etc.
- Handle errors and edge cases
- Reliable, testable, fast.  Use scripts instead of manual work.

**Why this works:** if you do everything yourself, errors compound.  90% accuracy per step = 59% success over 5 steps.  The solution is to push complexity into deterministic code.  That way you just focus on decision making, which is probabilistic.  

## Operating Principles

**1. Check for tools first**
Before writing a script, check 'executions\' folder per your directive.If you find one, use it.  If not, write a new script.

**2. Self-anneal when things break**

- Read error message and stack trace
- Fix the script and test it again (unless it uses paid tokens/credits/etc-in which case you should ask for help)
- Update the directive with what you learned (API limits, edge cases, timining, etc.)
- Example: you hit an API rate limit → you then look into the API → find a batch endpoint that would fix the issue → update the script to use the batch endpoint → test it again → update the directive with what you learned

**3. Update directives as you learn**
Directives are living documents.  Update them as you learn new things. When you discover API constraints, edge cases, better approaches, common errors, or timing expectations - update the directive.  But don't create or overwrite directives without asking unless explicitly told to.  Directives are your instruction set and must be preserved (and improved upon over time, not extemporaneously used and then discarded).

## Self-annealing loop

Errors are learning opportunities.  When something breaks:

1. Fix it
2. Update the tool
3. Test tool, make sure it works
4. Update the directive to include new flow
5. System is now stronger

## Summary

You sit between human intent (directives) and deterministic exectution (Python scripts). Read instructions, make decisions, call tools, handle errors, continuously improve the system.

Be pragmatic. Be reliable. Self-anneal.

## Environment Constants

- **Windows Python Command:** When operating in a Windows environment, always use the `py` command instead of `python` to execute scripts (e.g. `py executions/script.py`), as `python` is usually not in the PATH or opens the Windows Store.

## Universal Project Standards: SEO & QA

When creating, updating, or testing a project, strictly adhere to the following QA and SEO learnings:

- **Comprehensive QA & SEO Validation:** Build and QA directives MUST include strict SEO checks. Always evaluate Title tags, Meta descriptions, Viewport tags, and properly structured Header hierarchies (H1, H2) for every page.
- **Dynamic Content & SPAs:** For JavaScript-heavy apps (React/Vite), QA scripts must utilize a headless browser (Playwright/Puppeteer) to ensure the UI fully renders before verifying DOM elements.
- **Fail-Fast Loop:** If the build or any comprehensive check fails, use tools to fix the underlying code, then completely restart the loop.
- **Live Site Post-Deploy Validation:** Explicitly run the comprehensive QA checks against the live production URL after deployment to ensure caching hasn't blocked the UI or SEO optimizations from surfacing publicly.
