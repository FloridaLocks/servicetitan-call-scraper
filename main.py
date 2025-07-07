import asyncio
from playwright.async_api import async_playwright
import os

ST_USERNAME = os.getenv("ST_USERNAME")
ST_PASSWORD = os.getenv("ST_PASSWORD")

async def run():
    async with async_playwright() as p:
        print("Launching browser...")
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(storage_state=".auth/playwright_auth.json")
        page = await context.new_page()

        print("Navigating to ServiceTitan login...")
        await page.goto("https://go.servicetitan.com", timeout=60000)

        print("Waiting for dashboard to load...")
        await page.wait_for_timeout(8000)

        print("Navigating to your saved report...")
        await page.goto("https://go.servicetitan.com/#/new/reports/195360261", timeout=60000)
        await page.wait_for_timeout(10000)

        print("Saving rendered report HTML...")
        html = await page.content()
        print("\n--- FRESH START PAGE HTML ---\n")
        print(html[:3000])  # just first 3,000 characters
        print("\n--- END PAGE HTML ---\n")
        with open("call_log_page.html", "w", encoding="utf-8") as f:
            f.write(html)

        print("✅ Saved HTML — ready to inspect call rows")

        await browser.close()

# This part kicks off the script
asyncio.run(run())
