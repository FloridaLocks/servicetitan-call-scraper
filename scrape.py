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

        from datetime import datetime

        from datetime import datetime

        # Step 1: Click the visible date input to open the calendar panel
        print("📅 Clicking main date input...")
        await page.click('input[data-cy="qa-daterange-input"]')
        await page.wait_for_selector('div[data-cy="qa-daterange-calendar"]', timeout=5000)
        await page.wait_for_timeout(1000)
        
        # Step 2: Get today's date in MM/DD/YYYY format
        today_str = datetime.today().strftime("%m/%d/%Y")
        print(f"🗓 Typing {today_str} into start and end date fields...")
        
        # Step 3: Fill the start and end date fields
        await page.fill('input[placeholder="Start date"]', today_str)
        await page.keyboard.press("Tab")
        await page.fill('input[placeholder="End date"]', today_str)
        await page.keyboard.press("Enter")
        await page.wait_for_timeout(1000)
        
        # Step 4: Click Run Report
        print("▶️ Clicking Run Report...")
        await page.click("button.qa-run-button")
        
        # Step 5: Wait 15 seconds for report to process
        print("⏳ Waiting 15 seconds for report to process...")
        await page.wait_for_timeout(15000)
        
        # Step 6: Capture screenshot and HTML
        print("📸 Capturing screenshot and HTML...")
        await page.screenshot(path="screenshot.png", full_page=True)
        html = await page.content()
        with open("call_log_page.html", "w", encoding="utf-8") as f:
            f.write(html)

        
        html = await page.content()
        with open("call_log_page.html", "w", encoding="utf-8") as f:
            f.write(html)

        print("✅ Report HTML saved")

        # 📸 Capture a screenshot and base64 encode it
        screenshot_bytes = await page.screenshot()
        screenshot_b64 = base64.b64encode(screenshot_bytes).decode()
        
        # 🧾 Print screenshot directly in log
        print("\n--- BEGIN BASE64 SCREENSHOT ---\n")
        print(screenshot_b64)
        print("\n--- END BASE64 SCREENSHOT ---\n")
