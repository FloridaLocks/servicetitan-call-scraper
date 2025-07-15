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

        print("⌛ Waiting for calendar popup to appear...")
        await page.wait_for_timeout(2000)

        # Find date inputs based on their placeholder
        print("⌨️ Typing today's date into calendar fields...")
        today = datetime.today().strftime("%m/%d/%Y")
        inputs = await page.locator('input[placeholder="__/__/____"]').all()

        if len(inputs) < 2:
            raise Exception("❌ Did not find 2 input fields for date range")

        await inputs[0].fill(today)
        await inputs[1].fill(today)
        await page.keyboard.press("Enter")
        print("✅ Date fields filled")

        # Step 2: Click Run Report
        print("▶️ Clicking Run Report...")
        await page.click("button.qa-run-button")

        # Step 3: Wait for report to process
        print("⏳ Waiting 15 seconds for report to load...")
        await page.wait_for_timeout(15000)

        # Step 4: Save and print screenshot + HTML summary
        print("📸 Capturing screenshot...")
        try:
            screenshot_bytes = await page.screenshot(full_page=True)
            screenshot_b64 = base64.b64encode(screenshot_bytes).decode()
            print("\n--- BEGIN BASE64 SCREENSHOT ---")
            print(screenshot_b64[:1000] + "..." if len(screenshot_b64) > 1000 else screenshot_b64)
            print("--- END BASE64 SCREENSHOT ---\n")
        except Exception as e:
            print(f"❌ Error capturing screenshot: {e}")

        print("📄 Capturing HTML...")
        try:
            html = await page.content()
            print("\n--- BEGIN HTML PREVIEW ---")
            print(html[:3000] + "..." if len(html) > 3000 else html)
            print("--- END HTML PREVIEW ---\n")
        except Exception as e:
            print(f"❌ Error capturing HTML: {e}")
