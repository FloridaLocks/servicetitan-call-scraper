import asyncio
from playwright.async_api import async_playwright
import base64
import os

# Used to write session auth file from Railway ENV
def write_auth_file():
    b64_data = os.getenv("PLAYWRIGHT_AUTH_B64")
    if b64_data:
        os.makedirs(".auth", exist_ok=True)
        with open(".auth/playwright_auth.json", "wb") as f:
            f.write(base64.b64decode(b64_data))
        print("✅ playwright_auth.json restored from env")
    else:
        print("⚠️  No PLAYWRIGHT_AUTH_B64 found in environment")

async def run_scraper():
    # Debug check for environment variable
    value = os.getenv("PLAYWRIGHT_AUTH_B64")
    print("ENV VAR TEST:", value[:50] if value else "❌ MISSING")
    print("🚀 Starting scraper...")
    write_auth_file()

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(storage_state=".auth/playwright_auth.json")
        page = await context.new_page()

        print("🔐 Navigating to go.servicetitan.com")
        await page.goto("https://go.servicetitan.com", timeout=60000)
        await page.wait_for_timeout(6000)

        print("📊 Navigating to report...")
        await page.goto("https://go.servicetitan.com/#/new/reports/195360261", timeout=60000)
        await page.wait_for_timeout(6000)

        # Step 1: Select date range field
        print("📅 Selecting date range input...")
        await page.click('input[data-cy="qa-daterange-input"]')
        await page.wait_for_timeout(1000)

        # Step 2: Scroll down to "Last 7 Days" option
        print("🔽 Scrolling to Last 7 Days...")
        await page.keyboard.press("ArrowDown")
        await page.keyboard.press("ArrowDown")
        await page.keyboard.press("ArrowDown")
        await page.keyboard.press("ArrowDown")
        await page.keyboard.press("ArrowDown")
        await page.wait_for_timeout(500)

        await page.keyboard.press("Enter")
        await page.wait_for_timeout(500)

        # Step 3: Click Run Report
        print("▶️ Clicking Run Report...")
        await page.click("button.qa-run-button")

        # Step 4: Wait for table rows to appear
        print("⏳ Waiting for table to load...")
        await page.wait_for_selector("table tbody tr", timeout=20000)

        # Step 5: Save HTML content
        print("💾 Saving report HTML...")
        html = await page.content()
        with open("call_log_page.html", "w", encoding="utf-8") as f:
            f
