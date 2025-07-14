import asyncio
from playwright.async_api import async_playwright
import base64
import os
from datetime import datetime, timedelta

# DEBUG: Show if ENV VAR is set
print("DEBUG: ENV VAR FOUND?", os.getenv("PLAYWRIGHT_AUTH_B64") is not None)

# ✅ Write the playwright session file if env var is present
def write_auth_file():
    b64_data = os.getenv("PLAYWRIGHT_AUTH_B64")
    if b64_data:
        os.makedirs(".auth", exist_ok=True)
        with open(".auth/playwright_auth.json", "wb") as f:
            f.write(base64.b64decode(b64_data))
        print("✅ playwright_auth.json restored from env")
    else:
        print("⚠️  PLAYWRIGHT_AUTH_B64 not set — skipping session file write")

# 🔐 Make sure the session file exists before launching
def ensure_auth_file():
    if not os.path.exists(".auth/playwright_auth.json"):
        raise FileNotFoundError("❌ Auth file missing at .auth/playwright_auth.json")
    print("✅ playwright_auth.json found — ready to launch browser")

# 🧠 Main scraping logic
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

        # 🗓️ Step 1: Click the date range input
        print("📅 Clicking date input...")
        await page.click('input[data-cy="qa-daterange-input"]')
        await page.wait_for_timeout(1000)

        # Calculate dates
        today = datetime.now()
        seven_days_ago = today - timedelta(days=6)
        start_date = seven_days_ago.strftime("%m/%d/%Y")
        end_date = today.strftime("%m/%d/%Y")
        print(f"🧮 Setting date range: {start_date} – {end_date}")

        # ⌨️ Step 2: Type in the start and end dates manually
        await page.keyboard.type(start_date)
        await page.keyboard.press("Tab")
        await page.keyboard.type(end_date)
        await page.keyboard.press("Enter")
        await page.wait_for_timeout(500)

        # ▶️ Step 3: Click "Run Report"
        print("▶️ Clicking Run Report...")
        await page.click("button.qa-run-button")

        # ⏳ Step 4: Wait for report to load
        print("⏳ Waiting for table rows...")
        await page.wait_for_selector("table tbody tr", timeout=20000)

        # 💾 Save the report HTML for inspection
        html = await page.content()
        with open("call_log_page.html", "w", encoding="utf-8") as f:
            f.write(html)
        print("✅ Report HTML saved")

        # 📸 Capture a screenshot and base64 encode it
        screenshot_bytes = await page.screenshot()
        screenshot_b64 = base64.b64encode(screenshot_bytes).decode()
        with open("screenshot.b64.txt", "w") as f:
            f.write(screenshot_b64)
        print("🖼️ Screenshot saved to screenshot.b64.txt")

        await browser.close()
