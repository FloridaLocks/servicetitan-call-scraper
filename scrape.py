import asyncio
from playwright.async_api import async_playwright
import base64
import os
from datetime import datetime

# Ensure static directory exists
os.makedirs("static", exist_ok=True)

# ✅ Write auth file from base64 env var if present
def write_auth_file():
    b64_data = os.getenv("PLAYWRIGHT_AUTH_B64")
    if b64_data:
        os.makedirs(".auth", exist_ok=True)
        with open(".auth/playwright_auth.json", "wb") as f:
            f.write(base64.b64decode(b64_data))
        print("✅ playwright_auth.json restored from env")
    else:
        print("⚠️  PLAYWRIGHT_AUTH_B64 not set — skipping session file write")

# ✅ Ensure the .auth file exists before browser launch
def ensure_auth_file():
    if not os.path.exists(".auth/playwright_auth.json"):
        raise FileNotFoundError("❌ Auth file missing at .auth/playwright_auth.json")
    print("✅ playwright_auth.json found — ready to launch browser")

# 🚀 MAIN SCRAPER LOGIC
async def run_scraper():
    ensure_auth_file()
    print("🚀 Starting scraper...")

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(storage_state=".auth/playwright_auth.json")
        page = await context.new_page()

        print("🔐 Navigating to go.servicetitan.com")
        await page.goto("https://go.servicetitan.com", timeout=60000)
        await page.wait_for_timeout(5000)

        print("📊 Navigating to report page...")
        await page.goto("https://go.servicetitan.com/#/new/reports/195360261", timeout=60000)
        await page.wait_for_timeout(6000)

        print("📅 Clicking date input...")
        await page.locator('input[data-cy="qa-daterange-input"]').scroll_into_view_if_needed()
        await page.click('input[data-cy="qa-daterange-input"]')
        await page.wait_for_timeout(1000)

        today = datetime.today().strftime("%m/%d/%Y")
        print(f"⌨️ Typing today’s date: {today}")

        inputs = await page.query_selector_all('input[placeholder="__/__/____"]')
        if len(inputs) >= 2:
            await inputs[0].fill(today)
            await inputs[1].fill(today)
            await page.keyboard.press("Enter")
            print("✅ Dates entered")
        else:
            raise Exception("❌ Date input fields not found")

        print("▶️ Clicking Run Report...")
        await page.click("button.qa-run-button")

        print("⏳ Waiting 15s for report to load...")
        await page.wait_for_timeout(15000)

        print("📸 Capturing screenshot and HTML...")
        screenshot_bytes = await page.screenshot(path="static/latest_screenshot.png", full_page=True)
        html = await page.content()

        with open("static/latest_report.html", "w", encoding="utf-8") as f:
            f.write(html)

        print("✅ Files saved to static folder")
