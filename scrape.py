import asyncio
from playwright.async_api import async_playwright
import base64
import os
print("DEBUG: ENV VAR FOUND?" , os.getenv("PLAYWRIGHT_AUTH_B64") is not None)

# Used to write session auth file from Railway ENV
import os

def ensure_auth_file():
    if not os.path.exists(".auth/playwright_auth.json"):
        raise FileNotFoundError("❌ Auth file missing at .auth/playwright_auth.json")
    print("✅ playwright_auth.json found — ready to launch browser")

async def run_scraper():
    ensure_auth_file()
    # Debug check for environment variable
    value = os.getenv("PLAYWRIGHT_AUTH_B64")
    print("ENV VAR TEST:", value[:50] if value else "❌ MISSING")
    print("🚀 Starting scraper...")
    ensure_auth_file()

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
