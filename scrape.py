import asyncio
from playwright.async_api import async_playwright
import base64
import os
from datetime import datetime, timedelta

# Write auth file from env
def write_auth_file():
    b64 = os.getenv("PLAYWRIGHT_AUTH_B64")
    if b64:
        os.makedirs(".auth", exist_ok=True)
        with open(".auth/playwright_auth.json", "wb") as f:
            f.write(base64.b64decode(b64))
        print("✅ Auth restored")
    else:
        print("⚠️  No auth file found in env")

def ensure_auth_file():
    if not os.path.exists(".auth/playwright_auth.json"):
        raise FileNotFoundError("❌ Missing playwright_auth.json")

async def run_scraper():
    ensure_auth_file()
    print("🚀 Starting scraper...")

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(storage_state=".auth/playwright_auth.json")
        page = await context.new_page()

        print("🔐 Navigating to ServiceTitan")
        await page.goto("https://go.servicetitan.com", timeout=60000)
        await page.wait_for_timeout(5000)

        print("📊 Navigating to report page")
        await page.goto("https://go.servicetitan.com/#/new/reports/195360261", timeout=60000)
        await page.wait_for_timeout(5000)

        print("📅 Opening calendar popup...")
        await page.click('input[data-cy="qa-daterange-input"]')
        await page.wait_for_timeout(1500)

        # Screenshot to debug state
        screenshot = await page.screenshot()
        print("\n--- CALENDAR POPUP SCREENSHOT ---\n")
        print(base64.b64encode(screenshot).decode())
        print("\n--- END SCREENSHOT ---\n")

        # Find calendar fields using flexible query
        inputs = await page.query_selector_all('div.react-datepicker__tab-loop input')
        if len(inputs) < 2:
            raise Exception("❌ Could not find both calendar input fields")

        # Dates
        today = datetime.today()
        start = (today - timedelta(days=6)).strftime("%m/%d/%Y")
        end = today.strftime("%m/%d/%Y")
        print(f"⌨️ Typing date range: {start} - {end}")

        await inputs[0].fill(start)
        await page.keyboard.press("Tab")
        await inputs[1].fill(end)
        await page.keyboard.press("Enter")
        await page.wait_for_timeout(1000)

        print("▶️ Clicking Run Report...")
        await page.click("button.qa-run-button")

        print("⏳ Waiting 15s for report spinner...")
        await page.wait_for_timeout(15000)

        # Screenshot full page
        full_shot = await page.screenshot(full_page=True)
        print("\n--- FULL PAGE SCREENSHOT ---\n")
        print(base64.b64encode(full_shot).decode())
        print("\n--- END SCREENSHOT ---\n")

        # Save HTML
        html = await page.content()
        with open("call_log_page.html", "w", encoding="utf-8") as f:
            f.write(html)
        print("✅ call_log_page.html saved")
