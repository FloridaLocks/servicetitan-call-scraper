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
        await page.wait_for_timeout(8000)

        print("Done — browser session completed.")
        await browser.close()

asyncio.run(run())
