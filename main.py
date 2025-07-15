from flask import Flask, send_from_directory
import asyncio
from scrape import run_scraper
import os

app = Flask(__name__)

@app.route("/")
def home():
    return "✅ Scraper API is running."

@app.route("/run")
def trigger_scraper():
    try:
        asyncio.run(run_scraper())
        return "✅ Scraper ran successfully"
    except Exception as e:
        return f"❌ Scraper error: {e}"

@app.route("/screenshot")
def get_screenshot():
    return send_from_directory("static", "latest_screenshot.png")

@app.route("/html")
def get_html():
    return send_from_directory("static", "latest_report.html")
