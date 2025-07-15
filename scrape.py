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

        # Click to open calendar menu
        print("📅 Clicking date input to open calendar...")
        try:
            await page.locator('input[data-cy="qa-daterange-input"]').scroll_into_view_if_needed()
            await page.click('input[data-cy="qa-daterange-input"]')
            await page.wait_for_timeout(1000)
        except Exception as e:
            print(f"❌ Failed to click calendar input: {e}")

        # Screenshot immediately after clicking
        print("📸 Screenshot after clicking input...")
        screenshot_bytes = await page.screenshot()
        print("\n--- AFTER CLICK SCREENSHOT ---\n")
        print(base64.b64encode(screenshot_bytes).decode())
        print("\n--- END SCREENSHOT ---\n")

        # Wait for the date input fields to be ready
        print("⌛ Looking for masked date fields (placeholder='__/__/____')...")
        try:
            await page.wait_for_selector('input[placeholder="__/__/____"]', timeout=10000)
            date_inputs = await page.query_selector_all('input[placeholder="__/__/____"]')
        except Exception as e:
            print(f"❌ Could not find placeholder inputs: {e}")
            date_inputs = []

        if len(date_inputs) < 2:
            raise Exception("❌ Could not find both Start and End date inputs")

        today_str = datetime.today().strftime("%m/%d/%Y")
        print(f"⌨️ Typing today’s date: {today_str} into both fields...")
        await date_inputs[0].fill(today_str)
        await date_inputs[1].fill(today_str)
        await page.keyboard.press("Enter")
        print("✅ Date entry completed.")

        # Click Run Report
        print("▶️ Clicking Run Report...")
        try:
            await page.click("button.qa-run-button")
        except Exception as e:
            print(f"❌ Failed to click run report: {e}")

        # Wait for report to load
        print("⏳ Waiting 15 seconds for report to process...")
        await page.wait_for_timeout(15000)

        # Capture full HTML and screenshot
        print("📸 Final page capture...")
        html = await page.content()
        print("\n--- HTML START ---\n")
        print(html[:3000])
        print("\n--- HTML END ---\n")

        # Return base64 screenshot
        final_screenshot = await page.screenshot()
        print("\n--- FINAL SCREENSHOT BASE64 ---\n")
        print(base64.b64encode(final_screenshot).decode())
        print("\n--- END ---\n")
