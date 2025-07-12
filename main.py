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

        # Step 1: Wait for and open date selector
        print("Waiting for date range input...")
        await page.wait_for_selector('input[data-cy="qa-daterange-input"]')
        await page.click('input[data-cy="qa-daterange-input"]')
        await page.wait_for_timeout(1000)  # wait for menu to open
        
        # Step 2: Select "Last 7 Days" using keyboard navigation
        print("Selecting 'Last 7 Days' range with keyboard...")
        await page.keyboard.press("ArrowDown")  # Adjust number of presses if needed
        await page.keyboard.press("ArrowDown")
        await page.keyboard.press("ArrowDown")
        await page.keyboard.press("ArrowDown")
        await page.keyboard.press("Enter")
        await page.wait_for_timeout(1000)  # Let it update
        
        # Optional: Log what range was selected
        selected_range = await page.input_value('input[data-cy="qa-daterange-input"]')
        print(f"✅ Date range selected: {selected_range}")
        
        # Step 3: Run the report
        print("Running the report...")
        run_button = await page.wait_for_selector('button.qa-run-button', timeout=10000)
        await run_button.click()
        await page.wait_for_timeout(2000)  # Let it start loading
        
        # Step 4: Wait longer and verify data table appears
        print("Waiting for table rows to load (may take 10–20s)...")
        try:
            await page.wait_for_selector("table tbody tr", timeout=30000)
            print("✅ Table loaded!")
        except Exception:
            print("⚠️ Timeout waiting for table rows — report may not have loaded.")

        # Step 5: Save screenshot to inspect visually
        await page.screenshot(path="report_after_run.png", full_page=True)
        print("🖼️ Screenshot saved: report_after_run.png")
        import base64
        # Read and encode the screenshot
        with open("report_after_run.png", "rb") as image_file:
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
