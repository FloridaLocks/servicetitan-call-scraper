import asyncio
from playwright.async_api import async_playwright

async def run():
    async with async_playwright() as p:
        print("Launching browser...")
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(storage_state=".auth/playwright_auth.json")
        page = await context.new_page()

        print("Navigating to ServiceTitan dashboard...")
        await page.goto("https://go.servicetitan.com", timeout=60000)
        await page.wait_for_timeout(8000)

        print("Going to saved report...")
        await page.goto("https://go.servicetitan.com/#/new/reports/195360261", timeout=60000)
        await page.wait_for_timeout(5000)

        # Open the date range dropdown
        print("Opening date range selector...")
        await page.click('input[data-cy="qa-daterange-input"]')
        await page.wait_for_timeout(1000)

        print("Scrolling and clicking 'Last 7 Days'...")
        options = await page.locator("div[role='option']").all()
        if len(options) >= 6:
            await options[5].click()  # usually "Last 7 Days"
        else:
            print("❌ Not enough options found in date selector")

        print("Clicking Run Report...")
        await page.click("button.qa-run-button")
        await page.wait_for_timeout(10000)

        print("Saving report HTML...")
        html = await page.content()
        with open("call_log_page.html", "w", encoding="utf-8") as f:
            f.write(html)

        print("✅ Done. Report HTML saved.")

        await browser.close()

if __name__ == "__main__":
    asyncio.run(run())
