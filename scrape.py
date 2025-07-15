import asyncio
from playwright.async_api import async_playwright
import base64
import os
from datetime import datetime

# ✅ Restore auth file from environment
print("DEBUG: ENV VAR FOUND?", os.getenv("PLAYWRIGHT_AUTH_B64") is not None)

def write_auth_file():
    b64_data = os.getenv("PLAYWRIGHT_AUTH_B64")
    if b64_data:
        os.makedirs(".auth", exist_ok=True)
        with open(".auth/playwright_auth.json", "wb") as f:
            f.write(base64.b64decode(b64_data))
        print("✅ playwright_auth.json restored from env")
    else:
        print("⚠️  PLAYWRIGHT_AUTH_B64 not set — skipping session file write")

def ensure_auth_file():
    if not os.path.exists(".auth/playwright_auth.json"):
        raise FileNotFoundError("❌ Auth file missing at .auth/playwright_auth.json")
    print("✅ playwright_auth.json found — ready to launch browser")

# 🚀 Main scraping logic
async def run_scraper():
    ensure_auth_file()
    print("🚀 Starting scraper...")

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(storage_state=".auth/playwright_auth.json")
        page = await context.new_page()

        print("🔐 Navigating to go.servicetitan.com")
        await page.goto("https://go.servicetitan.com", timeout=60000)
        await page.wait_for_timeout(3000)

        print("📊 Navigating to report page...")
        await page.goto("https://go.servicetitan.com/#/new/reports/195360261", timeout=60000)
        await page.wait_for_timeout(5000)

        # 🗓️ Click and wait for calendar popup
        print("📅 Clicking date input to open calendar")
        await page.click('input[data-cy="qa-daterange-input"]')
        await page.wait_for_timeout(1000)

        print("⌛ Checking for calendar popup...")
        calendar_found = False
        for selector in [
            'input[placeholder="__/__/____"]',
            'input.InputDateMask',
        ]:
            try:
                await page.wait_for_selector(selector, timeout=5000)
                print(f"✅ Found calendar field with: {selector}")
                calendar_found = True
                break
            except:
                print(f"❌ Selector not found: {selector}")

        if not calendar_found:
            print("❌ Still no calendar found. Aborting.")
            return

        # 🧠 Fill in today's date into both fields
        today = datetime.today().strftime("%m/%d/%Y")
        print(f"⌨️ Typing today's date: {today}")

        inputs = await page.query_selector_all('input[placeholder="__/__/____"]')
        if len(inputs) >= 2:
            await inputs[0].fill(today)
            await inputs[1].fill(today)
            await page.keyboard.press("Enter")
            print("✅ Dates entered")
        else:
            print("❌ Couldn't find two input fields for start/end date")
            return

        # ▶️ Click Run Report
        print("▶️ Clicking Run Report...")
        try:
            await page.click("button.qa-run-button")
        except Exception as e:
            print(f"❌ Failed to click Run Report: {e}")
            return

        print("⏳ Waiting 15 seconds for report to load...")
        await page.wait_for_timeout(15000)

        # 📸 Screenshot & HTML output
        print("📸 Capturing final screenshot and HTML...")
        screenshot_bytes = await page.screenshot(path="screenshot.png", full_page=True)
        screenshot_b64 = base64.b64encode(screenshot_bytes).decode("utf-8")

        print("\n--- BEGIN BASE64 SCREENSHOT (first 500 chars) ---")
        print(screenshot_b64[:500])
        print("... (truncated)\n--- END BASE64 SCREENSHOT ---\n")

        html = await page.content()
        print("✅ Report HTML captured")

        print("\n--- BEGIN HTML SNIPPET (first 3000 chars) ---")
        print(html[:3000])
        print("\n--- END HTML SNIPPET ---\n")

        print("✅ Scraper completed successfully")

# Run for local debug
if __name__ == "__main__":
    write_auth_file()
    asyncio.run(run_scraper())
