import asyncio
from playwright.async_api import async_playwright
import base64
import os
from datetime import datetime

def write_auth_file():
    b64_data = os.getenv("PLAYWRIGHT_AUTH_B64")
    if b64_data:
        os.makedirs(".auth", exist_ok=True)
        with open(".auth/playwright_auth.json", "wb") as f:
            f.write(base64.b64decode(b64_data))
        print("✅ playwright_auth.json restored from env")

def ensure_auth_file():
    if not os.path.exists(".auth/playwright_auth.json"):
        raise FileNotFoundError("❌ Auth file missing at .auth/playwright_auth.json")
    print("✅ playwright_auth.json found — ready to launch browser")

async def run_scraper():
    ensure_auth_file()
    print("🚀 Starting scraper...")

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(storage_state=".auth/playwright_auth.json")
        page = await context.new_page()

        print("🔐 Navigating to ServiceTitan...")
        await page.goto("https://go.servicetitan.com", timeout=60000)
        await page.wait_for_timeout(4000)

        print("📊 Navigating to specific report...")
        await page.goto("https://go.servicetitan.com/#/new/reports/195360261", timeout=60000)
        await page.wait_for_timeout(6000)

        # Click the date range input
        print("📅 Clicking date input...")
        await page.click('input[data-cy="qa-daterange-input"]')
        await page.wait_for_timeout(2000)

        # Set today's date
        today = datetime.today().strftime("%m/%d/%Y")
        print(f"🗓 Setting both start and end date to {today}...")

        inputs = await page.query_selector_all('input[placeholder="__/__/____"]')
        if len(inputs) >= 2:
            await inputs[0].click()
            await inputs[0].fill(today)
            await page.keyboard.press("Tab")
            await inputs[1].click()
            await inputs[1].fill(today)
            await page.keyboard.press("Enter")
            print("✅ Date range input complete")
        else:
            raise Exception("❌ Could not find both date input fields")

        print("▶️ Clicking Run Report...")
        await page.click("button.qa-run-button")
        await page.wait_for_timeout(15000)

                # Final screenshot after Run Report
        print("⏳ Waiting a bit more before capturing screenshot...")
        await page.wait_for_timeout(2000)

        screenshot_bytes = await page.screenshot(path="screenshot.png", full_page=True)
        html = await page.content()

        with open("call_log_page.html", "w", encoding="utf-8") as f:
            f.write(html)
        print("✅ Report HTML saved")

        screenshot_b64 = base64.b64encode(screenshot_bytes).decode("utf-8")
        print(f"✅ Screenshot captured ({len(screenshot_b64)} characters)")

        print("\n--- BEGIN BASE64 SCREENSHOT ---\n")
        print(screenshot_b64[:500])  # Only show first 500 chars to reduce clutter
        print("...\n--- END BASE64 SCREENSHOT ---\n")
