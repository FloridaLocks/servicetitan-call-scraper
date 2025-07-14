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

        print("📅 Clicking main date input to open calendar...")
        await page.locator('input[data-cy="qa-daterange-input"]').scroll_into_view_if_needed()
        await page.click('input[data-cy="qa-daterange-input"]')

        print("📸 Screenshot after click")
        calendar_try = await page.screenshot()
        print("\n--- AFTER CLICK SCREENSHOT ---\n")
        print(base64.b64encode(calendar_try).decode())
        print("\n--- END ---\n")

        print("⌛ Waiting for calendar popup to appear...")
        selectors = [
            'div[data-cy="qa-daterange-calendar"]',
            'div.react-datepicker__calendar',
            'div.react-datepicker',
            'div.MuiPopover-root',
        ]
        calendar_found = False
        for selector in selectors:
            try:
                await page.wait_for_selector(selector, timeout=5000)
                print(f"✅ Found calendar using: {selector}")
                calendar_found = True
                break
            except:
                print(f"❌ Failed selector: {selector}")
        if not calendar_found:
            print("❌ Calendar popup not detected")
            html_debug = await page.content()
            print(html_debug[:3000])
            raise Exception("❌ Calendar still not found")

        print("✅ Calendar loaded — capturing HTML")
        with open("calendar_popup_debug.html", "w", encoding="utf-8") as f:
            f.write(await page.content())

        # ⌨️ Fill in today's date
        today = datetime.today().strftime("%m/%d/%Y")
        print(f"⌨️ Typing: {today}")

        # More reliable selector
        inputs = await page.query_selector_all('input[placeholder="Start date"], input[placeholder="End date"]')
        if len(inputs) >= 2:
            await inputs[0].fill(today)
            await page.keyboard.press("Tab")
            await inputs[1].fill(today)
            await page.keyboard.press("Enter")
            print("✅ Dates filled")
        else:
            raise Exception("❌ Start/End inputs not found")

        print("▶️ Clicking Run Report")
        await page.click("button.qa-run-button")

        print("⏳ Waiting for report to load...")
        await page.wait_for_timeout(15000)

        # 📸 Save result
        print("📸 Capturing screenshot and HTML...")
        screenshot_bytes = await page.screenshot(full_page=True)
        print("\n--- BEGIN BASE64 SCREENSHOT ---\n")
        print(base64.b64encode(screenshot_bytes).decode())
        print("\n--- END BASE64 SCREENSHOT ---\n")

        html = await page.content()
        with open("call_log_page.html", "w", encoding="utf-8") as f:
            f.write(html)
        print("✅ Report saved")
