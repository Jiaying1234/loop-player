from urllib.parse import urlparse

from flask import Flask, jsonify, render_template, request


# Create the website.
app = Flask(__name__)


# Check whether the address is an acceptable TikTok URL.
def is_tiktok_url(value: str) -> bool:
    """Return whether value is an HTTPS URL hosted on tiktok.com."""
    parsed = urlparse(value.strip())
    hostname = (parsed.hostname or "").lower()
    return (
        parsed.scheme == "https"
        and hostname in {"tiktok.com", "www.tiktok.com"}
        and bool(parsed.path.strip("/"))
    )


# Show the homepage.
@app.get("/")
def index():
    return render_template("index.html")


# Check a submitted URL and return a placeholder result.
@app.post("/convert")
def convert():
    url = request.form.get("url", "")
    if not is_tiktok_url(url):
        return jsonify({"message": "URL not accepted. Try again.", "accepted": False}), 400

    return jsonify({"message": "converting to mp3", "accepted": True})


# Start the website when this file is run.
if __name__ == "__main__":
    app.run(debug=True)

#cd "C:\Users\bigch\Downloads\Rich\loop-player".\venv\Scripts\python.exe app.py
