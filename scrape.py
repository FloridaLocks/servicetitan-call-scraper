import asyncio
from playwright.async_api import async_playwright
import base64
import os
from datetime import datetime, timedelta

# ✅ Write auth file from environment
def write_auth_file():
    b64_data = os.getenv("PLAYWRIGHT_AUTH_B64")
    if b64_data:
        os.makedirs(".auth", exist_ok=True)
        with open(".auth/playwright_auth.json", "wb") as f:
            f.write(base64.b64decode(b64_data))
        print("✅ playwright_auth.json restored from env")
    else:
        print("⚠️ PLAYWRIGHT_AUTH_B64 not set — skipping session file write")

# ✅ Ensure auth file exists
def ensure_auth_file():
    if not os.path.exists(".auth/playwright_auth.json"):
        raise FileNotFoundError("❌ Auth file missing")
    print("✅ playwright_auth.json found — ready to launch browser")

# 🧠 Scraper logic
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

        print("📊 Navigating to report...")
        await page.goto("https://go.servicetitan.com/#/new/reports/195360261", timeout=60000)
        await page.wait_for_timeout(6000)

        # Step 1: Click date range input
        print("📅 Clicking date range input...")
        await page.click('input[data-cy="qa-daterange-input"]')
        await page.wait_for_timeout(1000)

        # Step 2: Type date range (Last 7 Days)
        today = datetime.today()
        start = (today - timedelta(days=6)).strftime("%m/%d/%Y")
        end = today.strftime("%m/%d/%Y")
        print(f"🗓 Entering dates: {start} to {end}")

        await page.fill('input[placeholder="Start date"]', start)
        await page.keyboard.press("Tab")
        await page.fill('input[placeholder="End date"]', end)
        await page.keyboard.press("Enter")
        await page.wait_for_timeout(1000)

        # Step 3: Click Run Report
        print("▶️ Clicking Run Report...")
        await page.click("button.qa-run-button")

        # Step 4: Wait for report spinner to process
        print("⏳ Waiting 15s for report to generate...")
        await page.wait_for_timeout(15000)

        # Step 5: Screenshot and HTML
        print("📸 Capturing screenshot and HTML...")
        html = await page.content()
        with open("call_log_page.html", "w", encoding="utf-8") as f:
            f.write(html)

        screenshot = await page.screenshot(full_page=True)
        screenshot_b64 = base64.b64encode(screenshot).decode()
        print("\n--- BEGIN BASE64 SCREENSHOT ---\n")
        print(screenshot_b64)
        print("\n--- END BASE64 SCREENSHOT ---\n")
