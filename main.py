from flask import Flask
import subprocess

app = Flask(__name__)

@app.route("/")
def index():
    return "✅ ServiceTitan Call Scraper is deployed."

@app.route("/run")
def run_scraper():
    try:
        result = subprocess.run(["python3", "scrape.py"], capture_output=True, text=True)
        return f"<pre>{result.stdout}\n{result.stderr}</pre>"
    except Exception as e:
        return f"<pre>❌ Error: {str(e)}</pre>"

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
