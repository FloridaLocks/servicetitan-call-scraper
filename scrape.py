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

        # Step 1: Click the date input to trigger calendar mounting
        print("📅 Clicking date input to mount calendar...")
        await page.locator('input[data-cy="qa-daterange-input"]').scroll_into_view_if_needed()
        await page.click('input[data-cy="qa-daterange-input"]')
        await page.wait_for_timeout(1000)

        # 📸 Screenshot after click
        calendar_try = await page.screenshot()
        print("\n--- AFTER CLICK SCREENSHOT ---\n")
        print(base64.b64encode(calendar_try).decode())
        print("\n--- END ---\n")

        # Step 2: Inject date strings directly into the DOM
        today = datetime.today().strftime("%m/%d/%Y")
        print(f"⌨️ Injecting today's date: {today} into Start and End date fields")

        await page.evaluate(f'''
            () => {{
                const inputs = document.querySelectorAll('input[placeholder="Start date"], input[placeholder="End date"]');
                if (inputs.length < 2) throw new Error("❌ Could not find both date inputs.");
                inputs[0].value = "{today}";
                inputs[1].value = "{today}";
                inputs[0].dispatchEvent(new Event('input', {{ bubbles: true }}));
                inputs[1].dispatchEvent(new Event('input', {{ bubbles: true }}));
            }}
        ''')
        await page.keyboard.press("Enter")
        print("✅ Dates injected successfully and Enter key pressed")

        # Step 3: Click Run Report
        print("▶️ Clicking Run Report...")
        await page.click("button.qa-run-button")

        # Step 4: Wait for report to process
        print("⏳ Waiting 15 seconds for report to load...")
        await page.wait_for_timeout(15000)

        # Step 5: Save full-page screenshot and HTML
        print("📸 Capturing screenshot and HTML...")
        screenshot_bytes = await page.screenshot(full_page=True)
        html = await page.content()

        # Base64 Screenshot (printable in Railway log)
        print("\n--- BEGIN BASE64 SCREENSHOT ---\n")
        print(base64.b64encode(screenshot_bytes).decode())
        print("\n--- END BASE64 SCREENSHOT ---\n")

        # HTML Preview Snippet
        print("\n--- BEGIN HTML PAGE ---\n")
        print(html[:5000])
        print("\n--- END HTML PAGE ---\n")

        print("✅ Done.")

# 🔁 Optional: Entrypoint for local test
if __name__ == "__main__":
    asyncio.run(run_scraper())
