import asyncio
from playwright.async_api import async_playwright
import base64
import os
from datetime import datetime

# ✅ Log whether environment variable is present
print("DEBUG: ENV VAR FOUND?", os.getenv("PLAYWRIGHT_AUTH_B64") is not None)

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

        # Step 1: Click the visible date input to open the calendar panel
        print("📅 Clicking main date input to open calendar...")
        await page.locator('input[data-cy="qa-daterange-input"]').scroll_into_view_if_needed()
        await page.click('input[data-cy="qa-daterange-input"]')

        # Screenshot right after click to verify state
        print("📸 Taking screenshot right after clicking date input...")
        calendar_try = await page.screenshot()
        calendar_try_b64 = base64.b64encode(calendar_try).decode()
        print("\n--- AFTER CLICK SCREENSHOT ---\n")
        print(calendar_try_b64)
        print("\n--- END ---\n")

        print("⌛ Waiting for date input fields...")
        await page.wait_for_selector('div.InputDateMask input[placeholder="__/__/____"]', timeout=10000)

        date_inputs = await page.query_selector_all('div.InputDateMask input[placeholder="__/__/____"]')
        if len(date_inputs) >= 2:
            today = datetime.today().strftime("%m/%d/%Y")
            print(f"⌨️ Typing {today} into date range fields...")

            await date_inputs[0].click()
            await date_inputs[0].fill(today)
            await page.keyboard.press("Tab")
            await date_inputs[1].click()
            await date_inputs[1].fill(today)
            await page.keyboard.press("Enter")

            print("✅ Dates entered and calendar submitted")
        else:
            raise Exception("❌ Could not find both start and end date fields.")

        # STEP 3: Click Run Report
        print("▶️ Clicking Run Report...")
        await page.click("button.qa-run-button")

        # STEP 4: Wait for report to process
        print("⏳ Waiting 15 seconds for report to load...")
        await page.wait_for_timeout(15000)

        # STEP 5: Save full-page screenshot and HTML
        print("📸 Capturing screenshot and HTML...")
        await page.screenshot(path="screenshot.png", full_page=True)
        html = await page.content()
        print("\n--- BEGIN HTML PAGE ---\n")
        print(html[:5000])
        print("\n--- END HTML PAGE ---\n")

        with open("call_log_page.html", "w", encoding="utf-8") as f:
            f.write(html)
        print("✅ Report HTML saved")

        # STEP 6: Print screenshot base64 for deploy log
        screenshot_bytes = await page.screenshot()
        screenshot_b64 = base64.b64encode(screenshot_bytes).decode()
        print("\n--- BEGIN BASE64 SCREENSHOT ---\n")
        print(screenshot_b64)
        print("\n--- END BASE64 SCREENSHOT ---\n")
