import asyncio
from playwright.async_api import async_playwright
from datetime import datetime, timedelta

async def run_scraper():
    async with async_playwright() as p:
        print("Launching browser...")
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(storage_state=".auth/playwright_auth.json")
        page = await context.new_page()

        print("Navigating to ServiceTitan dashboard...")
        await page.goto("https://go.servicetitan.com", timeout=60000)
        await page.wait_for_timeout(6000)

        print("Navigating to saved report...")
        await page.goto("https://go.servicetitan.com/#/new/reports/195360261", timeout=60000)
        await page.wait_for_timeout(8000)

        print("Selecting 'Last 7 Days'...")
        await page.click('input[data-cy="qa-daterange-input"]')
        await page.wait_for_timeout(1000)
        await page.keyboard.press("PageDown")  # scroll down to reveal options
        await page.keyboard.press("ArrowDown")
        await page.keyboard.press("ArrowDown")
        await page.keyboard.press("ArrowDown")
        await page.keyboard.press("ArrowDown")
        await page.keyboard.press("ArrowDown")
        await page.keyboard.press("Enter")
        await page.wait_for_timeout(1000)

        print("Running the report...")
        await page.click('button.qa-run-button')
        await page.wait_for_selector("table tbody tr", timeout=20000)

        print("Saving page HTML...")
        html = await page.content()
        with open("call_log_page.html", "w", encoding="utf-8") as f:
            f.write(html)

        print("✅ Report saved. Ready to parse calls.")
        await browser.close()
