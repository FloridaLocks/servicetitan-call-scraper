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

        print("📅 Clicking main date input to open calendar...")
        await page.locator('input[data-cy="qa-daterange-input"]').scroll_into_view_if_needed()
        await page.click('input[data-cy="qa-daterange-input"]')

        print("📸 Taking screenshot right after clicking date input...")
        calendar_try = await page.screenshot()
        calendar_try_b64 = base64.b64encode(calendar_try).decode()
        print("\n--- AFTER CLICK SCREENSHOT ---\n")
        print(calendar_try_b64)
        print("\n--- END ---\n")

        print("⌛ Checking for calendar popup...")
        calendar_found = False
        for selector in [
            'div[data-cy="qa-daterange-calendar"]',
            'div.react-datepicker__calendar',
            'div.react-datepicker',
            'div.MuiPopover-root',
            'div[role="dialog"]'
        ]:
            try:
                await page.wait_for_selector(selector, timeout=5000)
                print(f"✅ Found calendar using selector: {selector}")
                calendar_found = True
                break
            except:
                print(f"❌ Selector not found: {selector}")

        if not calendar_found:
            print("❌ Calendar popup still not detected after retries.")
            calendar_html = await page.content()
            print("\n--- CALENDAR HTML DEBUG (trimmed) ---\n")
            print(calendar_html[:3000])
            print("\n--- END CALENDAR HTML ---\n")
            raise Exception("❌ Calendar popup still not detected after all selector attempts.")

        # 🗓 Inject today's date using JavaScript
        today = datetime.today().strftime("%m/%d/%Y")
        print(f"⌨️ Setting Start and End date to: {today}")

        await page.evaluate("""
            (dateStr) => {
                const inputs = document.querySelectorAll('div.react-datepicker__tab-loop input');
                if (inputs.length >= 2) {
                    inputs[0].value = dateStr;
                    inputs[1].value = dateStr;
                } else {
                    throw new Error('❌ Could not find both Start and End date inputs');
                }
            }
        """, today)

        # Press Enter on second field to apply the date
        inputs = await page.query_selector_all('div.react-datepicker__tab-loop input')
        if len(inputs) >= 2:
            await inputs[1].press("Enter")
            print("✅ Enter pressed on End Date input")
            try:
                await page.wait_for_selector('div.react-datepicker__tab-loop', state='detached', timeout=5000)
                print("✅ Calendar dismissed successfully")
            except:
                print("⚠️ Calendar may still be open, clicking outside to force close")
                await page.click("header")
                await page.wait_for_timeout(1000)
        else:
            raise Exception("❌ Could not find both Start and End date inputs after JavaScript fill")

        # 🔺 Click Run Report
        print("▶️ Clicking Run Report...")
        await page.click("button.qa-run-button")

        # ⏳ Wait for report to process
        print("⌛ Waiting 15 seconds for report to load...")
        await page.wait_for_timeout(15000)

        # 📸 Capture screenshot and HTML
        print("📸 Capturing screenshot and HTML...")
        await page.screenshot(path="screenshot.png", full_page=True)
        html = await page.content()
        print("\n--- BEGIN HTML PAGE ---\n")
        print(html[:5000])
        print("\n--- END HTML PAGE ---\n")

        with open("call_log_page.html", "w", encoding="utf-8") as f:
            f.write(html)
        print("✅ Report HTML saved")

        screenshot_bytes = await page.screenshot()
        screenshot_b64 = base64.b64encode(screenshot_bytes).decode()
        print("\n--- BEGIN BASE64 SCREENSHOT ---\n")
        print(screenshot_b64)
        print("\n--- END BASE64 SCREENSHOT ---\n")
