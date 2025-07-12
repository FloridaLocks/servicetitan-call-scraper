from flask import Flask, send_file
import asyncio
import os
from playwright.async_api import async_playwright

app = Flask(__name__)

SCRAPED_FILE = "call_log_page.html"

async def run_scraper():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(storage_state=".auth/playwright_auth.json")
        page = await context.new_page()

        await page.goto("https://go.servicetitan.com", timeout=60000)
        await page.wait_for_timeout(8000)

        await page.goto("https://go.servicetitan.com/#/new/reports/195360261", timeout=60000)
        await page.wait_for_timeout(10000)

        # Interact with date selector
        await page.click('input[data-cy="qa-daterange-input"]')
        await page.wait_for_timeout(500)
        await page.keyboard.press("ArrowDown")
        await page.keyboard.press("ArrowDown")
        await page.keyboard.press("ArrowDown")
        await page.keyboard.press("ArrowDown")
        await page.keyboard.press("ArrowDown")
        await page.keyboard.press("Enter")
        await page.wait_for_timeout(500)

        await page.click('button.qa-run-button')
        await page.wait_for_selector("table tbody tr", timeout=20000)

        html = await page.content()
        with open(SCRAPED_FILE, "w", encoding="utf-8") as f:
            f.write(html)

        await browser.close()

@app.route("/")
def index():
    return "ServiceTitan scraper is running. Visit /download to view the scraped report."

@app.route("/download")
def download_file():
    if os.path.exists(SCRAPED_FILE):
        return send_file(SCRAPED_FILE)
    else:
        return "Scraped file not found", 404

# Run the scraper once on startup
asyncio.run(run_scraper())

if __name__ == "__main__":
    app.run(debug=False, host="0.0.0.0", port=8080)
