import asyncio
from playwright.async_api import async_playwright
from flask import Flask, send_file
import os

STORAGE_STATE = ".auth/playwright_auth.json"
ST_USERNAME = os.getenv("ST_USERNAME")
ST_PASSWORD = os.getenv("ST_PASSWORD")

app = Flask(__name__)
screenshot_path = "report_page.png"

@app.route("/")
def home():
    return "<h1>Call Logger is running</h1><p><a href='/report_page.png'>View Screenshot</a></p>"

@app.route("/report_page.png")
def serve_screenshot():
    return send_file(screenshot_path, mimetype="image/png")

async def run_browser_task():
    async with async_playwright() as p:
        print("Launching browser...")
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(storage_state=STORAGE_STATE)
        page = await context.new_page()

        print("Navigating to dashboard...")
        await page.goto("https://go.servicetitan.com", timeout=60000)
        await page.wait_for_timeout(8000)

        print("Navigating to report...")
        await page.goto("https://go.servicetitan.com/#/new/reports/195360261", timeout=60000)
        await page.wait_for_timeout(8000)

        print("Taking screenshot...")
        await page.screenshot(path=screenshot_path)

        print("✅ Screenshot saved")
        await browser.close()

# Launch the browser task in background when Flask starts
@app.before_first_request
def start_browser_task():
    asyncio.get_event_loop().create_task(run_browser_task())

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
