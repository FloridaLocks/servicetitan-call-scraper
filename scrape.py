import asyncio
from playwright.async_api import async_playwright
import base64
import os

# DEBUG: Check if ENV VAR exists
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

async def run_scraper():
    ensure_auth_file()
    print("🚀 Starting scraper...")

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(storage_state=".auth/playwright_auth.json")
        page = await context.new_page()

        print("🔐 Navigating to ServiceTitan...")
        await page.goto("https://go.servicetitan.com", timeout=60000)
        await page.wait_for_timeout(6000)

        print("📊 Navigating to report URL...")
        await page.goto("https://go.servicetitan.com/#/new/reports/195360261", timeout=60000)
        await page.wait_for_timeout(6000)

        print("📅 Selecting date input...")
        await page.click('input[data-cy="qa-daterange-input"]')
        await page.wait_for_timeout(1000)

        print("🔽 Scrolling to 'Last 7 Days'...")
        for _ in range(5):
            await page.keyboard.press("ArrowDown")
        await page.wait_for_timeout(500)
        await page.keyboard.press("Enter")
        await page.wait_for_timeout(500)

        print("▶️ Clicking Run Report...")
        await page.click("button.qa-run-button")

        print("⏳ Waiting for table to load...")
        await page.wait_for_selector("table tbody tr", timeout=20000)

        print("💾 Saving HTML snapshot...")
        html = await page.content()
        with open("call_log_page.html", "w", encoding="utf-8") as f:
            f.write(html)

        # Take Screenshot and export as Base64
        print("📸 Taking screenshot...")
        await page.screenshot(path="screenshot.png", full_page=True)
        with open("screenshot.png", "rb") as img_file:
            b64_img = base64.b64encode(img_file.read()).decode('utf-8')
            print("\n--- BEGIN BASE64 SCREENSHOT ---\n")
            print(b64_img)
            print("\n--- END BASE64 SCREENSHOT ---\n")

        await browser.close()
        print("✅ Scraper finished")
