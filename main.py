import asyncio
from flask import Flask
from playwright.async_api import async_playwright
import os

app = Flask(__name__)

async def run():
    print("🚀 Starting Playwright automation...")
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(storage_state=".auth/playwright_auth.json")
        page = await context.new_page()

        print("🌐 Navigating to ServiceTitan dashboard...")
        await page.goto("https://go.servicetitan.com", timeout=60000)
        await page.wait_for_timeout(6000)

        print("📊 Opening saved report...")
        await page.goto("https://go.servicetitan.com/#/new/reports/195360261", timeout=60000)
        await page.wait_for_timeout(6000)

        # ⚠️ Add interaction like clicking date range & "Run Report" if needed here

        print("💾 Saving HTML content...")
        html = await page.content()
        with open("call_log_page.html", "w", encoding="utf-8") as f:
            f.write(html)

        await browser.close()
        print("✅ Done.")

@app.route("/")
def index():
    return "📡 Call logger is running!"

# 🔁 Trigger Playwright once on app startup
if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.create_task(run())  # run() starts in background
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
