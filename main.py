import asyncio
from playwright.async_api import async_playwright
import os

ST_USERNAME = os.getenv("ST_USERNAME")
ST_PASSWORD = os.getenv("ST_PASSWORD")

async def run():
    async with async_playwright() as p:
        print("Launching browser...")
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(storage_state=".auth/playwright_auth.json")
        page = await context.new_page()

        print("Navigating to ServiceTitan login...")
        await page.goto("https://go.servicetitan.com", timeout=60000)

        print("Waiting for dashboard to load...")
        await page.wait_for_timeout(8000)

        print("Navigating to your saved report...")
        await page.goto("https://go.servicetitan.com/#/new/reports/195360261", timeout=60000)

                # Step 1: Open date selector
        print("Waiting for date range input...")
        await page.wait_for_selector('input[data-cy="qa-daterange-input"]', timeout=10000)
        await page.click('input[data-cy="qa-daterange-input"]')
        await page.wait_for_timeout(1000)  # give dropdown a moment to open

        # Step 2: Click the "Last 7 Days" shortcut
        print("Selecting 'Last 7 Days' shortcut...")
        await page.locator("text=Last 7 Days").click(force=True)
        await page.wait_for_timeout(500)

        # Step 3: Click the "Run Report" button
        print("Clicking 'Run Report'...")
        await page.click('button.qa-run-button')
        
        # Step 4: Wait for the call table to load
        print("Waiting for call table to load...")
        await page.wait_for_selector("table tbody tr", timeout=20000)

        # Step 5: Save page content for verification
        print("Saving rendered report HTML...")
        html = await page.content()
        print("\n--- FRESH START PAGE HTML ---\n")
        print(html[:3000])  # show first part for debug
        print("\n--- END PAGE HTML ---\n")
        with open("call_log_page.html", "w", encoding="utf-8") as f:
            f.write(html)

        await page.screenshot(path="report_page.png")
        print("📸 Screenshot saved as report_page.png")
        
        import base64
        # Read and encode the screenshot
        with open("report_page.png", "rb") as image_file:
            encoded = base64.b64encode(image_file.read()).decode("utf-8")
            print("\n--- BEGIN BASE64 IMAGE ---\n")
            print(encoded)
            print("\n--- END BASE64 IMAGE ---\n")


        print("Saving rendered report HTML...")
        html = await page.content()
        print("\n--- FRESH START PAGE HTML ---\n")
        print(html[:3000])  # just first 3,000 characters
        print("\n--- END PAGE HTML ---\n")
        with open("call_log_page.html", "w", encoding="utf-8") as f:
            f.write(html)

        print("✅ Saved HTML — ready to inspect call rows")

        await browser.close()

# This part kicks off the script
asyncio.run(run())
