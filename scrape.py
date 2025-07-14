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
        await page.click('input[data-cy="qa-daterange-input"]', force=True)

        # Screenshot right after click to verify state
        print("📸 Taking screenshot right after clicking date input...")
        calendar_try = await page.screenshot()
        calendar_try_b64 = base64.b64encode(calendar_try).decode()
        print("\n--- AFTER CLICK SCREENSHOT ---\n")
        print(calendar_try_b64)
        print("\n--- END ---\n")
        
        # Print trimmed HTML for inspection
        print("📝 Dumping full HTML after calendar click (trimmed)...")
        html_debug = await page.content()
        print("\n--- BEGIN CALENDAR HTML (trimmed to 5000 chars) ---\n")
        print(html_debug[:5000])  # only first 5000 characters to avoid flooding logs
        print("\n--- END CALENDAR HTML ---\n")

        # Try to detect calendar container with flexible selectors
        print("⌛ Waiting for calendar panel using alternative methods...")

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
            try:
                await page.get_by_text("Start date").wait_for(timeout=5000)
                print("✅ Found calendar using visible text 'Start date'")
                calendar_found = True
            except Exception as e:
                print("❌ Calendar popup not detected using ARIA or visible text")
                html_debug = await page.content()
                print("\n--- HTML DEBUG ---\n")
                print(html_debug[:3000])
                print("\n--- END HTML DEBUG ---\n")
                raise Exception("Calendar popup still not detected after all selector attempts.")

        # Save HTML for debugging
        html_debug = await page.content()
        with open("calendar_popup_debug.html", "w", encoding="utf-8") as f:
            f.write(html_debug)
        print("✅ Saved calendar popup HTML for inspection")

        # STEP 2: Type today's date into both fields
        today = datetime.today().strftime("%m/%d/%Y")
        print(f"⌨️ Typing today's date: {today} into calendar fields...")

        inputs = await page.query_selector_all('div.react-datepicker__tab-loop input')
        print(f"🔍 Found {len(inputs)} input fields")
        if len(inputs) >= 2:
            await inputs[0].fill(today)  # Start Date
            await page.keyboard.press("Tab")
            await inputs[1].fill(today)  # End Date
            await page.keyboard.press("Enter")
            print("✅ Dates entered")
        else:
            raise Exception("❌ Could not find both Start and End date inputs")

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

        # STEP 6: Print screenshot base64
        screenshot_bytes = await page.screenshot()
        screenshot_b64 = base64.b64encode(screenshot_bytes).decode()
        print("\n--- BEGIN BASE64 SCREENSHOT ---\n")
        print(screenshot_b64)
        print("\n--- END BASE64 SCREENSHOT ---\n")
