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
    else:
        print("⚠️  PLAYWRIGHT_AUTH_B64 not set — skipping")

def ensure_auth_file():
    if not os.path.exists(".auth/playwright_auth.json"):
        raise FileNotFoundError("❌ Missing auth file")
    print("✅ Auth file ready")

async def run_scraper():
    ensure_auth_file()
    print("🚀 Starting scraper...")

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(storage_state=".auth/playwright_auth.json")
        page = await context.new_page()

        print("🔐 Navigating to ServiceTitan...")
        await page.goto("https://go.servicetitan.com", timeout=60000)
        await page.wait_for_timeout(5000)

        print("📊 Navigating to report...")
        await page.goto("https://go.servicetitan.com/#/new/reports/195360261", timeout=60000)
        await page.wait_for_timeout(6000)

        # Step 1: Open date range calendar
        print("📅 Clicking date input to open calendar...")
        await page.click('input[data-cy="qa-daterange-input"]')
        await page.wait_for_timeout(1500)

        # Step 2: Wait for calendar popup to render
        print("⌛ Waiting for calendar popup...")
        try:
            await page.wait_for_selector('div[data-cy="qa-daterange-calendar"]', timeout=10000)
            print("✅ Calendar popup visible")
        except Exception as e:
            print("❌ Calendar popup did not load")
            raise

        # Step 3: Type into visible date inputs
        today_str = datetime.today().strftime("%m/%d/%Y")
        print(f"⌨️ Typing today's date: {today_str}")
        inputs = await page.query_selector_all('div[data-cy="qa-daterange-calendar"] input')

        if len(inputs) >= 2:
            await inputs[0].fill(today_str)
            await page.keyboard.press("Tab")
            await inputs[1].fill(today_str)
            await page.keyboard.press("Enter")
            print("✅ Dates entered")
        else:
            raise Exception("❌ Could not find 2 calendar inputs")

        # Step 4: Click Run Report
        print("▶️ Clicking Run Report...")
        await page.click("button.qa-run-button")

        # Step 5: Wait and capture
        print("⏳ Waiting 15 seconds for report...")
        await page.wait_for_timeout(15000)

        print("📸 Capturing screenshot and HTML...")
        screenshot = await page.screenshot(full_page=True)
        b64 = base64.b64encode(screenshot).decode()
        print("\n--- BEGIN SCREENSHOT ---\n")
        print(b64)
        print("\n--- END SCREENSHOT ---\n")

        html = await page.content()
        with open("call_log_page.html", "w", encoding="utf-8") as f:
            f.write(html)
        print("✅ HTML saved")

