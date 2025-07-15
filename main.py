from flask import Flask
import asyncio

print("🚀 Flask app starting...")

app = Flask(__name__)

@app.route("/")
def index():
    return "✅ App is alive"

@app.route("/run")
def run():
    return "🛠 /run not enabled in debug mode"
