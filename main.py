import asyncio
from playwright.async_api import async_playwright
import os

ST_USERNAME = os.getenv("ST_USERNAME")
ST_PASSWORD = os.getenv("ST_PASSWORD")

async def run():
    async with async_playwright() as p:
        print("Launching browser...")
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context()
        page = await context.new_page()

        print("Navigating to ServiceTitan login...")
        await page.goto("https://auth.servicetitan.com", timeout=60000)

        print("Filling out login form...")
        await page.fill('input[name="username"]', ST_USERNAME)
        await page.fill('input[name="password"]', ST_PASSWORD)
        await page.click('button[type="submit"]')

        print("Waiting for dashboard to load...")
        print("Waiting for dashboard to load...")
        await page.wait_for_timeout(8000)

        print("Navigating to your saved report...")
        await page.goto("https://go.servicetitan.com/#/new/reports/195360261", timeout=60000)

        # Wait for JavaScript to load the report content
        await page.wait_for_timeout(10000)

        print("Saving rendered report HTML...")
        html = await page.content()
        with open("call_log_page.html", "w", encoding="utf-8") as f:
            f.write(html)

        print("✅ Saved HTML — ready to inspect call rows")

await browser.close()


asyncio.run(run())
