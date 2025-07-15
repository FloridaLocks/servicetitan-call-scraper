import asyncio
from playwright.async_api import async_playwright
import base64
import os
from datetime import datetime

# ✅ Write the playwright session file from env var if available
def write_auth_file():
    b64_data = os.getenv("PLAYWRIGHT_AUTH_B64")
    if b64_data:
        os.makedirs(".auth", exist_ok=True)
        with open(".auth/playwright_auth.json", "wb") as f:
            f.write(base64.b64decode(b64_data))
        print("✅ playwright_auth.json restored from env")
    else:
        print("⚠️ PLAYWRIGHT_AUTH_B64 not set — skipping session file write")

# ✅ Ensure auth file exists
def ensure_auth_file():
    if not os.path.exists(".auth/playwright_auth.json"):
        raise FileNotFoundError("❌ Missing auth file")
    print("✅ Auth file ready")

# 🚀 Main scraper logic
async def run_scraper():
    ensure_auth_file()
    print("🚀 Starting scraper...")

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(storage_state=".auth/playwright_auth.json")
        page = await context.new_page()

        print("🔐 Navigating to ServiceTitan...")
        await page.goto("https://go.servicetitan.com", timeout=60000)
        await page.wait_for_timeout(5000)

        print("📊 Navigating to report...")
        await page.goto("https://go.servicetitan.com/#/new/reports/195360261", timeout=60000)
        await page.wait_for_timeout(6000)

        # Step 1: Click on the main date range input
        print("📅 Opening calendar popup...")
        await page.locator('input[data-cy="qa-daterange-input"]').scroll_into_view_if_needed()
        await page.click('input[data-cy="qa-daterange-input"]')
        await page.wait_for_timeout(1500)

        # Step 2: Try typing directly into date fields
        today = datetime.today().strftime("%m/%d/%Y")
        print(f"⌨️ Typing today's date: {today}")
        try:
            await page.fill('inp
