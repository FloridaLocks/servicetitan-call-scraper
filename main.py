import base64
import os
import asyncio

from flask import Flask
from scrape import run_scraper  # This is your main scraping logic

# --- Step 1: Rebuild the playwright_auth.json file from an env var ---
# Expecting PLAYWRIGHT_AUTH_B64 to be set in Railway
auth_b64 = os.getenv("PLAYWRIGHT_AUTH_B64")
if auth_b64:
    os.makedirs(".auth", exist_ok=True)
    with open(".auth/playwright_auth.json", "wb") as f:
        f.write(base64.b64decode(auth_b64))
    print("✅ Session file restored to .auth/playwright_auth.json")
else:
    print("⚠️  PLAYWRIGHT_AUTH_B64 not set — skipping session file write")

# --- Step 2: Set up a basic Flask app to trigger scraping remotely ---
app = Flask(__name__)

@app.route("/")
def hello():
    return "✅ ServiceTitan scraper is deployed!"

@app.route("/run")
def run():
    try:
        asyncio.run(run_scraper())
        return "✅ Scraper ran successfully"
    except Exception as e:
        return f"❌ Scraper error: {str(e)}"

# --- Step 3: Start Flask app (used by Railway to serve traffic) ---
if __name__ == "__main__":
    app.run(debug=False, host="0.0.0.0", port=int(os.environ.get("PORT", 8080)))
from flask import Flask, send_file

@app.route("/screenshot")
def serve_screenshot():
    return send_file("latest_screenshot.png", mimetype="image/png")

@app.route("/html")
def serve_html():
    return send_file("latest_report.html", mimetype="text/html")
